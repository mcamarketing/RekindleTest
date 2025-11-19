-- Create best_practices_rag table for RAG system
-- Stores successful patterns, emails, subject lines, etc. from all clients

CREATE TABLE IF NOT EXISTS best_practices_rag (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL, -- 'email', 'subject_line', 'sequence', 'timing', 'channel', etc.
    content TEXT NOT NULL, -- The actual content (email body, subject line, etc.)
    performance_metrics JSONB NOT NULL DEFAULT '{}', -- {"open_rate": 0.67, "reply_rate": 0.23, "meeting_rate": 0.15}
    context JSONB NOT NULL DEFAULT '{}', -- Lead type, industry, ACV range, etc.
    success_score FLOAT NOT NULL DEFAULT 0.0, -- Calculated from metrics
    usage_count INTEGER NOT NULL DEFAULT 0, -- How many times this has been used
    success_count INTEGER NOT NULL DEFAULT 0, -- How many times it succeeded
    tags TEXT[] DEFAULT ARRAY[]::TEXT[], -- For easier retrieval
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_best_practices_category ON best_practices_rag(category);
CREATE INDEX IF NOT EXISTS idx_best_practices_success_score ON best_practices_rag(success_score DESC);
CREATE INDEX IF NOT EXISTS idx_best_practices_tags ON best_practices_rag USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_best_practices_context ON best_practices_rag USING GIN(context);

-- RLS Policies
ALTER TABLE best_practices_rag ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (for agents)
CREATE POLICY "Service role full access" ON best_practices_rag
    FOR ALL
    USING (auth.role() = 'service_role');

-- Users can read best practices (for learning)
CREATE POLICY "Users can read best practices" ON best_practices_rag
    FOR SELECT
    USING (true);

-- Comments
COMMENT ON TABLE best_practices_rag IS 'RAG system storing best practices and successful patterns from all clients';
COMMENT ON COLUMN best_practices_rag.category IS 'Type of practice: email, subject_line, sequence, timing, channel, etc.';
COMMENT ON COLUMN best_practices_rag.content IS 'The actual content (email body, subject line, sequence structure, etc.)';
COMMENT ON COLUMN best_practices_rag.performance_metrics IS 'JSON with performance data: open_rate, reply_rate, meeting_rate, etc.';
COMMENT ON COLUMN best_practices_rag.context IS 'JSON with context about when/where it worked: industry, ACV range, company size, etc.';
COMMENT ON COLUMN best_practices_rag.success_score IS 'Calculated success score (0-1) based on performance metrics';
COMMENT ON COLUMN best_practices_rag.tags IS 'Tags for easier retrieval: industry:B2B SaaS, acv:high, etc.';






