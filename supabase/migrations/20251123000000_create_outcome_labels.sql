-- Outcome Labels Table for LLM Training Pipeline
-- Purpose: Capture message → outcome chains for GPT-4 fine-tuning
-- Part of: Flywheel Architecture - Proprietary LLM Brain Loop

CREATE TABLE IF NOT EXISTS outcome_labels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Ownership & context
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

  -- Message details (what we sent)
  message_id UUID, -- Reference to sent message if tracked separately
  channel TEXT NOT NULL, -- 'email', 'linkedin', 'sms'
  sequence_step INT NOT NULL DEFAULT 1,
  subject_line TEXT,
  message_body TEXT NOT NULL,

  -- Agent strategy (what the AI decided)
  framework TEXT, -- 'PAS', 'AIDA', 'BAF', 'FAB', 'PASTOR', etc.
  tone TEXT, -- 'professional', 'casual', 'friendly', 'urgent'
  personalization_strategy JSONB, -- Agent decisions on personalization
  agent_decisions JSONB, -- Full agent decision log

  -- Immediate outcomes (delivery & engagement)
  sent_at TIMESTAMPTZ,
  delivered BOOLEAN DEFAULT FALSE,
  delivered_at TIMESTAMPTZ,

  bounced BOOLEAN DEFAULT FALSE,
  bounce_reason TEXT,

  opened BOOLEAN DEFAULT FALSE,
  opened_at TIMESTAMPTZ,
  open_count INT DEFAULT 0,

  clicked BOOLEAN DEFAULT FALSE,
  clicked_at TIMESTAMPTZ,
  click_count INT DEFAULT 0,

  -- Reply outcomes
  replied BOOLEAN DEFAULT FALSE,
  replied_at TIMESTAMPTZ,
  reply_text TEXT,
  reply_sentiment_score FLOAT, -- -1 (negative) to 1 (positive)
  reply_sentiment_label TEXT, -- 'positive', 'neutral', 'negative'

  -- Reply classification
  objection_detected BOOLEAN DEFAULT FALSE,
  objection_type TEXT, -- 'price', 'timing', 'not_interested', 'competitor', 'authority'
  interest_signal BOOLEAN DEFAULT FALSE,
  interest_type TEXT, -- 'high', 'medium', 'low', 'question', 'request_info'

  -- Meeting outcomes
  meeting_requested BOOLEAN DEFAULT FALSE,
  meeting_booked BOOLEAN DEFAULT FALSE,
  meeting_booked_at TIMESTAMPTZ,
  meeting_completed BOOLEAN DEFAULT FALSE,
  meeting_completed_at TIMESTAMPTZ,
  meeting_no_show BOOLEAN DEFAULT FALSE,

  -- Revenue outcomes (from CRM integration)
  opportunity_created BOOLEAN DEFAULT FALSE,
  opportunity_created_at TIMESTAMPTZ,
  opportunity_value DECIMAL(12,2),

  deal_closed BOOLEAN DEFAULT FALSE,
  deal_closed_at TIMESTAMPTZ,
  deal_value DECIMAL(12,2),
  time_to_close_days INT,

  deal_lost BOOLEAN DEFAULT FALSE,
  deal_lost_reason TEXT,

  -- Lead context (for pattern learning)
  lead_industry TEXT,
  lead_role TEXT,
  lead_seniority TEXT, -- 'c-level', 'vp', 'director', 'manager', 'individual'
  company_size INT,
  company_revenue_range TEXT,

  -- ICP scoring (how well did they match ideal customer profile)
  icp_score FLOAT, -- 0.0 to 1.0
  icp_factors JSONB, -- What made them high/low ICP

  -- Model training metadata
  training_label TEXT, -- 'positive_example', 'negative_example', 'neutral'
  training_weight FLOAT DEFAULT 1.0, -- Weight for training (higher = more important)
  included_in_training BOOLEAN DEFAULT FALSE,
  training_batch_id UUID,

  -- Audit
  labeled_at TIMESTAMPTZ,
  labeled_by UUID, -- User who confirmed label (if manual verification)

  CONSTRAINT outcome_labels_sentiment_score_range CHECK (reply_sentiment_score IS NULL OR (reply_sentiment_score >= -1.0 AND reply_sentiment_score <= 1.0)),
  CONSTRAINT outcome_labels_icp_score_range CHECK (icp_score IS NULL OR (icp_score >= 0.0 AND icp_score <= 1.0))
);

-- Indexes for performance
CREATE INDEX idx_outcome_labels_org_id ON outcome_labels(organization_id);
CREATE INDEX idx_outcome_labels_campaign_id ON outcome_labels(campaign_id);
CREATE INDEX idx_outcome_labels_lead_id ON outcome_labels(lead_id);
CREATE INDEX idx_outcome_labels_sent_at ON outcome_labels(sent_at DESC);
CREATE INDEX idx_outcome_labels_training ON outcome_labels(included_in_training, training_label) WHERE included_in_training = TRUE;
CREATE INDEX idx_outcome_labels_replied ON outcome_labels(replied, replied_at DESC) WHERE replied = TRUE;
CREATE INDEX idx_outcome_labels_deal_closed ON outcome_labels(deal_closed, deal_closed_at DESC) WHERE deal_closed = TRUE;

-- Composite index for training data queries
CREATE INDEX idx_outcome_labels_training_query ON outcome_labels(organization_id, included_in_training, training_label, created_at DESC);

-- Row-Level Security (RLS)
ALTER TABLE outcome_labels ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see outcome labels from their organization
CREATE POLICY "Users can view their organization's outcome labels"
  ON outcome_labels
  FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id
      FROM profiles
      WHERE id = auth.uid()
    )
  );

-- Policy: System can insert outcome labels
CREATE POLICY "System can insert outcome labels"
  ON outcome_labels
  FOR INSERT
  WITH CHECK (TRUE); -- Backend service role will insert

-- Policy: Users can update outcome labels in their organization
CREATE POLICY "Users can update their organization's outcome labels"
  ON outcome_labels
  FOR UPDATE
  USING (
    organization_id IN (
      SELECT organization_id
      FROM profiles
      WHERE id = auth.uid()
    )
  );

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_outcome_labels_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_outcome_labels_updated_at
  BEFORE UPDATE ON outcome_labels
  FOR EACH ROW
  EXECUTE FUNCTION update_outcome_labels_updated_at();

-- View: Training-ready outcome labels (for data warehouse ETL)
CREATE OR REPLACE VIEW training_ready_outcomes AS
SELECT
  ol.id,
  ol.organization_id,
  ol.campaign_id,
  ol.lead_id,

  -- Input (what we sent)
  ol.channel,
  ol.subject_line,
  ol.message_body,
  ol.framework,
  ol.tone,
  ol.personalization_strategy,
  ol.agent_decisions,

  -- Context
  ol.lead_industry,
  ol.lead_role,
  ol.lead_seniority,
  ol.company_size,
  ol.icp_score,

  -- Outcomes (labels)
  ol.delivered,
  ol.opened,
  ol.clicked,
  ol.replied,
  ol.reply_sentiment_score,
  ol.reply_sentiment_label,
  ol.objection_detected,
  ol.objection_type,
  ol.interest_signal,
  ol.meeting_booked,
  ol.meeting_completed,
  ol.deal_closed,
  ol.deal_value,
  ol.time_to_close_days,

  -- Training metadata
  ol.training_label,
  ol.training_weight,
  ol.created_at,
  ol.sent_at,
  ol.replied_at,
  ol.deal_closed_at
FROM outcome_labels ol
WHERE ol.included_in_training = TRUE
  AND ol.sent_at IS NOT NULL
ORDER BY ol.created_at DESC;

-- Grant access to service role
GRANT ALL ON outcome_labels TO service_role;
GRANT SELECT ON training_ready_outcomes TO service_role;

-- Comments for documentation
COMMENT ON TABLE outcome_labels IS 'Captures message→outcome chains for LLM training. Part of Flywheel Architecture - Proprietary LLM Brain Loop.';
COMMENT ON COLUMN outcome_labels.agent_decisions IS 'JSON log of all agent decisions that led to this message (PersonalizerAgent, CopywriterAgent, etc.)';
COMMENT ON COLUMN outcome_labels.training_label IS 'Classification for training: positive_example (high engagement/revenue), negative_example (bounced/objection), neutral';
COMMENT ON COLUMN outcome_labels.training_weight IS 'Weight for training. Higher for closed deals (10.0), medium for meetings (5.0), low for replies (1.0)';
COMMENT ON VIEW training_ready_outcomes IS 'View of outcome labels ready for export to data warehouse and GPT-4 training pipeline';
