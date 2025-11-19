-- Create pilot_applications table
CREATE TABLE IF NOT EXISTS public.pilot_applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Company Info
  company_name TEXT NOT NULL,
  company_website TEXT NOT NULL,
  company_size TEXT NOT NULL,
  industry TEXT NOT NULL,
  
  -- Contact Info
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  role TEXT NOT NULL,
  
  -- Qualification
  average_deal_value TEXT NOT NULL,
  dormant_leads_count TEXT NOT NULL,
  current_crm TEXT NOT NULL,
  primary_challenge TEXT NOT NULL,
  
  -- Commitment
  agreed_to_30_days BOOLEAN DEFAULT TRUE,
  agreed_to_performance_fee BOOLEAN DEFAULT TRUE,
  
  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'contacted')),
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  reviewed_by UUID REFERENCES auth.users(id),
  notes TEXT,
  
  -- Constraints
  CONSTRAINT unique_email UNIQUE (email)
);

-- Enable RLS
ALTER TABLE public.pilot_applications ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Only admins can read pilot applications
CREATE POLICY "Admins can read pilot applications"
ON public.pilot_applications
FOR SELECT
TO authenticated
USING (
  -- TODO: Replace with actual admin check
  -- For now, allow authenticated users to read their own application
  email = (SELECT email FROM auth.users WHERE id = auth.uid())
);

-- RLS Policy: Anyone can insert their pilot application (public form)
CREATE POLICY "Anyone can submit pilot application"
ON public.pilot_applications
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

-- Indexes for performance
CREATE INDEX idx_pilot_applications_status ON public.pilot_applications(status);
CREATE INDEX idx_pilot_applications_created_at ON public.pilot_applications(created_at DESC);
CREATE INDEX idx_pilot_applications_email ON public.pilot_applications(email);

-- Comments
COMMENT ON TABLE public.pilot_applications IS 'Stores pilot program applications from landing page';
COMMENT ON COLUMN public.pilot_applications.status IS 'Application status: pending, approved, rejected, contacted';
COMMENT ON COLUMN public.pilot_applications.agreed_to_30_days IS 'User agreed to 30-day pilot commitment';
COMMENT ON COLUMN public.pilot_applications.agreed_to_performance_fee IS 'User agreed to performance-based pricing (2.5-3% ACV)';

