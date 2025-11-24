-- =====================================================
-- CREATE AGENTS TABLE AND RELATED TABLES
-- =====================================================
-- This script creates the agents table and related tables for AI agent monitoring

-- Create agents table
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

-- Create agent_metrics table
CREATE TABLE IF NOT EXISTS agent_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  
  -- Performance Metrics
  cpu_usage numeric(5,2) DEFAULT 0 CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
  memory_usage numeric(5,2) DEFAULT 0 CHECK (memory_usage >= 0 AND memory_usage <= 100),
  response_time numeric(10,2) DEFAULT 0, -- milliseconds
  
  -- Task Metrics
  completed_tasks integer DEFAULT 0,
  failed_tasks integer DEFAULT 0,
  error_count integer DEFAULT 0,
  
  -- Timestamps
  recorded_at timestamptz DEFAULT now()
);

-- Create agent_tasks table
CREATE TABLE IF NOT EXISTS agent_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Task Information
  task_type text NOT NULL,
  task_data jsonb DEFAULT '{}',
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
  
  -- Results
  result_data jsonb DEFAULT '{}',
  error_message text,
  
  -- Timestamps
  created_at timestamptz DEFAULT now(),
  started_at timestamptz,
  completed_at timestamptz
);

-- Create agent_logs table
CREATE TABLE IF NOT EXISTS agent_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  
  -- Log Information
  log_level text NOT NULL CHECK (log_level IN ('debug', 'info', 'warning', 'error', 'critical')),
  message text NOT NULL,
  context jsonb DEFAULT '{}',
  
  -- Timestamps
  created_at timestamptz DEFAULT now()
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Agents policies (system-wide agents visible to all, user-specific agents private)
CREATE POLICY "Users can view all agents" ON agents FOR SELECT USING (true);
CREATE POLICY "Users can view own agent tasks" ON agents FOR SELECT USING (user_id IS NULL OR user_id = auth.uid());
CREATE POLICY "Service role can manage agents" ON agents FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Agent metrics policies
CREATE POLICY "Users can view agent metrics" ON agent_metrics FOR SELECT USING (true);
CREATE POLICY "Service role can insert metrics" ON agent_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Agent tasks policies
CREATE POLICY "Users can view own tasks" ON agent_tasks FOR SELECT USING (user_id = auth.uid() OR user_id IS NULL);
CREATE POLICY "Users can create own tasks" ON agent_tasks FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Service role can manage tasks" ON agent_tasks FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Agent logs policies
CREATE POLICY "Users can view agent logs" ON agent_logs FOR SELECT USING (true);
CREATE POLICY "Service role can insert logs" ON agent_logs FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_created_at ON agents(created_at DESC);

CREATE INDEX idx_agent_metrics_agent_id ON agent_metrics(agent_id);
CREATE INDEX idx_agent_metrics_recorded_at ON agent_metrics(recorded_at DESC);

CREATE INDEX idx_agent_tasks_agent_id ON agent_tasks(agent_id);
CREATE INDEX idx_agent_tasks_user_id ON agent_tasks(user_id);
CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_created_at ON agent_tasks(created_at DESC);

CREATE INDEX idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX idx_agent_logs_log_level ON agent_logs(log_level);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at DESC);

-- =====================================================
-- TRIGGER FOR updated_at
-- =====================================================

CREATE TRIGGER update_agents_updated_at 
  BEFORE UPDATE ON agents 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();








