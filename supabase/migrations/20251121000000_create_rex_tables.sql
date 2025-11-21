-- REX: Autonomous Orchestration System Database Schema
-- Priority 0: Foundation Tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- REX MISSIONS TABLE
-- ============================================================================
CREATE TABLE rex_missions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,

    -- Mission metadata
    type TEXT NOT NULL CHECK (type IN (
        'lead_reactivation',
        'campaign_execution',
        'icp_extraction',
        'domain_rotation',
        'performance_optimization',
        'error_recovery'
    )),
    state TEXT NOT NULL DEFAULT 'queued' CHECK (state IN (
        'queued',
        'assigned',
        'executing',
        'collecting',
        'analyzing',
        'optimizing',
        'completed',
        'failed',
        'escalated'
    )),
    priority INTEGER DEFAULT 50 CHECK (priority >= 0 AND priority <= 100),

    -- Context
    campaign_id UUID REFERENCES campaigns,
    lead_ids UUID[],
    custom_params JSONB DEFAULT '{}'::jsonb,

    -- Execution
    assigned_crew TEXT,
    assigned_agents TEXT[],
    allocated_resources JSONB DEFAULT '{}'::jsonb,

    -- Results
    outcome JSONB,
    metrics JSONB,
    error JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_rex_missions_user_state ON rex_missions(user_id, state);
CREATE INDEX idx_rex_missions_type ON rex_missions(type);
CREATE INDEX idx_rex_missions_priority ON rex_missions(priority DESC, created_at ASC);
CREATE INDEX idx_rex_missions_state ON rex_missions(state) WHERE state IN ('queued', 'assigned', 'executing');
CREATE INDEX idx_rex_missions_created_at ON rex_missions(created_at DESC);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_rex_missions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rex_missions_updated_at
    BEFORE UPDATE ON rex_missions
    FOR EACH ROW
    EXECUTE FUNCTION update_rex_missions_updated_at();

-- ============================================================================
-- REX TASKS TABLE (Sub-tasks of missions)
-- ============================================================================
CREATE TABLE rex_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mission_id UUID REFERENCES rex_missions ON DELETE CASCADE NOT NULL,
    agent_name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'pending' CHECK (state IN (
        'pending',
        'executing',
        'completed',
        'failed'
    )),

    -- Execution data
    input JSONB DEFAULT '{}'::jsonb,
    output JSONB,
    error JSONB,

    -- Metrics
    duration_ms INTEGER,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.00,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_rex_tasks_mission ON rex_tasks(mission_id, created_at DESC);
CREATE INDEX idx_rex_tasks_agent ON rex_tasks(agent_name);
CREATE INDEX idx_rex_tasks_state ON rex_tasks(state) WHERE state IN ('pending', 'executing');

-- ============================================================================
-- REX ANALYTICS TABLE
-- ============================================================================
CREATE TABLE rex_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Snapshot data (JSONB for flexibility)
    missions_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    agents_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    campaigns_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    domains_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Quick access metrics (denormalized for performance)
    total_missions INTEGER DEFAULT 0,
    active_missions INTEGER DEFAULT 0,
    completed_missions INTEGER DEFAULT 0,
    failed_missions INTEGER DEFAULT 0,
    avg_duration_ms INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_rex_analytics_user_time ON rex_analytics(user_id, timestamp DESC);
CREATE INDEX idx_rex_analytics_timestamp ON rex_analytics(timestamp DESC);

-- ============================================================================
-- REX DOMAIN POOL TABLE
-- ============================================================================
CREATE TABLE rex_domain_pool (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    domain TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('custom', 'prewarmed')),

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active',
        'warming',
        'rotated',
        'failed',
        'pending_verification'
    )),
    reputation_score DECIMAL(3, 2) DEFAULT 1.00 CHECK (reputation_score >= 0 AND reputation_score <= 1),

    -- Usage tracking
    emails_sent_today INTEGER DEFAULT 0,
    emails_sent_total INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    assigned_to_campaign UUID REFERENCES campaigns,

    -- Health metrics
    bounce_rate DECIMAL(5, 4) DEFAULT 0.0000,
    spam_complaint_rate DECIMAL(5, 4) DEFAULT 0.0000,
    open_rate DECIMAL(5, 4) DEFAULT 0.0000,

    -- Warmup (for prewarmed domains)
    warmup_progress DECIMAL(3, 2) DEFAULT 0.00 CHECK (warmup_progress >= 0 AND warmup_progress <= 1),
    warmup_started_at TIMESTAMPTZ,
    warmup_completed_at TIMESTAMPTZ,

    -- Rotation
    rotated_at TIMESTAMPTZ,
    rotation_reason TEXT,
    replacement_domain_id UUID REFERENCES rex_domain_pool(id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(user_id, domain)
);

-- Indexes
CREATE INDEX idx_rex_domains_user_status ON rex_domain_pool(user_id, status);
CREATE INDEX idx_rex_domains_reputation ON rex_domain_pool(reputation_score DESC);
CREATE INDEX idx_rex_domains_type ON rex_domain_pool(type, status);
CREATE INDEX idx_rex_domains_assigned ON rex_domain_pool(assigned_to_campaign) WHERE assigned_to_campaign IS NOT NULL;

-- Auto-update updated_at timestamp
CREATE TRIGGER rex_domain_pool_updated_at
    BEFORE UPDATE ON rex_domain_pool
    FOR EACH ROW
    EXECUTE FUNCTION update_rex_missions_updated_at();

-- ============================================================================
-- REX LOGS TABLE (For audit trail)
-- ============================================================================
CREATE TABLE rex_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mission_id UUID REFERENCES rex_missions,
    user_id UUID REFERENCES auth.users NOT NULL,

    -- Log data
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,

    -- Source
    source TEXT NOT NULL, -- 'rex', crew_name, agent_name

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rex_logs_mission ON rex_logs(mission_id, created_at DESC);
CREATE INDEX idx_rex_logs_user ON rex_logs(user_id, created_at DESC);
CREATE INDEX idx_rex_logs_level ON rex_logs(level, created_at DESC);
CREATE INDEX idx_rex_logs_created_at ON rex_logs(created_at DESC);

-- Partition logs by month for performance (optional, for scale)
-- This can be enabled later when log volume grows

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS
ALTER TABLE rex_missions ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_domain_pool ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_logs ENABLE ROW LEVEL SECURITY;

-- Rex Missions policies
CREATE POLICY "Users can view their own missions"
    ON rex_missions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own missions"
    ON rex_missions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own missions"
    ON rex_missions FOR UPDATE
    USING (auth.uid() = user_id);

-- Rex Tasks policies
CREATE POLICY "Users can view tasks for their missions"
    ON rex_tasks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM rex_missions
            WHERE rex_missions.id = rex_tasks.mission_id
            AND rex_missions.user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert tasks"
    ON rex_tasks FOR INSERT
    WITH CHECK (true); -- Tasks created by backend system

CREATE POLICY "System can update tasks"
    ON rex_tasks FOR UPDATE
    USING (true); -- Tasks updated by backend system

-- Rex Analytics policies
CREATE POLICY "Users can view their own analytics"
    ON rex_analytics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert analytics"
    ON rex_analytics FOR INSERT
    WITH CHECK (true);

-- Rex Domain Pool policies
CREATE POLICY "Users can view their own domains"
    ON rex_domain_pool FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own domains"
    ON rex_domain_pool FOR ALL
    USING (auth.uid() = user_id);

-- Rex Logs policies
CREATE POLICY "Users can view their own logs"
    ON rex_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert logs"
    ON rex_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate mission progress
CREATE OR REPLACE FUNCTION calculate_mission_progress(mission_id_param UUID)
RETURNS DECIMAL(3, 2) AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
BEGIN
    SELECT COUNT(*), COUNT(*) FILTER (WHERE state = 'completed')
    INTO total_tasks, completed_tasks
    FROM rex_tasks
    WHERE mission_id = mission_id_param;

    IF total_tasks = 0 THEN
        RETURN 0.00;
    END IF;

    RETURN ROUND((completed_tasks::DECIMAL / total_tasks::DECIMAL), 2);
END;
$$ LANGUAGE plpgsql;

-- Function to get active missions count
CREATE OR REPLACE FUNCTION get_active_missions_count(user_id_param UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM rex_missions
        WHERE user_id = user_id_param
        AND state IN ('queued', 'assigned', 'executing', 'collecting', 'analyzing', 'optimizing')
    );
END;
$$ LANGUAGE plpgsql;

-- Function to update domain reputation
CREATE OR REPLACE FUNCTION update_domain_reputation(
    domain_id_param UUID,
    new_bounce_rate DECIMAL,
    new_spam_rate DECIMAL,
    new_open_rate DECIMAL
)
RETURNS VOID AS $$
DECLARE
    new_reputation DECIMAL(3, 2);
BEGIN
    -- Calculate reputation score (simple weighted formula)
    -- Perfect score = 1.0, worst score = 0.0
    new_reputation := 1.0 - (
        (new_bounce_rate * 0.4) +
        (new_spam_rate * 0.5) +
        ((1.0 - new_open_rate) * 0.1)
    );

    -- Clamp between 0 and 1
    new_reputation := GREATEST(0.00, LEAST(1.00, new_reputation));

    UPDATE rex_domain_pool
    SET
        bounce_rate = new_bounce_rate,
        spam_complaint_rate = new_spam_rate,
        open_rate = new_open_rate,
        reputation_score = new_reputation
    WHERE id = domain_id_param;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active missions with progress
CREATE VIEW rex_active_missions_with_progress AS
SELECT
    m.*,
    calculate_mission_progress(m.id) as progress,
    (SELECT COUNT(*) FROM rex_tasks WHERE mission_id = m.id) as total_tasks,
    (SELECT COUNT(*) FROM rex_tasks WHERE mission_id = m.id AND state = 'completed') as completed_tasks,
    (SELECT COUNT(*) FROM rex_tasks WHERE mission_id = m.id AND state = 'failed') as failed_tasks
FROM rex_missions m
WHERE m.state IN ('queued', 'assigned', 'executing', 'collecting', 'analyzing', 'optimizing');

-- View: Domain health summary
CREATE VIEW rex_domain_health_summary AS
SELECT
    user_id,
    COUNT(*) as total_domains,
    COUNT(*) FILTER (WHERE status = 'active') as active_domains,
    COUNT(*) FILTER (WHERE status = 'warming') as warming_domains,
    COUNT(*) FILTER (WHERE status = 'rotated') as rotated_domains,
    COUNT(*) FILTER (WHERE type = 'custom') as custom_domains,
    COUNT(*) FILTER (WHERE type = 'prewarmed') as prewarmed_domains,
    AVG(reputation_score) as avg_reputation,
    MIN(reputation_score) as min_reputation,
    MAX(reputation_score) as max_reputation
FROM rex_domain_pool
GROUP BY user_id;

-- ============================================================================
-- INITIAL DATA / SEED (Optional)
-- ============================================================================

-- Insert default prewarmed domains pool (example - populate with real domains)
-- This would be managed by the domain provisioning service in production

COMMENT ON TABLE rex_missions IS 'Core table for Rex autonomous mission orchestration';
COMMENT ON TABLE rex_tasks IS 'Individual tasks executed by agents as part of missions';
COMMENT ON TABLE rex_analytics IS 'Time-series analytics snapshots for performance tracking';
COMMENT ON TABLE rex_domain_pool IS 'Domain pool management for email deliverability';
COMMENT ON TABLE rex_logs IS 'Audit trail for all Rex operations';
