-- ============================================================================
-- ENHANCED DOMAIN POOL
-- Production-grade domain management with warmup state machine
-- ============================================================================

-- Drop existing table if upgrading
-- DROP TABLE IF EXISTS rex_domain_pool CASCADE;

-- Extend existing rex_domain_pool table with warmup state machine
ALTER TABLE rex_domain_pool
    ADD COLUMN IF NOT EXISTS warmup_state TEXT DEFAULT 'cold' CHECK (warmup_state IN (
        'cold',           -- New domain, not warmed up
        'warming',        -- Actively warming up
        'warm',           -- Fully warmed, ready for production
        'cooling',        -- Temporarily paused
        'burned',         -- Reputation damaged, needs rotation
        'retired'         -- Permanently removed from pool
    )),

    ADD COLUMN IF NOT EXISTS warmup_day INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS warmup_emails_sent_today INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS warmup_target_per_day INTEGER DEFAULT 10,
    ADD COLUMN IF NOT EXISTS warmup_schedule JSONB DEFAULT '[]',

    -- Enhanced health metrics
    ADD COLUMN IF NOT EXISTS deliverability_score DECIMAL(3, 2) DEFAULT 1.00 CHECK (deliverability_score >= 0 AND deliverability_score <= 1),
    ADD COLUMN IF NOT EXISTS spam_trap_hits INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS hard_bounces INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS soft_bounces INTEGER DEFAULT 0,

    -- DNS verification
    ADD COLUMN IF NOT EXISTS dns_verified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS dns_records JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS dns_verified_at TIMESTAMPTZ,

    -- Billing & ownership
    ADD COLUMN IF NOT EXISTS billing_tier TEXT DEFAULT 'free' CHECK (billing_tier IN ('free', 'starter', 'pro', 'enterprise')),
    ADD COLUMN IF NOT EXISTS purchased_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ,

    -- Rate limiting
    ADD COLUMN IF NOT EXISTS daily_send_limit INTEGER DEFAULT 100,
    ADD COLUMN IF NOT EXISTS hourly_send_limit INTEGER DEFAULT 10,

    -- Monitoring
    ADD COLUMN IF NOT EXISTS last_health_check_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS health_check_failures INTEGER DEFAULT 0;

-- Create index on warmup_state for filtering
CREATE INDEX IF NOT EXISTS idx_domain_pool_warmup_state ON rex_domain_pool(warmup_state);
CREATE INDEX IF NOT EXISTS idx_domain_pool_dns_verified ON rex_domain_pool(dns_verified) WHERE dns_verified = TRUE;
CREATE INDEX IF NOT EXISTS idx_domain_pool_billing_tier ON rex_domain_pool(billing_tier);
CREATE INDEX IF NOT EXISTS idx_domain_pool_expires_at ON rex_domain_pool(expires_at) WHERE expires_at IS NOT NULL;

-- ============================================================================
-- WARMUP STATE MACHINE FUNCTIONS
-- ============================================================================

-- Function: Transition domain to next warmup state
CREATE OR REPLACE FUNCTION domain_warmup_transition(
    p_domain TEXT,
    p_target_state TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_state TEXT;
    v_valid_transition BOOLEAN := FALSE;
BEGIN
    -- Get current state
    SELECT warmup_state INTO v_current_state
    FROM rex_domain_pool
    WHERE domain = p_domain;

    IF v_current_state IS NULL THEN
        RAISE EXCEPTION 'Domain not found: %', p_domain;
    END IF;

    -- Validate state transition
    v_valid_transition := CASE
        -- cold -> warming (start warmup)
        WHEN v_current_state = 'cold' AND p_target_state = 'warming' THEN TRUE

        -- warming -> warm (complete warmup)
        WHEN v_current_state = 'warming' AND p_target_state = 'warm' THEN TRUE

        -- warming -> cooling (pause warmup)
        WHEN v_current_state = 'warming' AND p_target_state = 'cooling' THEN TRUE

        -- warm -> cooling (temporary pause)
        WHEN v_current_state = 'warm' AND p_target_state = 'cooling' THEN TRUE

        -- cooling -> warming (resume)
        WHEN v_current_state = 'cooling' AND p_target_state = 'warming' THEN TRUE

        -- any -> burned (reputation damage)
        WHEN p_target_state = 'burned' THEN TRUE

        -- burned -> retired (permanent removal)
        WHEN v_current_state = 'burned' AND p_target_state = 'retired' THEN TRUE

        -- warm -> retired (manual removal)
        WHEN v_current_state = 'warm' AND p_target_state = 'retired' THEN TRUE

        ELSE FALSE
    END;

    IF NOT v_valid_transition THEN
        RAISE EXCEPTION 'Invalid state transition: % -> %', v_current_state, p_target_state;
    END IF;

    -- Execute transition
    UPDATE rex_domain_pool
    SET
        warmup_state = p_target_state,
        updated_at = NOW()
    WHERE domain = p_domain;

    -- Log transition
    INSERT INTO agent_logs (agent_name, event_type, data)
    VALUES (
        'DomainWarmupEngine',
        'custom',
        jsonb_build_object(
            'event', 'state_transition',
            'domain', p_domain,
            'from_state', v_current_state,
            'to_state', p_target_state
        )
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Calculate warmup schedule (14-day warmup plan)
CREATE OR REPLACE FUNCTION calculate_warmup_schedule()
RETURNS JSONB AS $$
DECLARE
    schedule JSONB := '[]'::JSONB;
    day INTEGER;
    emails INTEGER;
BEGIN
    -- Standard 14-day warmup schedule
    FOR day IN 1..14 LOOP
        emails := CASE
            WHEN day = 1 THEN 5
            WHEN day = 2 THEN 10
            WHEN day = 3 THEN 15
            WHEN day = 4 THEN 25
            WHEN day = 5 THEN 40
            WHEN day = 6 THEN 60
            WHEN day = 7 THEN 80
            WHEN day = 8 THEN 100
            WHEN day = 9 THEN 125
            WHEN day = 10 THEN 150
            WHEN day = 11 THEN 175
            WHEN day = 12 THEN 200
            WHEN day = 13 THEN 250
            WHEN day = 14 THEN 300
        END;

        schedule := schedule || jsonb_build_object(
            'day', day,
            'target_emails', emails,
            'notes', CASE
                WHEN day <= 3 THEN 'Ramp up slowly'
                WHEN day <= 7 THEN 'Steady increase'
                WHEN day <= 10 THEN 'Accelerate'
                ELSE 'Full production'
            END
        );
    END LOOP;

    RETURN schedule;
END;
$$ LANGUAGE plpgsql;

-- Function: Start domain warmup
CREATE OR REPLACE FUNCTION start_domain_warmup(p_domain TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Transition to warming state
    PERFORM domain_warmup_transition(p_domain, 'warming');

    -- Initialize warmup schedule
    UPDATE rex_domain_pool
    SET
        warmup_started_at = NOW(),
        warmup_day = 1,
        warmup_schedule = calculate_warmup_schedule(),
        warmup_target_per_day = 5, -- Day 1 target
        warmup_emails_sent_today = 0
    WHERE domain = p_domain;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Advance warmup day
CREATE OR REPLACE FUNCTION advance_warmup_day(p_domain TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_next_day INTEGER;
    v_schedule JSONB;
    v_next_target INTEGER;
BEGIN
    -- Get current warmup state
    SELECT warmup_day + 1, warmup_schedule
    INTO v_next_day, v_schedule
    FROM rex_domain_pool
    WHERE domain = p_domain;

    -- Get target for next day
    SELECT (schedule_item->>'target_emails')::INTEGER
    INTO v_next_target
    FROM jsonb_array_elements(v_schedule) AS schedule_item
    WHERE (schedule_item->>'day')::INTEGER = v_next_day;

    -- Update domain
    UPDATE rex_domain_pool
    SET
        warmup_day = v_next_day,
        warmup_target_per_day = v_next_target,
        warmup_emails_sent_today = 0,
        updated_at = NOW()
    WHERE domain = p_domain;

    -- If day 14 reached, transition to warm
    IF v_next_day >= 14 THEN
        PERFORM domain_warmup_transition(p_domain, 'warm');

        UPDATE rex_domain_pool
        SET warmup_completed_at = NOW()
        WHERE domain = p_domain;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- HEALTH CHECK FUNCTIONS
-- ============================================================================

-- Function: Check domain health and trigger rotation if needed
CREATE OR REPLACE FUNCTION check_domain_health(p_domain TEXT)
RETURNS TABLE (
    health_status TEXT,
    reputation_score DECIMAL,
    deliverability_score DECIMAL,
    should_rotate BOOLEAN,
    rotation_reason TEXT
) AS $$
DECLARE
    v_domain rex_domain_pool%ROWTYPE;
    v_health TEXT;
    v_should_rotate BOOLEAN := FALSE;
    v_reason TEXT := NULL;
BEGIN
    -- Get domain data
    SELECT * INTO v_domain
    FROM rex_domain_pool
    WHERE domain = p_domain;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Domain not found: %', p_domain;
    END IF;

    -- Calculate health status
    IF v_domain.reputation_score >= 0.8 AND v_domain.deliverability_score >= 0.9 THEN
        v_health := 'excellent';
    ELSIF v_domain.reputation_score >= 0.7 AND v_domain.deliverability_score >= 0.8 THEN
        v_health := 'good';
    ELSIF v_domain.reputation_score >= 0.6 AND v_domain.deliverability_score >= 0.7 THEN
        v_health := 'fair';
    ELSE
        v_health := 'poor';
    END IF;

    -- Check rotation triggers
    IF v_domain.reputation_score < 0.7 THEN
        v_should_rotate := TRUE;
        v_reason := 'reputation_below_threshold';
    ELSIF v_domain.spam_complaint_rate > 0.001 THEN -- 0.1%
        v_should_rotate := TRUE;
        v_reason := 'high_spam_complaints';
    ELSIF v_domain.bounce_rate > 0.05 THEN -- 5%
        v_should_rotate := TRUE;
        v_reason := 'high_bounce_rate';
    ELSIF v_domain.spam_trap_hits > 0 THEN
        v_should_rotate := TRUE;
        v_reason := 'spam_trap_detected';
    END IF;

    -- Update last health check
    UPDATE rex_domain_pool
    SET last_health_check_at = NOW()
    WHERE domain = p_domain;

    RETURN QUERY SELECT
        v_health,
        v_domain.reputation_score,
        v_domain.deliverability_score,
        v_should_rotate,
        v_reason;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Trigger domain rotation
CREATE OR REPLACE FUNCTION trigger_domain_rotation(
    p_domain TEXT,
    p_reason TEXT
)
RETURNS UUID AS $$
DECLARE
    v_user_id UUID;
    v_campaign_id UUID;
    v_replacement_domain TEXT;
    v_mission_id UUID;
BEGIN
    -- Get current domain info
    SELECT user_id, assigned_to_campaign
    INTO v_user_id, v_campaign_id
    FROM rex_domain_pool
    WHERE domain = p_domain;

    -- Mark domain as burned
    UPDATE rex_domain_pool
    SET
        warmup_state = 'burned',
        status = 'rotated',
        rotated_at = NOW(),
        rotation_reason = p_reason
    WHERE domain = p_domain;

    -- Find replacement domain
    SELECT domain INTO v_replacement_domain
    FROM rex_domain_pool
    WHERE
        warmup_state = 'warm'
        AND status = 'active'
        AND assigned_to_campaign IS NULL
        AND (user_id = v_user_id OR type = 'prewarmed')
    ORDER BY reputation_score DESC
    LIMIT 1;

    IF v_replacement_domain IS NULL THEN
        RAISE WARNING 'No replacement domain available for %', p_domain;
        RETURN NULL;
    END IF;

    -- Assign replacement to campaign
    IF v_campaign_id IS NOT NULL THEN
        UPDATE rex_domain_pool
        SET
            assigned_to_campaign = v_campaign_id,
            user_id = v_user_id,
            last_used_at = NOW()
        WHERE domain = v_replacement_domain;
    END IF;

    -- Create rotation mission
    INSERT INTO rex_missions (
        user_id,
        type,
        state,
        priority,
        custom_params
    ) VALUES (
        v_user_id,
        'domain_rotation',
        'queued',
        90, -- High priority
        jsonb_build_object(
            'old_domain', p_domain,
            'new_domain', v_replacement_domain,
            'reason', p_reason,
            'campaign_id', v_campaign_id
        )
    ) RETURNING id INTO v_mission_id;

    RETURN v_mission_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- AUTOMATED MAINTENANCE
-- ============================================================================

-- Function: Daily domain health check (call from cron)
CREATE OR REPLACE FUNCTION daily_domain_health_check()
RETURNS TABLE (
    domain TEXT,
    health_status TEXT,
    action_taken TEXT
) AS $$
DECLARE
    v_domain RECORD;
    v_health RECORD;
BEGIN
    FOR v_domain IN
        SELECT d.domain
        FROM rex_domain_pool d
        WHERE d.status = 'active'
        AND d.warmup_state IN ('warming', 'warm')
    LOOP
        -- Check health
        SELECT * INTO v_health
        FROM check_domain_health(v_domain.domain);

        -- Take action if needed
        IF v_health.should_rotate THEN
            PERFORM trigger_domain_rotation(v_domain.domain, v_health.rotation_reason);

            RETURN QUERY SELECT
                v_domain.domain,
                v_health.health_status,
                'rotated: ' || v_health.rotation_reason;
        ELSE
            RETURN QUERY SELECT
                v_domain.domain,
                v_health.health_status,
                'healthy';
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Domain pool summary with health
CREATE OR REPLACE VIEW domain_pool_summary AS
SELECT
    d.domain,
    d.type,
    d.warmup_state,
    d.status,
    d.reputation_score,
    d.deliverability_score,
    d.bounce_rate,
    d.spam_complaint_rate,
    d.warmup_day,
    d.warmup_target_per_day,
    d.emails_sent_today,
    d.assigned_to_campaign,
    d.billing_tier,
    CASE
        WHEN d.reputation_score >= 0.8 AND d.deliverability_score >= 0.9 THEN 'excellent'
        WHEN d.reputation_score >= 0.7 AND d.deliverability_score >= 0.8 THEN 'good'
        WHEN d.reputation_score >= 0.6 AND d.deliverability_score >= 0.7 THEN 'fair'
        ELSE 'poor'
    END as health_status,
    CASE
        WHEN d.warmup_state = 'warm' AND d.status = 'active' AND d.assigned_to_campaign IS NULL THEN TRUE
        ELSE FALSE
    END as available_for_assignment
FROM rex_domain_pool d;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON COLUMN rex_domain_pool.warmup_state IS 'Warmup state machine: cold -> warming -> warm -> cooling/burned/retired';
COMMENT ON COLUMN rex_domain_pool.warmup_schedule IS 'JSON array of daily email targets for warmup period';
COMMENT ON COLUMN rex_domain_pool.deliverability_score IS 'Calculated deliverability score (0.0-1.0) based on bounces, spam complaints';
COMMENT ON COLUMN rex_domain_pool.billing_tier IS 'Subscription tier for this domain (affects send limits)';
