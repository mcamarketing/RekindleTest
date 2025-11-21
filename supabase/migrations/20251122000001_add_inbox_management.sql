-- ============================================================================
-- INBOX MANAGEMENT
-- Email account management with billing integration
-- ============================================================================

-- Create inbox_management table
CREATE TABLE IF NOT EXISTS inbox_management (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    domain_id UUID REFERENCES rex_domain_pool(id) ON DELETE SET NULL,

    -- Email Account Details
    email_address TEXT NOT NULL UNIQUE,
    display_name TEXT,

    -- Provider Configuration
    provider TEXT NOT NULL CHECK (provider IN ('sendgrid', 'gmail', 'outlook', 'custom_smtp')),
    provider_config JSONB DEFAULT '{}', -- API keys, SMTP credentials, etc

    -- Status
    status TEXT NOT NULL DEFAULT 'pending_setup' CHECK (status IN (
        'pending_setup',    -- Awaiting configuration
        'active',           -- Ready for use
        'warming',          -- In warmup period
        'paused',           -- Temporarily disabled
        'suspended',        -- Suspended due to issues
        'deleted'           -- Soft deleted
    )),

    -- Health Metrics
    emails_sent_today INTEGER DEFAULT 0,
    emails_sent_total INTEGER DEFAULT 0,
    replies_received INTEGER DEFAULT 0,
    bounce_count INTEGER DEFAULT 0,
    spam_complaint_count INTEGER DEFAULT 0,

    -- Rate Limits (per inbox)
    daily_send_limit INTEGER DEFAULT 50,
    hourly_send_limit INTEGER DEFAULT 5,

    -- Billing
    billing_tier TEXT DEFAULT 'free' CHECK (billing_tier IN ('free', 'starter', 'pro', 'enterprise')),
    purchased_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT FALSE,
    stripe_subscription_id TEXT,

    -- Assignment
    assigned_to_campaign UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    assigned_to_user UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Monitoring
    last_email_sent_at TIMESTAMPTZ,
    last_reply_received_at TIMESTAMPTZ,
    last_health_check_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_inbox_management_user_id ON inbox_management(user_id);
CREATE INDEX idx_inbox_management_domain_id ON inbox_management(domain_id) WHERE domain_id IS NOT NULL;
CREATE INDEX idx_inbox_management_status ON inbox_management(status);
CREATE INDEX idx_inbox_management_email_address ON inbox_management(email_address);
CREATE INDEX idx_inbox_management_assigned_campaign ON inbox_management(assigned_to_campaign) WHERE assigned_to_campaign IS NOT NULL;
CREATE INDEX idx_inbox_management_billing_tier ON inbox_management(billing_tier);
CREATE INDEX idx_inbox_management_expires_at ON inbox_management(expires_at) WHERE expires_at IS NOT NULL;

-- GIN index for provider_config JSON queries
CREATE INDEX idx_inbox_management_provider_config ON inbox_management USING gin(provider_config);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE inbox_management ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own inboxes
CREATE POLICY inbox_management_select_policy ON inbox_management
    FOR SELECT
    USING (user_id = auth.uid());

-- Policy: Users can insert their own inboxes
CREATE POLICY inbox_management_insert_policy ON inbox_management
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Policy: Users can update their own inboxes
CREATE POLICY inbox_management_update_policy ON inbox_management
    FOR UPDATE
    USING (user_id = auth.uid());

-- Policy: Users can soft-delete their own inboxes
CREATE POLICY inbox_management_delete_policy ON inbox_management
    FOR DELETE
    USING (user_id = auth.uid());

-- Policy: Service role has full access
CREATE POLICY inbox_management_service_policy ON inbox_management
    FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================================================
-- BILLING TIERS & LIMITS
-- ============================================================================

-- Function: Get inbox tier limits
CREATE OR REPLACE FUNCTION get_inbox_tier_limits(p_tier TEXT)
RETURNS TABLE (
    daily_send_limit INTEGER,
    hourly_send_limit INTEGER,
    price_per_month DECIMAL,
    features JSONB
) AS $$
BEGIN
    RETURN QUERY SELECT
        CASE p_tier
            WHEN 'free' THEN 50
            WHEN 'starter' THEN 500
            WHEN 'pro' THEN 2000
            WHEN 'enterprise' THEN 10000
        END as daily_send_limit,
        CASE p_tier
            WHEN 'free' THEN 5
            WHEN 'starter' THEN 50
            WHEN 'pro' THEN 200
            WHEN 'enterprise' THEN 1000
        END as hourly_send_limit,
        CASE p_tier
            WHEN 'free' THEN 0.00
            WHEN 'starter' THEN 14.99
            WHEN 'pro' THEN 99.99
            WHEN 'enterprise' THEN 399.99
        END::DECIMAL as price_per_month,
        CASE p_tier
            WHEN 'free' THEN '{"warmup": false, "analytics": false, "priority_support": false}'::JSONB
            WHEN 'starter' THEN '{"warmup": true, "analytics": true, "priority_support": false}'::JSONB
            WHEN 'pro' THEN '{"warmup": true, "analytics": true, "priority_support": true, "custom_domain": true}'::JSONB
            WHEN 'enterprise' THEN '{"warmup": true, "analytics": true, "priority_support": true, "custom_domain": true, "dedicated_ip": true, "white_label": true}'::JSONB
        END as features;
END;
$$ LANGUAGE plpgsql;

-- Function: Upgrade inbox tier
CREATE OR REPLACE FUNCTION upgrade_inbox_tier(
    p_inbox_id UUID,
    p_new_tier TEXT,
    p_stripe_subscription_id TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_limits RECORD;
BEGIN
    -- Get new tier limits
    SELECT * INTO v_limits
    FROM get_inbox_tier_limits(p_new_tier);

    -- Update inbox
    UPDATE inbox_management
    SET
        billing_tier = p_new_tier,
        daily_send_limit = v_limits.daily_send_limit,
        hourly_send_limit = v_limits.hourly_send_limit,
        stripe_subscription_id = COALESCE(p_stripe_subscription_id, stripe_subscription_id),
        purchased_at = CASE WHEN p_new_tier != 'free' THEN NOW() ELSE purchased_at END,
        expires_at = CASE
            WHEN p_new_tier != 'free' THEN NOW() + INTERVAL '30 days'
            ELSE NULL
        END,
        updated_at = NOW()
    WHERE id = p_inbox_id;

    -- Log upgrade
    INSERT INTO agent_logs (agent_name, event_type, data)
    VALUES (
        'BillingEngine',
        'custom',
        jsonb_build_object(
            'event', 'inbox_upgraded',
            'inbox_id', p_inbox_id,
            'new_tier', p_new_tier,
            'stripe_subscription_id', p_stripe_subscription_id
        )
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- INBOX ALLOCATION
-- ============================================================================

-- Function: Allocate inbox for campaign
CREATE OR REPLACE FUNCTION allocate_inbox_for_campaign(
    p_user_id UUID,
    p_campaign_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_inbox_id UUID;
BEGIN
    -- Find available inbox
    SELECT id INTO v_inbox_id
    FROM inbox_management
    WHERE
        user_id = p_user_id
        AND status = 'active'
        AND assigned_to_campaign IS NULL
        AND emails_sent_today < daily_send_limit
    ORDER BY
        -- Prefer inboxes with better health metrics
        (emails_sent_total::DECIMAL / NULLIF(bounce_count + spam_complaint_count, 0)) DESC NULLS LAST,
        last_email_sent_at ASC NULLS FIRST
    LIMIT 1;

    IF v_inbox_id IS NULL THEN
        RAISE EXCEPTION 'No available inbox for user %', p_user_id;
    END IF;

    -- Assign to campaign
    UPDATE inbox_management
    SET
        assigned_to_campaign = p_campaign_id,
        updated_at = NOW()
    WHERE id = v_inbox_id;

    RETURN v_inbox_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Release inbox from campaign
CREATE OR REPLACE FUNCTION release_inbox(p_inbox_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE inbox_management
    SET
        assigned_to_campaign = NULL,
        updated_at = NOW()
    WHERE id = p_inbox_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- HEALTH MONITORING
-- ============================================================================

-- Function: Check inbox health
CREATE OR REPLACE FUNCTION check_inbox_health(p_inbox_id UUID)
RETURNS TABLE (
    health_status TEXT,
    bounce_rate DECIMAL,
    spam_rate DECIMAL,
    reply_rate DECIMAL,
    should_pause BOOLEAN,
    pause_reason TEXT
) AS $$
DECLARE
    v_inbox inbox_management%ROWTYPE;
    v_status TEXT;
    v_should_pause BOOLEAN := FALSE;
    v_reason TEXT := NULL;
    v_bounce_rate DECIMAL;
    v_spam_rate DECIMAL;
    v_reply_rate DECIMAL;
BEGIN
    -- Get inbox data
    SELECT * INTO v_inbox
    FROM inbox_management
    WHERE id = p_inbox_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Inbox not found: %', p_inbox_id;
    END IF;

    -- Calculate rates
    v_bounce_rate := CASE
        WHEN v_inbox.emails_sent_total > 0 THEN
            v_inbox.bounce_count::DECIMAL / v_inbox.emails_sent_total
        ELSE 0
    END;

    v_spam_rate := CASE
        WHEN v_inbox.emails_sent_total > 0 THEN
            v_inbox.spam_complaint_count::DECIMAL / v_inbox.emails_sent_total
        ELSE 0
    END;

    v_reply_rate := CASE
        WHEN v_inbox.emails_sent_total > 0 THEN
            v_inbox.replies_received::DECIMAL / v_inbox.emails_sent_total
        ELSE 0
    END;

    -- Determine health status
    IF v_bounce_rate < 0.02 AND v_spam_rate < 0.001 THEN
        v_status := 'excellent';
    ELSIF v_bounce_rate < 0.05 AND v_spam_rate < 0.005 THEN
        v_status := 'good';
    ELSIF v_bounce_rate < 0.10 AND v_spam_rate < 0.01 THEN
        v_status := 'fair';
    ELSE
        v_status := 'poor';
    END IF;

    -- Check pause triggers
    IF v_bounce_rate > 0.10 THEN
        v_should_pause := TRUE;
        v_reason := 'high_bounce_rate';
    ELSIF v_spam_rate > 0.01 THEN
        v_should_pause := TRUE;
        v_reason := 'high_spam_complaints';
    ELSIF v_inbox.spam_complaint_count > 5 THEN
        v_should_pause := TRUE;
        v_reason := 'spam_complaint_threshold';
    END IF;

    -- Update last health check
    UPDATE inbox_management
    SET last_health_check_at = NOW()
    WHERE id = p_inbox_id;

    -- Auto-pause if needed
    IF v_should_pause AND v_inbox.status = 'active' THEN
        UPDATE inbox_management
        SET
            status = 'suspended',
            updated_at = NOW()
        WHERE id = p_inbox_id;

        -- Log suspension
        INSERT INTO agent_logs (agent_name, event_type, data)
        VALUES (
            'InboxHealthMonitor',
            'custom',
            jsonb_build_object(
                'event', 'inbox_suspended',
                'inbox_id', p_inbox_id,
                'reason', v_reason,
                'bounce_rate', v_bounce_rate,
                'spam_rate', v_spam_rate
            )
        );
    END IF;

    RETURN QUERY SELECT
        v_status,
        v_bounce_rate,
        v_spam_rate,
        v_reply_rate,
        v_should_pause,
        v_reason;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- AUTOMATED MAINTENANCE
-- ============================================================================

-- Function: Reset daily counters (call from cron at midnight)
CREATE OR REPLACE FUNCTION reset_inbox_daily_counters()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE inbox_management
    SET
        emails_sent_today = 0,
        updated_at = NOW()
    WHERE emails_sent_today > 0;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Check expired subscriptions
CREATE OR REPLACE FUNCTION check_expired_subscriptions()
RETURNS TABLE (
    inbox_id UUID,
    email_address TEXT,
    action_taken TEXT
) AS $$
DECLARE
    v_inbox RECORD;
BEGIN
    FOR v_inbox IN
        SELECT id, email_address, user_id
        FROM inbox_management
        WHERE
            expires_at IS NOT NULL
            AND expires_at < NOW()
            AND status != 'deleted'
            AND auto_renew = FALSE
    LOOP
        -- Downgrade to free tier
        PERFORM upgrade_inbox_tier(v_inbox.id, 'free');

        -- Pause if assigned
        UPDATE inbox_management
        SET
            status = 'paused',
            assigned_to_campaign = NULL
        WHERE id = v_inbox.id;

        RETURN QUERY SELECT
            v_inbox.id,
            v_inbox.email_address,
            'downgraded_to_free';
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Inbox pool summary
CREATE OR REPLACE VIEW inbox_pool_summary AS
SELECT
    im.id,
    im.email_address,
    im.provider,
    im.status,
    im.billing_tier,
    im.emails_sent_today,
    im.daily_send_limit,
    im.assigned_to_campaign,
    im.expires_at,
    CASE
        WHEN im.emails_sent_total > 0 THEN
            im.bounce_count::DECIMAL / im.emails_sent_total
        ELSE 0
    END as bounce_rate,
    CASE
        WHEN im.emails_sent_total > 0 THEN
            im.spam_complaint_count::DECIMAL / im.emails_sent_total
        ELSE 0
    END as spam_rate,
    CASE
        WHEN im.status = 'active'
            AND im.assigned_to_campaign IS NULL
            AND im.emails_sent_today < im.daily_send_limit THEN TRUE
        ELSE FALSE
    END as available_for_assignment
FROM inbox_management im;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_inbox_management_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER inbox_management_update_timestamp
    BEFORE UPDATE ON inbox_management
    FOR EACH ROW
    EXECUTE FUNCTION update_inbox_management_updated_at();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE inbox_management IS 'Email account management with billing and health monitoring';
COMMENT ON COLUMN inbox_management.provider_config IS 'Provider-specific configuration (API keys, SMTP credentials) - encrypted at app layer';
COMMENT ON COLUMN inbox_management.billing_tier IS 'Subscription tier (affects send limits and features)';
COMMENT ON COLUMN inbox_management.stripe_subscription_id IS 'Stripe subscription ID for billing integration';
COMMENT ON COLUMN inbox_management.auto_renew IS 'Whether subscription auto-renews on expiration';

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT ON inbox_management TO authenticated;
GRANT INSERT, UPDATE, DELETE ON inbox_management TO authenticated;
GRANT ALL ON inbox_management TO service_role;

GRANT SELECT ON inbox_pool_summary TO authenticated;
