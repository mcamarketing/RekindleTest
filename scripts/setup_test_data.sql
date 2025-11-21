-- Test Data Setup for E2E Testing
-- Run this in Supabase SQL Editor before running E2E tests

-- Clean up any existing test data
DELETE FROM messages WHERE email LIKE '%e2e%' OR email LIKE '%test%';
DELETE FROM leads WHERE email LIKE '%e2e%' OR email LIKE '%test%';
DELETE FROM billing_records WHERE lead_id IN (
    SELECT id FROM leads WHERE email LIKE '%e2e%' OR email LIKE '%test%'
);

-- Create test user profile (if not exists)
INSERT INTO profiles (id, email, full_name, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'e2e_test@rekindle.ai',
    'E2E Test User',
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Create test lead
INSERT INTO leads (
    id,
    user_id,
    first_name,
    last_name,
    email,
    company,
    industry,
    company_size,
    lead_score,
    status,
    custom_fields,
    created_at
)
VALUES (
    '00000000-0000-0000-0000-000000000100',
    '00000000-0000-0000-0000-000000000001',
    'John',
    'Doe',
    'john.doe.e2e@example.com',
    'Acme Corp',
    'SaaS',
    '50-200',
    75,
    'new',
    '{"acv": 5000, "source": "e2e_test"}'::jsonb,
    NOW()
)
ON CONFLICT (id) DO UPDATE SET
    status = 'new',
    lead_score = 75,
    custom_fields = '{"acv": 5000, "source": "e2e_test"}'::jsonb;

-- Verify test data
SELECT 
    'Test User' as check_type,
    COUNT(*) as count
FROM profiles 
WHERE email = 'e2e_test@rekindle.ai'

UNION ALL

SELECT 
    'Test Leads' as check_type,
    COUNT(*) as count
FROM leads 
WHERE email LIKE '%e2e%' OR email LIKE '%test%';

-- Output: Should show 1 test user and at least 1 test lead








