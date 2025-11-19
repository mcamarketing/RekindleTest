-- Quick check to see if agents exist
SELECT id, name, agent_type, status, created_at 
FROM agents 
ORDER BY created_at DESC;

-- Count agents
SELECT COUNT(*) as total_agents FROM agents;





