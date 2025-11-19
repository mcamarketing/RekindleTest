-- Insert test campaign directly into database
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/jnhbmemmwtsrfhlztmyq/sql

-- IMPORTANT: Run this query first to see all users in your database:
-- SELECT id, email, created_at FROM auth.users ORDER BY created_at DESC;

DO $$
DECLARE
  test_user_id uuid;
  test_campaign_id uuid;
  test_lead_id1 uuid;
  test_lead_id2 uuid;
  user_email text;
BEGIN
  -- Get the most recent user from auth.users (should be you!)
  SELECT id, email INTO test_user_id, user_email FROM auth.users ORDER BY created_at DESC LIMIT 1;

  -- Check if user exists
  IF test_user_id IS NULL THEN
    RAISE EXCEPTION 'No users found in auth.users. Please sign up at http://localhost:5174 first!';
  END IF;

  RAISE NOTICE 'Using user: % (ID: %)', user_email, test_user_id;

  -- Create a test campaign
  INSERT INTO campaigns (
    user_id,
    name,
    description,
    status,
    total_leads
  ) VALUES (
    test_user_id,
    'Test Campaign - Q4 Outreach',
    'Testing campaign launch functionality',
    'draft',
    2
  ) RETURNING id INTO test_campaign_id;

  -- Create test leads
  INSERT INTO leads (
    user_id,
    first_name,
    last_name,
    email,
    phone,
    company,
    job_title,
    status
  ) VALUES
  (
    test_user_id,
    'John',
    'Doe',
    'john.doe@example.com',
    '555-0100',
    'Acme Corp',
    'CEO',
    'new'
  ),
  (
    test_user_id,
    'Jane',
    'Smith',
    'jane.smith@techstart.com',
    '555-0101',
    'TechStart Inc',
    'CTO',
    'new'
  );

  -- Get the lead IDs
  SELECT id INTO test_lead_id1 FROM leads WHERE email = 'john.doe@example.com' AND user_id = test_user_id;
  SELECT id INTO test_lead_id2 FROM leads WHERE email = 'jane.smith@techstart.com' AND user_id = test_user_id;

  -- Link leads to campaign
  INSERT INTO campaign_leads (
    campaign_id,
    lead_id,
    status
  ) VALUES
  (
    test_campaign_id,
    test_lead_id1,
    'pending'
  ),
  (
    test_campaign_id,
    test_lead_id2,
    'pending'
  );

  RAISE NOTICE 'Test campaign created successfully!';
  RAISE NOTICE 'Campaign ID: %', test_campaign_id;
  RAISE NOTICE 'User ID: %', test_user_id;
END $$;

-- Verify the campaign was created
SELECT
  c.id,
  c.name,
  c.status,
  c.total_leads,
  u.email as user_email,
  (SELECT COUNT(*) FROM campaign_leads WHERE campaign_id = c.id) as actual_lead_count
FROM campaigns c
JOIN auth.users u ON u.id = c.user_id
ORDER BY c.created_at DESC
LIMIT 5;
