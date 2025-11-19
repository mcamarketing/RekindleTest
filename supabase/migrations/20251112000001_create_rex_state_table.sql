-- Create rex_state table for persistent REX agent state
-- This enables the "sentience layer" to maintain continuity across interactions

CREATE TABLE IF NOT EXISTS rex_state (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    state jsonb NOT NULL DEFAULT '{}',
    updated_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_rex_state_updated_at ON rex_state(updated_at);

-- RLS policies
ALTER TABLE rex_state ENABLE ROW LEVEL SECURITY;

-- Users can only access their own state
CREATE POLICY "Users can view own rex_state"
    ON rex_state FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own state
CREATE POLICY "Users can insert own rex_state"
    ON rex_state FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own state
CREATE POLICY "Users can update own rex_state"
    ON rex_state FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Service role can access all (for backend operations)
CREATE POLICY "Service role can access all rex_state"
    ON rex_state FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

COMMENT ON TABLE rex_state IS 'Persistent state storage for REX agent sentience layer';

