-- Remove duplicate agents, keeping only the first one (by created_at)
-- This will keep the oldest agent for each name and delete the rest

DELETE FROM agents
WHERE id NOT IN (
  SELECT DISTINCT ON (name) id
  FROM agents
  ORDER BY name, created_at ASC
);

-- Alternative method if the above doesn't work:
-- DELETE FROM agents a1
-- USING agents a2
-- WHERE a1.name = a2.name
--   AND a1.created_at > a2.created_at;

-- Verify you now have 28 unique agents
SELECT 
  COUNT(*) as total_agents,
  COUNT(DISTINCT name) as unique_names
FROM agents;

-- List all agents to verify
SELECT name, COUNT(*) as count
FROM agents
GROUP BY name
HAVING COUNT(*) > 1;








