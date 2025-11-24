-- Migration to update pilot period from 60 days to 30 days
-- Run this if the original migration has already been executed

-- Rename column if it exists
DO $$ 
BEGIN
  IF EXISTS (
    SELECT 1 
    FROM information_schema.columns 
    WHERE table_name = 'pilot_applications' 
    AND column_name = 'agreed_to_60_days'
  ) THEN
    ALTER TABLE public.pilot_applications 
    RENAME COLUMN agreed_to_60_days TO agreed_to_30_days;
    
    COMMENT ON COLUMN public.pilot_applications.agreed_to_30_days IS 'User agreed to 30-day pilot commitment';
  END IF;
END $$;









