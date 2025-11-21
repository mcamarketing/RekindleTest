-- ============================================================================
-- AGENT LOGS TABLE
-- Comprehensive audit trail for all agent actions
-- ============================================================================

-- Create agent_logs table
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Mission & Agent Context
    mission_id UUID REFERENCES rex_missions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,

    -- Event Data
    data JSONB DEFAULT '{}',

    -- Metadata
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms INTEGER,

    -- Error tracking
    error_code TEXT,
    error_message TEXT,
    stack_trace TEXT,

    -- Correlation
    correlation_id UUID,
    parent_log_id UUID REFERENCES agent_logs(id),

    -- Indexes for common queries
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'mission_started',
        'mission_progress',
        'mission_completed',
        'mission_failed',
        'mission_error',
        'llm_call',
        'tool_execution',
        'decision_made',
        'resource_allocated',
        'domain_rotated',
        'api_call',
        'custom'
    ))
);

-- Indexes for performance
CREATE INDEX idx_agent_logs_mission_id ON agent_logs(mission_id);
CREATE INDEX idx_agent_logs_agent_name ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_event_type ON agent_logs(event_type);
CREATE INDEX idx_agent_logs_timestamp ON agent_logs(timestamp DESC);
CREATE INDEX idx_agent_logs_correlation_id ON agent_logs(correlation_id) WHERE correlation_id IS NOT NULL;

-- GIN index for JSONB queries
CREATE INDEX idx_agent_logs_data ON agent_logs USING gin(data);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view logs for their own missions
CREATE POLICY agent_logs_select_policy ON agent_logs
    FOR SELECT
    USING (
        mission_id IN (
            SELECT id FROM rex_missions WHERE user_id = auth.uid()
        )
    );

-- Policy: Service role can insert logs
CREATE POLICY agent_logs_insert_policy ON agent_logs
    FOR INSERT
    WITH CHECK (true); -- Service role only

-- Policy: No updates (logs are immutable)
CREATE POLICY agent_logs_no_update ON agent_logs
    FOR UPDATE
    USING (false);

-- Policy: No deletes (logs are immutable except cascade)
CREATE POLICY agent_logs_no_delete ON agent_logs
    FOR DELETE
    USING (false);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get agent activity summary
CREATE OR REPLACE FUNCTION get_agent_activity_summary(
    p_agent_name TEXT,
    p_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
    event_type TEXT,
    count BIGINT,
    avg_duration_ms NUMERIC,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.event_type,
        COUNT(*) as count,
        AVG(al.duration_ms)::NUMERIC as avg_duration_ms,
        (COUNT(*) FILTER (WHERE al.event_type IN ('mission_completed', 'tool_execution'))::NUMERIC /
         NULLIF(COUNT(*), 0)) as success_rate
    FROM agent_logs al
    WHERE
        al.agent_name = p_agent_name
        AND al.timestamp >= NOW() - (p_hours || ' hours')::INTERVAL
    GROUP BY al.event_type
    ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get mission log timeline
CREATE OR REPLACE FUNCTION get_mission_log_timeline(p_mission_id UUID)
RETURNS TABLE (
    id UUID,
    agent_name TEXT,
    event_type TEXT,
    timestamp TIMESTAMPTZ,
    duration_ms INTEGER,
    data JSONB,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.id,
        al.agent_name,
        al.event_type,
        al.timestamp,
        al.duration_ms,
        al.data,
        al.error_message
    FROM agent_logs al
    WHERE al.mission_id = p_mission_id
    ORDER BY al.timestamp ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Cleanup old logs (data retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_agent_logs(p_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_logs
    WHERE timestamp < NOW() - (p_days || ' days')::INTERVAL
    AND mission_id IN (
        SELECT id FROM rex_missions
        WHERE state IN ('completed', 'failed')
    );

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Agent performance metrics
CREATE OR REPLACE VIEW agent_performance_metrics AS
SELECT
    agent_name,
    COUNT(*) as total_events,
    COUNT(*) FILTER (WHERE event_type = 'mission_completed') as missions_completed,
    COUNT(*) FILTER (WHERE event_type = 'mission_failed') as missions_failed,
    COUNT(*) FILTER (WHERE event_type = 'llm_call') as llm_calls,
    AVG(duration_ms) FILTER (WHERE duration_ms IS NOT NULL) as avg_duration_ms,
    (COUNT(*) FILTER (WHERE event_type = 'mission_completed')::NUMERIC /
     NULLIF(COUNT(*) FILTER (WHERE event_type IN ('mission_completed', 'mission_failed')), 0)) * 100 as success_rate,
    MAX(timestamp) as last_activity_at
FROM agent_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY agent_name;

-- View: Error summary by agent
CREATE OR REPLACE VIEW agent_error_summary AS
SELECT
    agent_name,
    error_code,
    COUNT(*) as error_count,
    MAX(timestamp) as last_occurrence,
    array_agg(DISTINCT error_message) as error_messages
FROM agent_logs
WHERE event_type IN ('mission_failed', 'mission_error')
AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY agent_name, error_code
ORDER BY error_count DESC;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Validate log data structure
CREATE OR REPLACE FUNCTION validate_agent_log_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure critical fields exist for certain event types
    IF NEW.event_type = 'llm_call' AND NOT (NEW.data ? 'model') THEN
        RAISE EXCEPTION 'llm_call events must include model in data';
    END IF;

    IF NEW.event_type = 'mission_failed' AND NEW.error_message IS NULL THEN
        RAISE EXCEPTION 'mission_failed events must include error_message';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_agent_log_before_insert
    BEFORE INSERT ON agent_logs
    FOR EACH ROW
    EXECUTE FUNCTION validate_agent_log_data();

-- ============================================================================
-- PARTITIONING (for high-volume production deployments)
-- ============================================================================

-- Note: Uncomment below for production partitioning by month
-- This is optional but recommended for high-volume deployments

/*
-- Convert to partitioned table
ALTER TABLE agent_logs RENAME TO agent_logs_old;

CREATE TABLE agent_logs (
    LIKE agent_logs_old INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Create partitions for current and next 3 months
CREATE TABLE agent_logs_2025_11 PARTITION OF agent_logs
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE agent_logs_2025_12 PARTITION OF agent_logs
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE agent_logs_2026_01 PARTITION OF agent_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Migrate data
INSERT INTO agent_logs SELECT * FROM agent_logs_old;

-- Drop old table
DROP TABLE agent_logs_old;
*/

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE agent_logs IS 'Audit trail for all agent actions and events';
COMMENT ON COLUMN agent_logs.mission_id IS 'Reference to the mission this log belongs to';
COMMENT ON COLUMN agent_logs.agent_name IS 'Name of the agent that generated this log';
COMMENT ON COLUMN agent_logs.event_type IS 'Type of event (mission_started, mission_completed, etc)';
COMMENT ON COLUMN agent_logs.data IS 'JSON blob with event-specific data';
COMMENT ON COLUMN agent_logs.correlation_id IS 'ID for tracking related log entries across agents';
COMMENT ON COLUMN agent_logs.parent_log_id IS 'Reference to parent log for nested operations';

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant read access to authenticated users (via RLS)
GRANT SELECT ON agent_logs TO authenticated;

-- Grant full access to service role
GRANT ALL ON agent_logs TO service_role;

-- Grant access to views
GRANT SELECT ON agent_performance_metrics TO authenticated;
GRANT SELECT ON agent_error_summary TO authenticated;
