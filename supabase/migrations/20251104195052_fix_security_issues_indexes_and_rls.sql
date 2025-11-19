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
