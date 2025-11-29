-- Add ARE (Autonomous Revenue Engine) columns to revival_messages table
-- These columns store ARE planning, execution, and evaluation data

ALTER TABLE revival_messages
ADD COLUMN IF NOT EXISTS are_plan JSONB,
ADD COLUMN IF NOT EXISTS are_execution JSONB,
ADD COLUMN IF NOT EXISTS are_content JSONB,
ADD COLUMN IF NOT EXISTS are_evaluation JSONB,
ADD COLUMN IF NOT EXISTS are_guardrail JSONB,
ADD COLUMN IF NOT EXISTS are_metadata JSONB;

-- Add indexes for ARE data queries
CREATE INDEX IF NOT EXISTS idx_revival_messages_are_plan ON revival_messages USING GIN (are_plan);
CREATE INDEX IF NOT EXISTS idx_revival_messages_are_execution ON revival_messages USING GIN (are_execution);
CREATE INDEX IF NOT EXISTS idx_revival_messages_are_evaluation ON revival_messages USING GIN (are_evaluation);

-- Add a check constraint to limit JSONB size (prevent 413 errors)
-- PostgreSQL doesn't have a direct size limit on JSONB, but we can add a constraint
-- This is a safety measure to prevent extremely large payloads
ALTER TABLE revival_messages
ADD CONSTRAINT check_are_plan_size CHECK (octet_length(are_plan::text) < 500000), -- ~500KB limit
ADD CONSTRAINT check_are_execution_size CHECK (octet_length(are_execution::text) < 1000000), -- ~1MB limit
ADD CONSTRAINT check_are_content_size CHECK (octet_length(are_content::text) < 500000), -- ~500KB limit
ADD CONSTRAINT check_are_evaluation_size CHECK (octet_length(are_evaluation::text) < 200000), -- ~200KB limit
ADD CONSTRAINT check_are_guardrail_size CHECK (octet_length(are_guardrail::text) < 100000), -- ~100KB limit
ADD CONSTRAINT check_are_metadata_size CHECK (octet_length(are_metadata::text) < 100000); -- ~100KB limit

-- Update RLS policies to include ARE columns
-- (No changes needed as existing policies cover all columns)