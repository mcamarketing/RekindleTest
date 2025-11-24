-- Model Registry Table
-- Purpose: Track all fine-tuned LLM models and their performance
-- Part of: Flywheel Architecture - LLM Training Pipeline

CREATE TABLE IF NOT EXISTS model_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Model identification
  model_id TEXT NOT NULL UNIQUE, -- OpenAI model ID (e.g., "ft:gpt-4:org:rekindle-v2:abc123")
  model_version TEXT NOT NULL, -- Semantic version (e.g., "v2.1.0")
  base_model TEXT NOT NULL, -- Base model (e.g., "gpt-4o-2024-08-06")
  model_suffix TEXT, -- Suffix used in fine-tuning

  -- Training metadata
  fine_tuning_job_id TEXT NOT NULL, -- OpenAI fine-tuning job ID
  training_file_id TEXT, -- OpenAI training file ID
  validation_file_id TEXT, -- OpenAI validation file ID
  trained_tokens INT, -- Number of tokens used in training
  training_duration_seconds INT, -- How long training took

  -- Training data stats
  training_examples_count INT, -- Number of training examples
  positive_examples INT, -- Number of positive examples
  negative_examples INT, -- Number of negative examples
  deals_in_training INT, -- Number of closed deals in training data
  avg_deal_value DECIMAL(12,2), -- Average deal value in training data

  -- Deployment status
  status TEXT NOT NULL DEFAULT 'training', -- 'training', 'ready', 'deployed', 'archived', 'failed'
  deployed_at TIMESTAMPTZ, -- When this model was deployed
  archived_at TIMESTAMPTZ, -- When this model was archived

  -- Organization filter (if model is org-specific)
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  is_global BOOLEAN DEFAULT TRUE, -- True = used for all orgs, False = org-specific

  -- A/B testing
  traffic_percentage FLOAT DEFAULT 0.0, -- Percentage of traffic routed to this model (0.0-100.0)
  ab_test_group TEXT, -- 'control', 'variant_a', 'variant_b', etc.

  -- Performance metrics (updated as model is used)
  total_messages_sent INT DEFAULT 0,
  total_replies INT DEFAULT 0,
  total_meetings_booked INT DEFAULT 0,
  total_deals_closed INT DEFAULT 0,
  total_revenue DECIMAL(12,2) DEFAULT 0,

  -- Calculated performance (updated daily)
  reply_rate FLOAT, -- Replies / Messages sent
  meeting_rate FLOAT, -- Meetings / Messages sent
  close_rate FLOAT, -- Deals / Messages sent
  avg_revenue_per_message DECIMAL(12,2),

  -- Comparison to baseline
  reply_rate_vs_baseline FLOAT, -- % improvement over baseline model
  meeting_rate_vs_baseline FLOAT,
  close_rate_vs_baseline FLOAT,

  -- Model notes
  description TEXT,
  changelog TEXT, -- What changed in this version
  training_notes TEXT, -- Notes about training process

  CONSTRAINT model_registry_status_check CHECK (status IN ('training', 'ready', 'deployed', 'archived', 'failed')),
  CONSTRAINT model_registry_traffic_percentage_check CHECK (traffic_percentage >= 0 AND traffic_percentage <= 100)
);

-- Indexes
CREATE INDEX idx_model_registry_model_id ON model_registry(model_id);
CREATE INDEX idx_model_registry_status ON model_registry(status);
CREATE INDEX idx_model_registry_deployed ON model_registry(deployed_at DESC) WHERE status = 'deployed';
CREATE INDEX idx_model_registry_org_id ON model_registry(organization_id) WHERE organization_id IS NOT NULL;

-- Composite index for active models
CREATE INDEX idx_model_registry_active ON model_registry(status, traffic_percentage DESC)
  WHERE status IN ('deployed', 'ready');

-- Row-Level Security
ALTER TABLE model_registry ENABLE ROW LEVEL SECURITY;

-- Policy: All users can view model registry
CREATE POLICY "Users can view model registry"
  ON model_registry
  FOR SELECT
  USING (TRUE);

-- Policy: Only service role can insert/update
CREATE POLICY "Service role can manage model registry"
  ON model_registry
  FOR ALL
  USING (TRUE)
  WITH CHECK (TRUE);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_model_registry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_model_registry_updated_at
  BEFORE UPDATE ON model_registry
  FOR EACH ROW
  EXECUTE FUNCTION update_model_registry_updated_at();

-- View: Active models (deployed or ready)
CREATE OR REPLACE VIEW active_models AS
SELECT
  id,
  model_id,
  model_version,
  base_model,
  status,
  deployed_at,
  traffic_percentage,
  ab_test_group,
  organization_id,
  is_global,

  -- Performance metrics
  total_messages_sent,
  total_replies,
  total_meetings_booked,
  total_deals_closed,
  total_revenue,
  reply_rate,
  meeting_rate,
  close_rate,
  avg_revenue_per_message,

  -- Comparison to baseline
  reply_rate_vs_baseline,
  meeting_rate_vs_baseline,
  close_rate_vs_baseline,

  created_at,
  updated_at
FROM model_registry
WHERE status IN ('deployed', 'ready')
ORDER BY deployed_at DESC;

-- View: Model performance leaderboard
CREATE OR REPLACE VIEW model_leaderboard AS
SELECT
  model_id,
  model_version,
  status,
  deployed_at,

  -- Messages and outcomes
  total_messages_sent,
  total_replies,
  total_meetings_booked,
  total_deals_closed,

  -- Performance rates
  reply_rate,
  meeting_rate,
  close_rate,

  -- Revenue
  total_revenue,
  avg_revenue_per_message,

  -- Ranking
  RANK() OVER (ORDER BY close_rate DESC NULLS LAST) as close_rate_rank,
  RANK() OVER (ORDER BY reply_rate DESC NULLS LAST) as reply_rate_rank,
  RANK() OVER (ORDER BY meeting_rate DESC NULLS LAST) as meeting_rate_rank,
  RANK() OVER (ORDER BY total_revenue DESC NULLS LAST) as revenue_rank
FROM model_registry
WHERE status = 'deployed'
  AND total_messages_sent >= 100 -- Min sample size
ORDER BY close_rate DESC;

-- Grant access
GRANT ALL ON model_registry TO service_role;
GRANT SELECT ON active_models TO service_role;
GRANT SELECT ON model_leaderboard TO service_role;

-- Comments
COMMENT ON TABLE model_registry IS 'Tracks all fine-tuned LLM models, their performance, and deployment status. Part of Flywheel Architecture LLM training pipeline.';
COMMENT ON COLUMN model_registry.model_id IS 'OpenAI fine-tuned model ID (e.g., ft:gpt-4:org:suffix:id)';
COMMENT ON COLUMN model_registry.traffic_percentage IS 'Percentage of requests routed to this model (0-100). Sum across deployed models should = 100.';
COMMENT ON COLUMN model_registry.reply_rate_vs_baseline IS 'Percentage improvement over baseline model (positive = better)';
COMMENT ON VIEW active_models IS 'Shows all deployed or ready-to-deploy models';
COMMENT ON VIEW model_leaderboard IS 'Performance leaderboard of deployed models (ranked by close rate, reply rate, etc.)';
