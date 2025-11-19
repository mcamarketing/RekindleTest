# 🔒 Rekindle.ai - Supabase RLS Policy Documentation

**Version:** 1.0  
**Last Updated:** November 7, 2025  
**SOC 2 Mapping:** Common Criteria 6.1 (Logical Access) & 6.8 (Access Control)

---

## 🎯 **Overview**

Row Level Security (RLS) forms the **core of Rekindle's multi-tenant security architecture**. RLS policies enforce that users can only access their own data, preventing data leakage between customers.

### **Global Security Posture**
- ✅ **RLS ENABLED on ALL public-facing tables**
- ✅ **Default DENY** - No access allowed unless explicitly granted
- ✅ **User-scoped policies** - All data tied to `auth.uid()`
- ✅ **Service role bypass** - Backend agents use service key for admin operations

---

## 📋 **Policy Reference**

### **Table: `profiles`**

**Purpose:** Stores user account info, subscription tier, and billing metadata

#### **Policy 1: Users can read their own profile**
```sql
CREATE POLICY "Users can read own profile"
ON profiles FOR SELECT
TO authenticated
USING (auth.uid() = id);
```

**Rationale:** Allows users to load their dashboard, subscription tier, and billing status.

**Test Query:**
```sql
-- Should return 1 row (your profile)
SELECT * FROM profiles WHERE id = auth.uid();
```

#### **Policy 2: Users can update their own profile**
```sql
CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);
```

**Rationale:** Allows users to update non-critical metadata (name, company, ACV).

**Test Query:**
```sql
-- Should succeed
UPDATE profiles 
SET company = 'New Company Name' 
WHERE id = auth.uid();
```

---

### **Table: `leads`**

**Purpose:** Stores all imported leads. **MOST SENSITIVE DATA.**

#### **Policy 1: Users can read their own leads**
```sql
CREATE POLICY "Users can read own leads"
ON leads FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

**Rationale:** **Core multi-tenant policy.** Ensures users only see leads they imported.

**Security Test:**
```sql
-- Should return 0 rows (can't see other users' leads)
SELECT * FROM leads WHERE user_id != auth.uid();

-- Should return your leads only
SELECT * FROM leads WHERE user_id = auth.uid();
```

#### **Policy 2: Users can insert leads for themselves**
```sql
CREATE POLICY "Users can insert own leads"
ON leads FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);
```

**Rationale:** Allows CSV import and CRM sync, automatically scoping new leads to the authenticated user.

**Test Query:**
```sql
-- Should succeed
INSERT INTO leads (user_id, first_name, last_name, email)
VALUES (auth.uid(), 'John', 'Doe', 'john@example.com');

-- Should FAIL (trying to insert for another user)
INSERT INTO leads (user_id, first_name, last_name, email)
VALUES ('other-user-id', 'Jane', 'Doe', 'jane@example.com');
```

#### **Policy 3: Users can update their own leads**
```sql
CREATE POLICY "Users can update own leads"
ON leads FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

**Rationale:** Allows updating lead status (e.g., `dormant` → `revived`), notes, tags.

**Test Query:**
```sql
-- Should succeed (your lead)
UPDATE leads 
SET status = 'qualified' 
WHERE id = 'your-lead-id' AND user_id = auth.uid();

-- Should FAIL (someone else's lead)
UPDATE leads 
SET status = 'qualified' 
WHERE user_id != auth.uid();
```

#### **Policy 4: Users can delete their own leads**
```sql
CREATE POLICY "Users can delete own leads"
ON leads FOR DELETE
TO authenticated
USING (auth.uid() = user_id);
```

**Rationale:** **Required for GDPR "Right to Erasure" (DSR) compliance.** Users must be able to delete their data.

**Test Query:**
```sql
-- Should succeed
DELETE FROM leads 
WHERE id = 'your-lead-id' AND user_id = auth.uid();

-- Should FAIL
DELETE FROM leads WHERE user_id != auth.uid();
```

---

### **Table: `messages`**

**Purpose:** Stores all AI-generated outreach messages

#### **Policy 1: Users can read messages for their own leads**
```sql
CREATE POLICY "Users can read own messages"
ON messages FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM leads 
    WHERE leads.id = messages.lead_id 
    AND leads.user_id = auth.uid()
  )
);
```

**Rationale:** More complex join-based check. User can only read messages for leads they own.

**Test Query:**
```sql
-- Should return messages for your leads only
SELECT m.* 
FROM messages m
JOIN leads l ON l.id = m.lead_id
WHERE l.user_id = auth.uid();
```

#### **Policy 2-4: No INSERT/UPDATE/DELETE for users**
```sql
-- No policies defined for INSERT/UPDATE/DELETE
-- Only backend service role can modify messages
```

**Rationale:** 
- All messages created by backend CrewAI agents via `SUPABASE_SERVICE_ROLE_KEY`
- Users cannot directly modify messages (maintains **audit trail integrity**)
- Prevents tampering with AI-generated content

---

### **Table: `campaigns`**

**Purpose:** Stores outreach campaigns created by users

#### **Policy 1: Users can read their own campaigns**
```sql
CREATE POLICY "Users can read own campaigns"
ON campaigns FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

#### **Policy 2: Users can insert their own campaigns**
```sql
CREATE POLICY "Users can insert own campaigns"
ON campaigns FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);
```

#### **Policy 3: Users can update their own campaigns**
```sql
CREATE POLICY "Users can update own campaigns"
ON campaigns FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

#### **Policy 4: Users can delete their own campaigns**
```sql
CREATE POLICY "Users can delete own campaigns"
ON campaigns FOR DELETE
TO authenticated
USING (auth.uid() = user_id);
```

---

### **Table: `invoices`** (Hypothetical - Future Implementation)

**Purpose:** Stores billing records and performance fee invoices

#### **Policy 1: Users can read their own invoices**
```sql
CREATE POLICY "Users can read own invoices"
ON invoices FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

**Rationale:** Allows the `/billing` page to display invoice history.

#### **Policy 2-4: No INSERT/UPDATE/DELETE for users**
```sql
-- No policies defined for data modification
-- Only backend Stripe webhook handler can create/update invoices
```

**Rationale:**
- Invoices created automatically by Stripe webhook handler via service key
- Maintains **financial data integrity**
- Prevents users from tampering with billing records

---

## 🔐 **Service Role Bypass**

### **What is the Service Role?**
The **service role key** (`SUPABASE_SERVICE_ROLE_KEY`) **bypasses all RLS policies**. This is used by:
- Backend CrewAI agents (to create messages for any user)
- Stripe webhook handlers (to create invoices)
- Admin dashboards (to view all data for support)

### **Security Best Practices**

#### **✅ DO:**
- Store service key in backend `.env` (NEVER expose to frontend)
- Use service key for admin operations only
- Rotate service key if compromised
- Log all service key usage

#### **❌ DON'T:**
- Expose service key in frontend code
- Commit service key to git
- Share service key via Slack/email
- Use service key for regular user operations

---

## 🧪 **Testing RLS Policies**

### **Manual Testing via Supabase Dashboard**

1. Go to **Supabase Dashboard → SQL Editor**
2. Click **"Run as authenticated user"**
3. Enter a test user ID
4. Run test queries:

```sql
-- Test: Can I see my own leads?
SELECT * FROM leads WHERE user_id = auth.uid();
-- Expected: Returns your leads

-- Test: Can I see other users' leads?
SELECT * FROM leads WHERE user_id != auth.uid();
-- Expected: Returns 0 rows (blocked by RLS)

-- Test: Can I insert a lead for another user?
INSERT INTO leads (user_id, first_name, last_name, email)
VALUES ('other-user-id', 'Test', 'User', 'test@example.com');
-- Expected: ERROR - policy violation
```

### **Automated Testing (Recommended)**

```typescript
// tests/rls-policies.test.ts
import { supabase } from '../lib/supabase';

describe('RLS Policies', () => {
  it('should only return leads for authenticated user', async () => {
    const { data, error } = await supabase
      .from('leads')
      .select('*');
    
    // Verify all leads belong to current user
    const allBelongToUser = data?.every(lead => 
      lead.user_id === (await supabase.auth.getUser()).data.user?.id
    );
    
    expect(allBelongToUser).toBe(true);
  });

  it('should block INSERT for other users', async () => {
    const { error } = await supabase
      .from('leads')
      .insert({
        user_id: 'other-user-id',
        first_name: 'Test',
        last_name: 'User',
        email: 'test@example.com'
      });
    
    expect(error).toBeDefined();
    expect(error?.message).toContain('policy');
  });
});
```

---

## 🚨 **Common RLS Mistakes**

### **Mistake 1: Forgetting to enable RLS**
```sql
-- BAD: RLS not enabled, ALL DATA EXPOSED
CREATE TABLE leads (...);

-- GOOD: RLS enabled by default
CREATE TABLE leads (...);
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
```

### **Mistake 2: Using wrong user check**
```sql
-- BAD: Checks current_user (database role, not auth user)
USING (current_user = user_id);

-- GOOD: Checks authenticated JWT user
USING (auth.uid() = user_id);
```

### **Mistake 3: Missing WITH CHECK on INSERT/UPDATE**
```sql
-- BAD: User could insert data for another user
CREATE POLICY "Insert leads"
ON leads FOR INSERT
TO authenticated;

-- GOOD: Validates user_id matches auth.uid()
CREATE POLICY "Insert leads"
ON leads FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);
```

### **Mistake 4: Overly permissive policy**
```sql
-- BAD: Anyone can read all leads
CREATE POLICY "Read leads"
ON leads FOR SELECT
TO authenticated
USING (true);

-- GOOD: User-scoped access
CREATE POLICY "Read leads"
ON leads FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

---

## 📊 **Monitoring RLS**

### **Sentry Integration**
```typescript
// Catch RLS policy violations
try {
  const { data, error } = await supabase
    .from('leads')
    .select('*');
  
  if (error) {
    Sentry.captureException(error, {
      tags: { 
        table: 'leads',
        operation: 'SELECT',
        error_type: 'rls_violation'
      }
    });
  }
} catch (err) {
  // Handle error
}
```

### **Supabase Logs**
```bash
# View RLS policy violations in Supabase Dashboard
# Go to: Logs → Database Logs
# Filter by: "permission denied"
```

---

## 🔄 **Policy Update Procedure**

### **Before Changing RLS Policies**
1. ✅ Test policy change in **development environment**
2. ✅ Document expected behavior
3. ✅ Create rollback plan
4. ✅ Schedule change during low-traffic window

### **Applying Policy Changes**
```sql
-- 1. Drop old policy
DROP POLICY "old_policy_name" ON leads;

-- 2. Create new policy
CREATE POLICY "new_policy_name"
ON leads FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- 3. Test immediately
SELECT * FROM leads; -- Should work

-- 4. Monitor Sentry for errors
```

### **Rollback Procedure**
```sql
-- If new policy causes issues, rollback immediately
DROP POLICY "new_policy_name" ON leads;

-- Restore old policy (keep this in runbook)
CREATE POLICY "old_policy_name"
ON leads FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

---

## ✅ **SOC 2 Compliance Checklist**

- [x] **CC 6.1:** RLS enabled on all tables containing PII
- [x] **CC 6.8:** User-scoped access control enforced
- [x] **CC 7.2:** Audit logging enabled (Supabase logs)
- [x] **CC 8.1:** Data segregation between customers (multi-tenant)
- [x] **A1.2:** Annual RLS policy review scheduled

**Next Review Date:** November 7, 2026

---

## 📞 **Support**

**Questions about RLS policies?**
- Internal: Slack #devops channel
- Supabase: support@supabase.com
- Documentation: https://supabase.com/docs/guides/auth/row-level-security

---

**Last Updated:** November 7, 2025  
**Author:** DevOps Team  
**Approved By:** CTO

