-- Add start_date column to campaigns table
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/jnhbmemmwtsrfhlztmyq/sql

ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS start_date timestamptz;

-- Add comment to document the column
COMMENT ON COLUMN campaigns.start_date IS 'Timestamp when the campaign was launched/activated';
