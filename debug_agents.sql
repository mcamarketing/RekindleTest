-- Debug script to check agents
-- Run this in Supabase SQL Editor to see what's happening

-- 1. Check if table exists
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'agents'
) as table_exists;

-- 2. Count agents
SELECT COUNT(*) as total_agents FROM agents;

-- 3. Check RLS policies
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies 
WHERE tablename = 'agents';

-- 4. List all agents (if any)
SELECT id, name, agent_type, status, created_at 
FROM agents 
ORDER BY name
LIMIT 10;

-- 5. Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'agents';





