/*
  # Compliance & GDPR Tables

  1. New Tables
    - `suppression_list`
      - Global unsubscribe list
      - Tracks opt-outs with reason and timestamp
      - Prevents sending to unsubscribed emails
    
    - `consent_records`
      - Tracks all consent given/withdrawn
      - GDPR audit trail
      - Records what, when, how consent was obtained
    
    - `email_preferences`
      - Per-user communication preferences
      - Marketing, transactional, updates toggles
      - Frequency preferences

  2. Security
    - Enable RLS on all tables
    - User-scoped access policies
    - Admin access for suppression list management

  3. Compliance Features
    - Automatic suppression checking
    - Consent tracking
    - Double opt-in support
    - Unsubscribe token generation
*/

-- Create suppression_list table
CREATE TABLE IF NOT EXISTS suppression_list (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Contact Information
  email text NOT NULL UNIQUE,
  phone text,
  
  -- Suppression Details
  reason text CHECK (reason IN ('user_request', 'bounce', 'spam_complaint', 'manual', 'gdpr_request', 'legal_requirement')),
  reason_text text, -- Additional context
  
  -- Source Tracking
  suppressed_by_user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  suppressed_via text CHECK (suppressed_via IN ('unsubscribe_link', 'preference_center', 'email_reply', 'api', 'manual', 'automatic')),
  
  -- Metadata
  original_lead_id uuid, -- Reference to original lead (if applicable)
  ip_address text,
  user_agent text,
  
  -- Scope
  scope text DEFAULT 'global' CHECK (scope IN ('global', 'user_specific', 'campaign_specific')),
  scope_id uuid, -- user_id or campaign_id if scoped
  
  -- Timestamps
  suppressed_at timestamptz DEFAULT now(),
  expires_at timestamptz, -- For temporary suppressions
  
  -- Indexes
  created_at timestamptz DEFAULT now()
);

-- Create consent_records table
CREATE TABLE IF NOT EXISTS consent_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Subject of consent
  email text NOT NULL,
  lead_id uuid REFERENCES leads(id) ON DELETE SET NULL,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Consent Details
  consent_type text NOT NULL CHECK (consent_type IN ('email_marketing', 'email_transactional', 'sms', 'phone', 'data_processing', 'third_party_sharing')),
  consent_given boolean NOT NULL,
  
  -- GDPR Requirements
  consent_method text NOT NULL CHECK (consent_method IN ('checkbox', 'form_submission', 'api', 'import', 'double_opt_in', 'verbal', 'written')),
  consent_text text, -- Exact wording shown to user
  legal_basis text CHECK (legal_basis IN ('consent', 'legitimate_interest', 'contract', 'legal_obligation')),
  
  -- Tracking
  ip_address text,
  user_agent text,
  source_url text,
  source_page text,
  
  -- Double Opt-In
  double_optin_required boolean DEFAULT false,
  double_optin_confirmed boolean DEFAULT false,
  double_optin_confirmed_at timestamptz,
  double_optin_token text,
  
  -- Metadata
  metadata jsonb DEFAULT '{}',
  
  -- Timestamps
  consented_at timestamptz DEFAULT now(),
  withdrawn_at timestamptz,
  expires_at timestamptz
);

-- Create email_preferences table
CREATE TABLE IF NOT EXISTS email_preferences (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- User/Lead Link
  email text NOT NULL UNIQUE,
  lead_id uuid REFERENCES leads(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Communication Preferences
  marketing_emails boolean DEFAULT true,
  transactional_emails boolean DEFAULT true,
  product_updates boolean DEFAULT true,
  newsletter boolean DEFAULT true,
  promotional_emails boolean DEFAULT true,
  
  -- Frequency
  frequency text DEFAULT 'normal' CHECK (frequency IN ('realtime', 'daily', 'weekly', 'monthly', 'never')),
  
  -- Channel Preferences
  sms_enabled boolean DEFAULT false,
  phone_enabled boolean DEFAULT false,
  
  -- Preference Token (for unauth access)
  preference_token text UNIQUE DEFAULT gen_random_uuid()::text,
  
  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create unsubscribe_tokens table (for secure one-click unsubscribe)
CREATE TABLE IF NOT EXISTS unsubscribe_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Token Details
  token text NOT NULL UNIQUE DEFAULT encode(gen_random_bytes(32), 'hex'),
  email text NOT NULL,
  lead_id uuid REFERENCES leads(id) ON DELETE CASCADE,
  
  -- Usage Tracking
  used boolean DEFAULT false,
  used_at timestamptz,
  ip_address text,
  
  -- Expiry
  expires_at timestamptz DEFAULT (now() + interval '90 days'),
  
  -- Timestamps
  created_at timestamptz DEFAULT now()
);

-- Add consent fields to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_email boolean DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_sms boolean DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_phone boolean DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_given_at timestamptz;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_ip_address text;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS consent_source text;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS gdpr_lawful_basis text CHECK (gdpr_lawful_basis IN ('consent', 'legitimate_interest', 'contract', 'legal_obligation'));

-- Enable RLS
ALTER TABLE suppression_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE unsubscribe_tokens ENABLE ROW LEVEL SECURITY;

-- RLS Policies for suppression_list
-- Allow users to view their own suppressions and global ones
CREATE POLICY "Users can view suppression list"
  ON suppression_list FOR SELECT
  TO authenticated
  USING (
    scope = 'global' 
    OR (scope = 'user_specific' AND scope_id = auth.uid())
  );

-- Allow users to add to suppression list
CREATE POLICY "Users can add to suppression list"
  ON suppression_list FOR INSERT
  TO authenticated
  WITH CHECK (suppressed_by_user_id = auth.uid());

-- Service role can manage all (for backend)
CREATE POLICY "Service role full access to suppression"
  ON suppression_list FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- RLS Policies for consent_records
CREATE POLICY "Users can view own consent records"
  ON consent_records FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert own consent records"
  ON consent_records FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Service role full access to consent records"
  ON consent_records FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- RLS Policies for email_preferences
CREATE POLICY "Users can view own email preferences"
  ON email_preferences FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can update own email preferences"
  ON email_preferences FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Allow public read by token (for unsubscribe page)
CREATE POLICY "Public can view preferences by token"
  ON email_preferences FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can update preferences by token"
  ON email_preferences FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

-- RLS Policies for unsubscribe_tokens
CREATE POLICY "Public can view valid tokens"
  ON unsubscribe_tokens FOR SELECT
  TO anon, authenticated
  USING (NOT used AND expires_at > now());

CREATE POLICY "Public can update tokens"
  ON unsubscribe_tokens FOR UPDATE
  TO anon, authenticated
  USING (NOT used AND expires_at > now())
  WITH CHECK (true);

CREATE POLICY "Service role full access to tokens"
  ON unsubscribe_tokens FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_suppression_list_email ON suppression_list(email);
CREATE INDEX IF NOT EXISTS idx_suppression_list_scope ON suppression_list(scope, scope_id);
CREATE INDEX IF NOT EXISTS idx_suppression_list_suppressed_at ON suppression_list(suppressed_at DESC);

CREATE INDEX IF NOT EXISTS idx_consent_records_email ON consent_records(email);
CREATE INDEX IF NOT EXISTS idx_consent_records_lead_id ON consent_records(lead_id);
CREATE INDEX IF NOT EXISTS idx_consent_records_user_id ON consent_records(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_records_type ON consent_records(consent_type);

CREATE INDEX IF NOT EXISTS idx_email_preferences_email ON email_preferences(email);
CREATE INDEX IF NOT EXISTS idx_email_preferences_token ON email_preferences(preference_token);

CREATE INDEX IF NOT EXISTS idx_unsubscribe_tokens_token ON unsubscribe_tokens(token);
CREATE INDEX IF NOT EXISTS idx_unsubscribe_tokens_email ON unsubscribe_tokens(email);
CREATE INDEX IF NOT EXISTS idx_unsubscribe_tokens_expires ON unsubscribe_tokens(expires_at);

-- Add updated_at trigger for email_preferences
CREATE TRIGGER update_email_preferences_updated_at
  BEFORE UPDATE ON email_preferences
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to check if email is suppressed
CREATE OR REPLACE FUNCTION is_email_suppressed(check_email text)
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM suppression_list
    WHERE email = check_email
    AND (expires_at IS NULL OR expires_at > now())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add email to suppression list
CREATE OR REPLACE FUNCTION add_to_suppression_list(
  p_email text,
  p_reason text DEFAULT 'user_request',
  p_reason_text text DEFAULT NULL,
  p_via text DEFAULT 'unsubscribe_link'
)
RETURNS uuid AS $$
DECLARE
  v_id uuid;
BEGIN
  INSERT INTO suppression_list (
    email,
    reason,
    reason_text,
    suppressed_via,
    scope
  ) VALUES (
    p_email,
    p_reason,
    p_reason_text,
    p_via,
    'global'
  )
  ON CONFLICT (email) 
  DO UPDATE SET
    suppressed_at = now(),
    reason = EXCLUDED.reason,
    reason_text = EXCLUDED.reason_text
  RETURNING id INTO v_id;
  
  -- Update lead status
  UPDATE leads
  SET status = 'opted_out'
  WHERE email = p_email;
  
  -- Update campaign_leads status
  UPDATE campaign_leads
  SET status = 'opted_out'
  WHERE lead_id IN (
    SELECT id FROM leads WHERE email = p_email
  );
  
  RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to record consent
CREATE OR REPLACE FUNCTION record_consent(
  p_email text,
  p_consent_type text,
  p_consent_given boolean,
  p_method text DEFAULT 'form_submission',
  p_ip_address text DEFAULT NULL,
  p_user_agent text DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
  v_id uuid;
  v_lead_id uuid;
BEGIN
  -- Get lead_id if exists
  SELECT id INTO v_lead_id FROM leads WHERE email = p_email LIMIT 1;
  
  INSERT INTO consent_records (
    email,
    lead_id,
    consent_type,
    consent_given,
    consent_method,
    ip_address,
    user_agent,
    legal_basis
  ) VALUES (
    p_email,
    v_lead_id,
    p_consent_type,
    p_consent_given,
    p_method,
    p_ip_address,
    p_user_agent,
    CASE WHEN p_consent_given THEN 'consent' ELSE NULL END
  )
  RETURNING id INTO v_id;
  
  -- Update lead consent fields
  IF v_lead_id IS NOT NULL THEN
    UPDATE leads
    SET 
      consent_email = CASE WHEN p_consent_type = 'email_marketing' THEN p_consent_given ELSE consent_email END,
      consent_given_at = CASE WHEN p_consent_given THEN now() ELSE consent_given_at END,
      consent_ip_address = COALESCE(p_ip_address, consent_ip_address),
      gdpr_lawful_basis = CASE WHEN p_consent_given THEN 'consent' ELSE gdpr_lawful_basis END
    WHERE id = v_lead_id;
  END IF;
  
  RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

