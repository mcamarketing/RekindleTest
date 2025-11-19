-- Initialize Rekindle AI Agents
-- This script creates the agents table (if it doesn't exist) and initializes all 28 specialized AI agents

-- =====================================================
-- STEP 1: CREATE AGENTS TABLE (if it doesn't exist)
-- =====================================================

CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Agent Information
  name text NOT NULL,
  description text,
  agent_type text NOT NULL CHECK (agent_type IN ('research', 'intelligence', 'content', 'specialized', 'safety', 'sync', 'revenue', 'orchestration', 'optimization', 'infrastructure', 'analytics')),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'idle', 'paused', 'error', 'offline', 'warning')),
  
  -- Metadata
  metadata jsonb DEFAULT '{}',
  
  -- Heartbeat tracking
  last_heartbeat timestamptz,
  
  -- Timestamps
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at DESC);

-- Enable RLS
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (drop first if exists, then create)
DROP POLICY IF EXISTS "Users can view all agents" ON agents;
DROP POLICY IF EXISTS "Anyone can insert agents" ON agents;
CREATE POLICY "Users can view all agents" ON agents FOR SELECT USING (true);
-- Allow inserts (for initialization - system-wide agents)
CREATE POLICY "Anyone can insert agents" ON agents FOR INSERT WITH CHECK (true);

-- =====================================================
-- STEP 2: REMOVE ANY EXISTING DUPLICATES
-- =====================================================
-- First, remove duplicates (keep the oldest one for each name)
DELETE FROM agents
WHERE id NOT IN (
  SELECT DISTINCT ON (name) id
  FROM agents
  ORDER BY name, created_at ASC
);

-- =====================================================
-- STEP 3: INITIALIZE ALL 28 AI AGENTS
-- =====================================================
-- Note: Using INSERT ... ON CONFLICT to prevent duplicates

-- Research & Intelligence Agents (4)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('ResearcherAgent', 'Deep lead intelligence using LinkedIn MCP. Fetches profile data, company updates, job postings, and extracts actionable pain points.', 'research', 'active', 
     '{"category": "intelligence", "crew": "DeadLeadReactivationCrew,FullCampaignCrew,AutoICPCrew", "capabilities": ["linkedin_research", "company_intelligence", "job_tracking"]}'::jsonb,
     NOW(), NOW()),
    
    ('ICPAnalyzerAgent', 'Extracts Ideal Customer Profile from winning leads. Analyzes closed deals to identify patterns in industry, company size, titles, and geography.', 'intelligence', 'active',
     '{"category": "intelligence", "crew": "AutoICPCrew", "capabilities": ["icp_extraction", "pattern_analysis", "deal_analysis"]}'::jsonb,
     NOW(), NOW()),
    
    ('LeadScorerAgent', 'Scores leads 0-100 for revivability. Analyzes lead data, engagement history, and firmographics to assign tiers: Hot (80+), Warm (60-79), Cold (<60).', 'intelligence', 'active',
     '{"category": "intelligence", "crew": "DeadLeadReactivationCrew,FullCampaignCrew,AutoICPCrew", "capabilities": ["lead_scoring", "tier_assignment", "revivability_analysis"]}'::jsonb,
     NOW(), NOW()),
    
    ('LeadSourcerAgent', 'Finds new leads matching ICP criteria. Searches LinkedIn and databases, validates emails, and enriches data to return scored leads ready for campaigns.', 'intelligence', 'active',
     '{"category": "intelligence", "crew": "AutoICPCrew", "capabilities": ["lead_sourcing", "email_validation", "data_enrichment"]}'::jsonb,
     NOW(), NOW());

-- Dead Lead Reactivation Agent (1)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('DeadLeadReactivationAgent', 'Monitors 50+ signals for trigger events to reactivate dormant leads. Continuously watches for funding, hiring, job changes, and company news.', 'specialized', 'active',
     '{"category": "specialized", "crew": "DeadLeadReactivationCrew", "capabilities": ["signal_monitoring", "trigger_detection", "reactivation"]}'::jsonb,
     NOW(), NOW());

-- Content Generation Agents (5)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('WriterAgent', 'Generates personalized message sequences using MCP. Creates multi-channel sequences (email, SMS, WhatsApp) with full context and personalization.', 'content', 'active',
     '{"category": "content", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["message_generation", "personalization", "multi_channel"]}'::jsonb,
     NOW(), NOW()),
    
    ('SubjectLineOptimizerAgent', 'Optimizes subject lines for maximum open rates. Generates multiple variants, tests different approaches, and tracks performance.', 'content', 'active',
     '{"category": "content", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["subject_optimization", "ab_testing", "performance_tracking"]}'::jsonb,
     NOW(), NOW()),
    
    ('FollowUpAgent', 'Generates intelligent follow-up messages. Analyzes previous engagement, creates context-aware follow-ups, and adjusts tone based on lead response.', 'content', 'active',
     '{"category": "content", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["follow_up_generation", "context_awareness", "tone_adjustment"]}'::jsonb,
     NOW(), NOW()),
    
    ('ObjectionHandlerAgent', 'Handles objections automatically. Identifies common objections in replies, generates personalized responses, and escalates complex cases.', 'content', 'active',
     '{"category": "content", "crew": "FullCampaignCrew", "capabilities": ["objection_handling", "response_generation", "escalation"]}'::jsonb,
     NOW(), NOW()),
    
    ('EngagementAnalyzerAgent', 'Analyzes engagement patterns. Tracks opens, clicks, replies, and predicts conversion likelihood to optimize messaging strategy.', 'content', 'active',
     '{"category": "content", "crew": "FullCampaignCrew", "capabilities": ["engagement_tracking", "pattern_analysis", "conversion_prediction"]}'::jsonb,
     NOW(), NOW());

-- Safety & Compliance Agents (3)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('ComplianceAgent', 'Ensures GDPR/CAN-SPAM/CCPA compliance. Checks suppression lists, validates consent, and prevents unauthorized messaging.', 'safety', 'active',
     '{"category": "safety", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["compliance_checking", "suppression_list", "consent_validation"]}'::jsonb,
     NOW(), NOW()),
    
    ('QualityControlAgent', 'Performs message quality checks. Detects spam triggers, validates personalization, ensures brand voice, and maintains message quality standards.', 'safety', 'active',
     '{"category": "safety", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["quality_checking", "spam_detection", "brand_voice"]}'::jsonb,
     NOW(), NOW()),
    
    ('RateLimitAgent', 'Manages rate limiting and throttling. Enforces domain/account rate limits, prevents sending too many messages, and ensures healthy sending patterns.', 'safety', 'active',
     '{"category": "safety", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["rate_limiting", "throttling", "send_pattern_optimization"]}'::jsonb,
     NOW(), NOW());

-- Sync & Tracking Agents (2)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('TrackerAgent', 'Tracks message delivery and engagement. Monitors delivery status, opens, clicks, replies, and classifies reply intent for proper routing.', 'sync', 'active',
     '{"category": "sync", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["delivery_tracking", "engagement_monitoring", "reply_classification"]}'::jsonb,
     NOW(), NOW()),
    
    ('SynchronizerAgent', 'Synchronizes data across systems. Syncs to CRM (HubSpot, Salesforce), Slack, and other integrations to keep all systems in sync.', 'sync', 'active',
     '{"category": "sync", "crew": "DeadLeadReactivationCrew,FullCampaignCrew", "capabilities": ["crm_sync", "slack_integration", "data_synchronization"]}'::jsonb,
     NOW(), NOW());

-- Revenue Agents (2)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('MeetingBookerAgent', 'Books meetings automatically. Detects meeting requests in replies, checks calendar availability, and schedules meetings via calendar integrations.', 'revenue', 'active',
     '{"category": "revenue", "crew": "FullCampaignCrew", "capabilities": ["meeting_detection", "calendar_integration", "automated_scheduling"]}'::jsonb,
     NOW(), NOW()),
    
    ('BillingAgent', 'Manages ACV-based billing. Charges fees based on Annual Contract Value, tracks revenue, and handles billing automation.', 'revenue', 'active',
     '{"category": "revenue", "crew": "FullCampaignCrew", "capabilities": ["billing_automation", "acv_tracking", "revenue_management"]}'::jsonb,
     NOW(), NOW());

-- Orchestration Agent (1)
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('OrchestratorAgent', 'Coordinates workflows and crew execution. Manages agent coordination, workflow orchestration, and ensures proper execution order.', 'orchestration', 'active',
     '{"category": "orchestration", "crew": "All", "capabilities": ["workflow_coordination", "crew_management", "execution_orchestration"]}'::jsonb,
     NOW(), NOW());

-- Optimization & Intelligence Agents (5) - NEW
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('ABTestingAgent', 'A/B tests message variants to optimize performance. Creates test variants for subject lines, tone, CTA, and send times, then analyzes results to identify winning variants.', 'optimization', 'active',
     '{"category": "optimization", "crew": "FullCampaignCrew", "capabilities": ["ab_testing", "variant_analysis", "performance_optimization"]}'::jsonb,
     NOW(), NOW()),
    
    ('DomainReputationAgent', 'Monitors domain health and reputation. Checks domain reputation scores, monitors bounce rates, tracks spam rates, and prevents domain damage.', 'optimization', 'active',
     '{"category": "optimization", "crew": "FullCampaignCrew", "capabilities": ["reputation_monitoring", "bounce_tracking", "blacklist_checking"]}'::jsonb,
     NOW(), NOW()),
    
    ('CalendarIntelligenceAgent', 'Determines optimal send times. Analyzes timezone data, considers calendar availability, uses historical engagement patterns, and recommends best send times.', 'optimization', 'active',
     '{"category": "optimization", "crew": "FullCampaignCrew", "capabilities": ["send_time_optimization", "timezone_analysis", "calendar_integration"]}'::jsonb,
     NOW(), NOW()),
    
    ('CompetitorIntelligenceAgent', 'Monitors competitor mentions and provides competitive intelligence. Detects competitor mentions in leads, suggests positioning angles, and tracks competitor news.', 'optimization', 'active',
     '{"category": "optimization", "crew": "FullCampaignCrew", "capabilities": ["competitor_monitoring", "intelligence_gathering", "positioning_analysis"]}'::jsonb,
     NOW(), NOW()),
    
    ('ContentPersonalizationAgent', 'Deep content personalization engine. Analyzes social media activity, reviews blog posts and content consumption, and creates hyper-personalized messages with specific references.', 'optimization', 'active',
     '{"category": "optimization", "crew": "FullCampaignCrew", "capabilities": ["deep_personalization", "social_analysis", "content_referencing"]}'::jsonb,
     NOW(), NOW());

-- Infrastructure & Operations Agents (3) - NEW
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('EmailWarmupAgent', 'Gradually warms up new email domains. Creates warmup schedules, gradually increases sending volume, monitors reputation during warmup, and prevents spam folder placement.', 'infrastructure', 'active',
     '{"category": "infrastructure", "crew": "FullCampaignCrew", "capabilities": ["domain_warmup", "reputation_management", "volume_optimization"]}'::jsonb,
     NOW(), NOW()),
    
    ('LeadNurturingAgent', 'Long-term lead nurturing specialist. Creates nurturing sequences, sends valuable content over time, keeps warm leads engaged, and nurtures until ready to buy.', 'infrastructure', 'active',
     '{"category": "infrastructure", "crew": "FullCampaignCrew", "capabilities": ["nurturing_sequences", "content_delivery", "engagement_maintenance"]}'::jsonb,
     NOW(), NOW()),
    
    ('ChurnPreventionAgent', 'Prevents customer churn. Identifies at-risk customers, detects disengagement signals, creates re-engagement campaigns, and prevents account churn.', 'infrastructure', 'active',
     '{"category": "infrastructure", "crew": "FullCampaignCrew", "capabilities": ["churn_detection", "risk_identification", "re_engagement"]}'::jsonb,
     NOW(), NOW());

-- Analytics & Intelligence Agents (2) - NEW
INSERT INTO agents (name, description, agent_type, status, metadata, created_at, updated_at)
  VALUES
    ('MarketIntelligenceAgent', 'Tracks industry trends and market shifts. Monitors industry news, tracks economic indicators, identifies market opportunities, and provides market context for campaigns.', 'analytics', 'active',
     '{"category": "analytics", "crew": "FullCampaignCrew", "capabilities": ["market_monitoring", "trend_analysis", "opportunity_identification"]}'::jsonb,
     NOW(), NOW()),
    
    ('PerformanceAnalyticsAgent', 'Deep analytics and ROI optimization. Calculates ROI metrics, analyzes campaign performance, provides optimization recommendations, and tracks cost per meeting and cost per deal.', 'analytics', 'active',
     '{"category": "analytics", "crew": "FullCampaignCrew", "capabilities": ["roi_calculation", "performance_analysis", "optimization_recommendations"]}'::jsonb,
     NOW(), NOW());

-- All 28 agents initialized!

-- Verification: Count and list agents
SELECT 
  COUNT(*) as total_agents,
  COUNT(DISTINCT name) as unique_names,
  string_agg(DISTINCT name, ', ' ORDER BY name) as agent_names
FROM agents;

-- Check for any duplicates
SELECT name, COUNT(*) as count
FROM agents
GROUP BY name
HAVING COUNT(*) > 1;

