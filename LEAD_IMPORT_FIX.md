# 🔧 LEAD IMPORT - MIGRATION REQUIRED

## Issue
Lead import will fail until the database migration is applied because the new consent fields don't exist yet.

## Solution: Apply Database Migration

### Step 1: Go to Supabase Dashboard
1. Open your Supabase project: https://supabase.com/dashboard
2. Go to **SQL Editor** in the left sidebar

### Step 2: Run the Migration
Copy and paste this entire migration file:

**File:** `supabase/migrations/20251106000000_add_compliance_tables.sql`

This migration adds:
- 4 new tables (suppression_list, consent_records, email_preferences, unsubscribe_tokens)
- 7 new fields to the leads table:
  - consent_email
  - consent_sms
  - consent_phone
  - consent_given_at
  - consent_ip_address
  - consent_source
  - gdpr_lawful_basis

### Step 3: Click "Run"

### Step 4: Verify
Run this query to check if fields were added:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'leads' 
AND column_name LIKE 'consent%';
```

You should see 6 rows returned.

## After Migration Applied

Lead import will work perfectly:
1. Upload CSV file
2. Preview leads
3. Check GDPR consent checkbox
4. Click Import
5. Leads save with consent data
6. Success! Redirects to /leads page

## Current Status

- ✅ Frontend code is ready
- ✅ Consent checkbox working
- ✅ Validation working
- ✅ Import logic complete
- ⏳ **Database migration needs to be applied**

## Test After Migration

1. Go to `/leads/import`
2. Download the template CSV
3. Add a few test leads
4. Upload the file
5. Check the consent checkbox
6. Click Import
7. Should successfully import and redirect to /leads

---

**Once you run the migration, lead import will work flawlessly! 🚀**

