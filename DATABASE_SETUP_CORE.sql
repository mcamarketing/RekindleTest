-- =====================================================
-- REKINDLE CORE DATABASE SETUP
-- =====================================================
-- This script creates only the essential tables needed to get started
-- Run this first, then add other features as needed

-- =====================================================
-- PART 1: CORE TABLES (Leads, Campaigns, Messages)
-- =====================================================

-- Create leads table
CREATE TABLE IF NOT EXISTS leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Contact Information
  first_name text NOT NULL,
  last_name text NOT NULL,
  email text NOT NULL,
  phone text,
  company text,
  job_title text,
  linkedin_url text,

  -- Lead Data
  status text NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'engaged', 'qualified', 'meeting_booked', 'converted', 'unresponsive', 'opted_out')),
  lead_score integer DEFAULT 0 CHECK (lead_score >= 0 AND lead_score <= 100),
  source text DEFAULT 'manual',

  -- Engagement Tracking
  last_contact_date timestamptz,
  last_response_date timestamptz,
  total_messages_sent integer DEFAULT 0,
  total_messages_opened integer DEFAULT 0,
  total_links_clicked integer DEFAULT 0,

  -- Consent & GDPR
  consent_email boolean DEFAULT false,
  consent_sms boolean DEFAULT false,
  consent_phone boolean DEFAULT false,
  consent_given_at timestamptz,
  consent_ip_address text,
  consent_source text,
  gdpr_lawful_basis text CHECK (gdpr_lawful_basis IN ('consent', 'legitimate_interest', 'contract', 'legal_obligation')),

  -- Metadata
  notes text,
  tags text[] DEFAULT '{}',
  custom_fields jsonb DEFAULT '{}',

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Campaign Details
  name text NOT NULL,
  description text,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived')),

  -- Campaign Configuration
  message_template text,
  lead_ids text[] DEFAULT '{}',
  settings jsonb DEFAULT '{}',

  -- Performance Metrics
  total_leads integer DEFAULT 0,
  messages_sent integer DEFAULT 0,
  messages_opened integer DEFAULT 0,
  messages_replied integer DEFAULT 0,
  meetings_booked integer DEFAULT 0,

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create campaign_leads junction table
CREATE TABLE IF NOT EXISTS campaign_leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  lead_id uuid NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

  -- Lead Status in Campaign
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'paused', 'opted_out', 'bounced', 'replied')),
  current_message_index integer DEFAULT 0,

  -- Engagement
  messages_sent integer DEFAULT 0,
  messages_opened integer DEFAULT 0,
  messages_replied integer DEFAULT 0,
  last_message_sent_at timestamptz,
  last_opened_at timestamptz,
  last_replied_at timestamptz,

  -- Next Action
  next_message_scheduled_at timestamptz,

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),

  -- Unique constraint: each lead can only be in a campaign once
  UNIQUE(campaign_id, lead_id)
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  lead_id uuid NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  campaign_lead_id uuid REFERENCES campaign_leads(id) ON DELETE CASCADE,

  -- Message Details
  subject text,
  body text NOT NULL,
  channel text NOT NULL DEFAULT 'email' CHECK (channel IN ('email', 'sms', 'linkedin')),
  message_index integer DEFAULT 0,

  -- Status
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'sent', 'delivered', 'opened', 'clicked', 'replied', 'bounced', 'failed')),

  -- Tracking
  sent_at timestamptz,
  delivered_at timestamptz,
  opened_at timestamptz,
  clicked_at timestamptz,
  replied_at timestamptz,
  bounced_at timestamptz,

  -- Engagement Metrics
  open_count integer DEFAULT 0,
  click_count integer DEFAULT 0,

  -- Reply Data
  reply_text text,
  reply_sentiment text CHECK (reply_sentiment IN ('positive', 'neutral', 'negative', 'objection')),

  -- Metadata
  tracking_id uuid DEFAULT gen_random_uuid(),
  error_message text,
  metadata jsonb DEFAULT '{}',

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- =====================================================
-- PART 2: COMPLIANCE TABLES
-- =====================================================

-- Create suppression_list table
CREATE TABLE IF NOT EXISTS suppression_list (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  phone text,
  reason text CHECK (reason IN ('user_request', 'bounce', 'spam_complaint', 'manual', 'gdpr_request', 'legal_requirement')),
  reason_text text,
  suppressed_by_user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  suppressed_via text CHECK (suppressed_via IN ('unsubscribe_link', 'preference_center', 'email_reply', 'api', 'manual', 'automatic')),
  scope text DEFAULT 'global' CHECK (scope IN ('global', 'user_specific', 'campaign_specific')),
  scope_id uuid,
  suppressed_at timestamptz DEFAULT now(),
  expires_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Create consent_records table
CREATE TABLE IF NOT EXISTS consent_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL,
  lead_id uuid REFERENCES leads(id) ON DELETE SET NULL,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  consent_type text NOT NULL CHECK (consent_type IN ('email_marketing', 'email_transactional', 'sms', 'phone', 'data_processing', 'third_party_sharing')),
  consent_given boolean NOT NULL,
  consent_method text NOT NULL CHECK (consent_method IN ('checkbox', 'form_submission', 'api', 'import', 'double_opt_in', 'verbal', 'written')),
  consent_text text,
  legal_basis text CHECK (legal_basis IN ('consent', 'legitimate_interest', 'contract', 'legal_obligation')),
  ip_address text,
  user_agent text,
  source_url text,
  source_page text,
  double_optin_required boolean DEFAULT false,
  double_optin_confirmed boolean DEFAULT false,
  double_optin_confirmed_at timestamptz,
  double_optin_token text,
  metadata jsonb DEFAULT '{}',
  consented_at timestamptz DEFAULT now(),
  withdrawn_at timestamptz,
  expires_at timestamptz
);

-- =====================================================
-- PART 3: PILOT APPLICATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS pilot_applications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name text NOT NULL,
  company_website text NOT NULL,
  company_size text NOT NULL,
  industry text NOT NULL,
  first_name text NOT NULL,
  last_name text NOT NULL,
  email text NOT NULL UNIQUE,
  phone text NOT NULL,
  role text NOT NULL,
  average_deal_value text NOT NULL,
  dormant_leads_count text NOT NULL,
  current_crm text NOT NULL,
  primary_challenge text NOT NULL,
  agreed_to_30_days boolean DEFAULT true,
  agreed_to_performance_fee boolean DEFAULT true,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'contacted')),
  created_at timestamptz DEFAULT now(),
  reviewed_at timestamptz,
  reviewed_by uuid REFERENCES auth.users(id),
  notes text
);

-- =====================================================
-- PART 4: ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppression_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE pilot_applications ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- PART 5: RLS POLICIES
-- =====================================================

-- Leads policies
CREATE POLICY "Users can view own leads" ON leads FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own leads" ON leads FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own leads" ON leads FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own leads" ON leads FOR DELETE USING (auth.uid() = user_id);

-- Campaigns policies
CREATE POLICY "Users can view own campaigns" ON campaigns FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own campaigns" ON campaigns FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own campaigns" ON campaigns FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own campaigns" ON campaigns FOR DELETE USING (auth.uid() = user_id);

-- Campaign leads policies
CREATE POLICY "Users can view campaign_leads" ON campaign_leads FOR SELECT
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_leads.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can insert campaign_leads" ON campaign_leads FOR INSERT
  WITH CHECK (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_leads.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can update campaign_leads" ON campaign_leads FOR UPDATE
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_leads.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can delete campaign_leads" ON campaign_leads FOR DELETE
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = campaign_leads.campaign_id AND campaigns.user_id = auth.uid()));

-- Messages policies
CREATE POLICY "Users can view messages" ON messages FOR SELECT
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = messages.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can insert messages" ON messages FOR INSERT
  WITH CHECK (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = messages.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can update messages" ON messages FOR UPDATE
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = messages.campaign_id AND campaigns.user_id = auth.uid()));
CREATE POLICY "Users can delete messages" ON messages FOR DELETE
  USING (EXISTS (SELECT 1 FROM campaigns WHERE campaigns.id = messages.campaign_id AND campaigns.user_id = auth.uid()));

-- Suppression list policies
CREATE POLICY "Users can view suppressions" ON suppression_list FOR SELECT USING (true);
CREATE POLICY "Anyone can add to suppression" ON suppression_list FOR INSERT WITH CHECK (true);

-- Consent records policies
CREATE POLICY "Users can view own consent" ON consent_records FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert consent" ON consent_records FOR INSERT WITH CHECK (user_id = auth.uid());

-- Pilot applications policies
CREATE POLICY "Anyone can submit pilot application" ON pilot_applications FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can view own application" ON pilot_applications FOR SELECT
  USING (email = (SELECT email FROM auth.users WHERE id = auth.uid()));

-- =====================================================
-- PART 6: INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at DESC);

CREATE INDEX idx_campaign_leads_campaign_id ON campaign_leads(campaign_id);
CREATE INDEX idx_campaign_leads_lead_id ON campaign_leads(lead_id);

CREATE INDEX idx_messages_campaign_id ON messages(campaign_id);
CREATE INDEX idx_messages_lead_id ON messages(lead_id);

CREATE INDEX idx_suppression_list_email ON suppression_list(email);
CREATE INDEX idx_consent_records_email ON consent_records(email);
CREATE INDEX idx_pilot_applications_email ON pilot_applications(email);

-- =====================================================
-- PART 7: TRIGGER FUNCTION FOR updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaign_leads_updated_at BEFORE UPDATE ON campaign_leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
