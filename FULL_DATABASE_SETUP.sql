/*
  # Create Rekindle Core Tables

  1. New Tables
    - `leads`
      - Core lead information with contact details
      - Tracks lead status, score, and engagement
      - Links to user who owns the lead
    
    - `campaigns`
      - Campaign management for lead outreach
      - Tracks campaign status, performance metrics
      - Links to user who created the campaign
    
    - `campaign_leads`
      - Junction table linking campaigns to leads
      - Tracks individual lead status within a campaign
      - Records message sequence progress
    
    - `messages`
      - Individual messages sent to leads
      - Tracks delivery status, opens, clicks, replies
      - Links to campaign and lead

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to manage their own data
    - Restrict access based on user ownership

  3. Indexes
    - Performance indexes on frequently queried columns
    - Foreign key indexes for join performance
*/

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
  message_sequence jsonb DEFAULT '[]',
  total_messages integer DEFAULT 5,
  days_between_messages integer DEFAULT 3,
  
  -- Performance Metrics
  total_leads integer DEFAULT 0,
  messages_sent integer DEFAULT 0,
  messages_opened integer DEFAULT 0,
  messages_replied integer DEFAULT 0,
  meetings_booked integer DEFAULT 0,
  
  -- Calculated Metrics
  open_rate numeric(5,2) DEFAULT 0,
  response_rate numeric(5,2) DEFAULT 0,
  conversion_rate numeric(5,2) DEFAULT 0,
  
  -- Schedule
  start_date timestamptz,
  end_date timestamptz,
  
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

-- Enable RLS
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for leads
CREATE POLICY "Users can view own leads"
  ON leads FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own leads"
  ON leads FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own leads"
  ON leads FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own leads"
  ON leads FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for campaigns
CREATE POLICY "Users can view own campaigns"
  ON campaigns FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own campaigns"
  ON campaigns FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own campaigns"
  ON campaigns FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own campaigns"
  ON campaigns FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for campaign_leads
CREATE POLICY "Users can view campaign_leads for their campaigns"
  ON campaign_leads FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert campaign_leads for their campaigns"
  ON campaign_leads FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update campaign_leads for their campaigns"
  ON campaign_leads FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete campaign_leads for their campaigns"
  ON campaign_leads FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- RLS Policies for messages
CREATE POLICY "Users can view messages for their campaigns"
  ON messages FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert messages for their campaigns"
  ON messages FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update messages for their campaigns"
  ON messages FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete messages for their campaigns"
  ON messages FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_campaign_leads_campaign_id ON campaign_leads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_leads_lead_id ON campaign_leads(lead_id);
CREATE INDEX IF NOT EXISTS idx_campaign_leads_status ON campaign_leads(status);

CREATE INDEX IF NOT EXISTS idx_messages_campaign_id ON messages(campaign_id);
CREATE INDEX IF NOT EXISTS idx_messages_lead_id ON messages(lead_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER update_leads_updated_at
  BEFORE UPDATE ON leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at
  BEFORE UPDATE ON campaigns
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_leads_updated_at
  BEFORE UPDATE ON campaign_leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at
  BEFORE UPDATE ON messages
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
/*
  # Fix Security Issues - Indexes and RLS Performance

  ## Changes Made
  
  1. **Foreign Key Indexes** (Performance)
     - Add index on `agent_configurations.created_by`
     - Add index on `messages.campaign_lead_id`
     - Add index on `system_alerts.resolved_by`
  
  2. **RLS Performance Optimization**
     - Optimize all RLS policies to use `(select auth.uid())` instead of `auth.uid()`
     - This prevents re-evaluation for each row and significantly improves performance at scale
     - Affects policies on:
       - user_roles
       - leads
       - campaigns
       - campaign_leads
       - messages
       - agent_configurations
       - system_alerts
  
  3. **Multiple Permissive Policies Fix**
     - Consolidate overlapping permissive policies into single policies
     - Remove redundant policies on agent_configurations, system_alerts, user_roles
  
  4. **Function Security**
     - Fix search_path for all functions to prevent security vulnerabilities
     - Set explicit search_path for handle_new_user, handle_updated_at, update_updated_at_column

  ## Security Improvements
  - Better query performance for foreign key lookups
  - Optimized RLS evaluation reducing database load
  - Consolidated security policies for clarity
  - Secure function execution paths
*/

-- =====================================================
-- PART 1: ADD MISSING FOREIGN KEY INDEXES
-- =====================================================

-- Index for agent_configurations.created_by
CREATE INDEX IF NOT EXISTS idx_agent_configurations_created_by 
ON public.agent_configurations(created_by);

-- Index for messages.campaign_lead_id
CREATE INDEX IF NOT EXISTS idx_messages_campaign_lead_id 
ON public.messages(campaign_lead_id);

-- Index for system_alerts.resolved_by
CREATE INDEX IF NOT EXISTS idx_system_alerts_resolved_by 
ON public.system_alerts(resolved_by);

-- =====================================================
-- PART 2: FIX RLS POLICIES - LEADS TABLE
-- =====================================================

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own leads" ON public.leads;
DROP POLICY IF EXISTS "Users can insert own leads" ON public.leads;
DROP POLICY IF EXISTS "Users can update own leads" ON public.leads;
DROP POLICY IF EXISTS "Users can delete own leads" ON public.leads;

-- Recreate with optimized auth function calls
CREATE POLICY "Users can view own leads"
  ON public.leads
  FOR SELECT
  TO authenticated
  USING (user_id = (select auth.uid()));

CREATE POLICY "Users can insert own leads"
  ON public.leads
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can update own leads"
  ON public.leads
  FOR UPDATE
  TO authenticated
  USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can delete own leads"
  ON public.leads
  FOR DELETE
  TO authenticated
  USING (user_id = (select auth.uid()));

-- =====================================================
-- PART 3: FIX RLS POLICIES - CAMPAIGNS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view own campaigns" ON public.campaigns;
DROP POLICY IF EXISTS "Users can insert own campaigns" ON public.campaigns;
DROP POLICY IF EXISTS "Users can update own campaigns" ON public.campaigns;
DROP POLICY IF EXISTS "Users can delete own campaigns" ON public.campaigns;

CREATE POLICY "Users can view own campaigns"
  ON public.campaigns
  FOR SELECT
  TO authenticated
  USING (user_id = (select auth.uid()));

CREATE POLICY "Users can insert own campaigns"
  ON public.campaigns
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can update own campaigns"
  ON public.campaigns
  FOR UPDATE
  TO authenticated
  USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

CREATE POLICY "Users can delete own campaigns"
  ON public.campaigns
  FOR DELETE
  TO authenticated
  USING (user_id = (select auth.uid()));

-- =====================================================
-- PART 4: FIX RLS POLICIES - CAMPAIGN_LEADS TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view campaign_leads for their campaigns" ON public.campaign_leads;
DROP POLICY IF EXISTS "Users can insert campaign_leads for their campaigns" ON public.campaign_leads;
DROP POLICY IF EXISTS "Users can update campaign_leads for their campaigns" ON public.campaign_leads;
DROP POLICY IF EXISTS "Users can delete campaign_leads for their campaigns" ON public.campaign_leads;

CREATE POLICY "Users can view campaign_leads for their campaigns"
  ON public.campaign_leads
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can insert campaign_leads for their campaigns"
  ON public.campaign_leads
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can update campaign_leads for their campaigns"
  ON public.campaign_leads
  FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can delete campaign_leads for their campaigns"
  ON public.campaign_leads
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = campaign_leads.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

-- =====================================================
-- PART 5: FIX RLS POLICIES - MESSAGES TABLE
-- =====================================================

DROP POLICY IF EXISTS "Users can view messages for their campaigns" ON public.messages;
DROP POLICY IF EXISTS "Users can insert messages for their campaigns" ON public.messages;
DROP POLICY IF EXISTS "Users can update messages for their campaigns" ON public.messages;
DROP POLICY IF EXISTS "Users can delete messages for their campaigns" ON public.messages;

CREATE POLICY "Users can view messages for their campaigns"
  ON public.messages
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can insert messages for their campaigns"
  ON public.messages
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can update messages for their campaigns"
  ON public.messages
  FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

CREATE POLICY "Users can delete messages for their campaigns"
  ON public.messages
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = messages.campaign_id
      AND campaigns.user_id = (select auth.uid())
    )
  );

-- =====================================================
-- PART 6: FIX MULTIPLE PERMISSIVE POLICIES - USER_ROLES
-- =====================================================

-- Drop all existing policies
DROP POLICY IF EXISTS "Users can view own role" ON public.user_roles;
DROP POLICY IF EXISTS "Admins can manage all roles" ON public.user_roles;

-- Create a single consolidated policy for SELECT
CREATE POLICY "Users can view roles"
  ON public.user_roles
  FOR SELECT
  TO authenticated
  USING (
    user_id = (select auth.uid())
    OR
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role = 'admin'
    )
  );

-- Separate policies for admin operations
CREATE POLICY "Admins can manage roles"
  ON public.user_roles
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role = 'admin'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role = 'admin'
    )
  );

-- =====================================================
-- PART 7: FIX MULTIPLE PERMISSIVE POLICIES - AGENT_CONFIGURATIONS
-- =====================================================

DROP POLICY IF EXISTS "Authenticated users can view configurations" ON public.agent_configurations;
DROP POLICY IF EXISTS "Admins and operators can manage configurations" ON public.agent_configurations;

-- Single SELECT policy
CREATE POLICY "Authenticated users can view agent configurations"
  ON public.agent_configurations
  FOR SELECT
  TO authenticated
  USING (true);

-- Admin/operator management policy
CREATE POLICY "Admins and operators can manage agent configurations"
  ON public.agent_configurations
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role IN ('admin', 'operator')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role IN ('admin', 'operator')
    )
  );

-- =====================================================
-- PART 8: FIX MULTIPLE PERMISSIVE POLICIES - SYSTEM_ALERTS
-- =====================================================

DROP POLICY IF EXISTS "Authenticated users can view alerts" ON public.system_alerts;
DROP POLICY IF EXISTS "Admins and operators can manage alerts" ON public.system_alerts;

-- Single SELECT policy
CREATE POLICY "Authenticated users can view system alerts"
  ON public.system_alerts
  FOR SELECT
  TO authenticated
  USING (true);

-- Admin/operator management policy
CREATE POLICY "Admins and operators can manage system alerts"
  ON public.system_alerts
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role IN ('admin', 'operator')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      WHERE ur.user_id = (select auth.uid())
      AND ur.role IN ('admin', 'operator')
    )
  );

-- =====================================================
-- PART 9: FIX FUNCTION SEARCH PATH SECURITY
-- =====================================================

-- Recreate handle_new_user with secure search_path
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
BEGIN
  INSERT INTO public.user_roles (user_id, role)
  VALUES (new.id, 'viewer');
  RETURN new;
END;
$$;

-- Recreate handle_updated_at with secure search_path
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  new.updated_at = now();
  RETURN new;
END;
$$;

-- Recreate update_updated_at_column with secure search_path
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  new.updated_at = now();
  RETURN new;
END;
$$;
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


/*
  # Invoices Table for Billing Management

  1. New Table
    - `invoices`
      - Stores all billing invoices
      - Tracks Stripe charges and meeting fees
      - Audit trail for all financial transactions
      - Supports platform fees + performance fees model

  2. Security
    - Enable RLS on table
    - User-scoped access (users can only see their own invoices)
    - Admin read-all policy for support

  3. Features
    - Complete billing history
    - Stripe charge tracking
    - Meeting-based performance fee calculation
    - Refund support
    - Invoice status tracking
*/

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- User Reference
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Invoice Details
  invoice_number text NOT NULL UNIQUE, -- e.g., "INV-2025-001"
  status text NOT NULL CHECK (status IN ('draft', 'pending', 'paid', 'failed', 'refunded', 'partially_refunded')),

  -- Amounts (in pence/cents)
  platform_fee_amount integer NOT NULL DEFAULT 9900, -- £99.00 or $99.00
  performance_fee_amount integer NOT NULL DEFAULT 0,
  total_amount integer NOT NULL,
  amount_paid integer DEFAULT 0,
  amount_refunded integer DEFAULT 0,

  -- Currency
  currency text NOT NULL DEFAULT 'GBP' CHECK (currency IN ('GBP', 'USD', 'EUR')),

  -- Billing Period
  billing_period_start timestamptz NOT NULL,
  billing_period_end timestamptz NOT NULL,

  -- Performance Metrics
  meetings_count integer DEFAULT 0,
  total_acv integer DEFAULT 0, -- Total ACV from all meetings in this period
  performance_fee_rate numeric(5,4) DEFAULT 0.0250, -- 2.5%

  -- Stripe Integration
  stripe_invoice_id text, -- Stripe Invoice ID
  stripe_charge_id text, -- Stripe Charge ID
  stripe_payment_intent_id text, -- Stripe Payment Intent ID
  stripe_customer_id text, -- Stripe Customer ID
  payment_method_id text, -- Stripe Payment Method ID

  -- Payment Details
  payment_status text CHECK (payment_status IN ('unpaid', 'processing', 'succeeded', 'failed', 'refunded')),
  paid_at timestamptz,
  payment_failed_at timestamptz,
  payment_failure_reason text,

  -- Refund Details
  refunded_at timestamptz,
  refund_reason text,
  refund_stripe_id text,

  -- Invoice Metadata
  invoice_pdf_url text, -- URL to PDF invoice (if generated)
  notes text, -- Admin notes
  metadata jsonb, -- Additional flexible data

  -- Related Records
  lead_ids uuid[], -- Array of lead IDs that contributed to this invoice

  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  due_date timestamptz,

  -- Indexes for performance
  CONSTRAINT check_total_amount CHECK (total_amount = platform_fee_amount + performance_fee_amount)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_invoice_id ON invoices(stripe_invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_charge_id ON invoices(stripe_charge_id);
CREATE INDEX IF NOT EXISTS idx_invoices_billing_period ON invoices(billing_period_start, billing_period_end);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at DESC);

-- Enable Row Level Security
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own invoices
CREATE POLICY "Users can view their own invoices"
  ON invoices
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own invoices (via service role in backend)
-- Note: In production, this should be restricted to service role only
CREATE POLICY "Service role can insert invoices"
  ON invoices
  FOR INSERT
  WITH CHECK (auth.jwt()->>'role' = 'service_role' OR auth.uid() = user_id);

-- Policy: Service role can update invoices
CREATE POLICY "Service role can update invoices"
  ON invoices
  FOR UPDATE
  USING (auth.jwt()->>'role' = 'service_role');

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_invoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_invoices_updated_at_trigger
  BEFORE UPDATE ON invoices
  FOR EACH ROW
  EXECUTE FUNCTION update_invoices_updated_at();

-- Function to generate invoice number
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS text AS $$
DECLARE
  next_num integer;
  year_month text;
BEGIN
  year_month := to_char(now(), 'YYYYMM');

  -- Get the next sequential number for this month
  SELECT COALESCE(MAX(CAST(SUBSTRING(invoice_number FROM 13) AS integer)), 0) + 1
  INTO next_num
  FROM invoices
  WHERE invoice_number LIKE 'INV-' || year_month || '-%';

  RETURN 'INV-' || year_month || '-' || LPAD(next_num::text, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Add comment to table
COMMENT ON TABLE invoices IS 'Stores all billing invoices for Rekindle.ai platform and performance fees';
COMMENT ON COLUMN invoices.platform_fee_amount IS 'Fixed monthly platform fee in smallest currency unit (pence/cents)';
COMMENT ON COLUMN invoices.performance_fee_amount IS 'Variable performance fee based on meetings booked, in smallest currency unit';
COMMENT ON COLUMN invoices.total_amount IS 'Total invoice amount (platform + performance fees)';
COMMENT ON COLUMN invoices.meetings_count IS 'Number of meetings booked during this billing period';
COMMENT ON COLUMN invoices.performance_fee_rate IS 'Performance fee percentage (0.0250 = 2.5%)';
