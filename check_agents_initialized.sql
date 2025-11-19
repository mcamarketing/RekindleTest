-- Quick check to see if agents are initialized
SELECT 
  COUNT(*) as total_agents,
  COUNT(CASE WHEN status = 'active' THEN 1 END) as active_agents,
  COUNT(CASE WHEN last_heartbeat > NOW() - INTERVAL '5 minutes' THEN 1 END) as recent_heartbeat
FROM agents;

-- List all agents
SELECT id, name, agent_type, status, last_heartbeat, created_at
FROM agents
ORDER BY name;





