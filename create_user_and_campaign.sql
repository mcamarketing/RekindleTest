-- Create user and test campaign directly
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/jnhbmemmwtsrfhlztmyq/sql

DO $$
DECLARE
  test_user_id uuid;
  test_campaign_id uuid;
  test_lead_id1 uuid;
  test_lead_id2 uuid;
BEGIN
  -- Create a test user directly (bypassing email confirmation)
  INSERT INTO auth.users (
    instance_id,
    id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    raw_app_meta_data,
    raw_user_meta_data,
    created_at,
    updated_at,
    confirmation_token,
    email_change,
    email_change_token_new,
    recovery_token
  ) VALUES (
    '00000000-0000-0000-0000-000000000000',
    gen_random_uuid(),
    'authenticated',
    'authenticated',
    'test@example.com',
    crypt('password123', gen_salt('bf')),
    NOW(),
    '{"provider":"email","providers":["email"]}',
    '{}',
    NOW(),
    NOW(),
    '',
    '',
    '',
    ''
  ) RETURNING id INTO test_user_id;

  RAISE NOTICE 'Created user: test@example.com (ID: %)', test_user_id;

  -- Also create identity for the user
  INSERT INTO auth.identities (
    id,
    user_id,
    identity_data,
    provider,
    provider_id,
    last_sign_in_at,
    created_at,
    updated_at
  ) VALUES (
    gen_random_uuid(),
    test_user_id,
    jsonb_build_object('sub', test_user_id::text, 'email', 'test@example.com'),
    'email',
    test_user_id::text,
    NOW(),
    NOW(),
    NOW()
  );

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
  RAISE NOTICE '';
  RAISE NOTICE 'Login credentials:';
  RAISE NOTICE 'Email: test@example.com';
  RAISE NOTICE 'Password: password123';
END $$;

-- Verify everything was created
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
