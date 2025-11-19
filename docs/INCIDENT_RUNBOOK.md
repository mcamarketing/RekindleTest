# 🚨 Rekindle.ai - Incident Runbook

**Version:** 1.0  
**Last Updated:** November 7, 2025  
**Owner:** DevOps Team  
**On-Call Escalation:** See PagerDuty rotation

---

## 📋 **Quick Reference**

| Priority | Response Time | Description |
|----------|---------------|-------------|
| **P1** | < 15 minutes | Complete service outage, data breach |
| **P2** | < 1 hour | Degraded performance, high error rate |
| **P3** | < 4 hours | Feature broken, non-critical issue |

---

## 🔥 **P1: Supabase Unreachable (API/Database Down)**

### **Symptoms**
- ❌ Frontend app fails to load data (Dashboard, Leads)
- ❌ FastAPI server logs show "Connection refused" or 5xx errors from Supabase
- ❌ Sentry floods with "Failed to fetch" or "Database connection error"
- ❌ Users reporting complete inability to access application

### **Validation Steps**

#### **1. Check Supabase Status**
```bash
# Check official status page
open https://status.supabase.com
```

#### **2. Check Supabase Dashboard**
```bash
# Log in to Rekindle Supabase Dashboard
open https://supabase.com/dashboard/project/<PROJECT_ID>

# Navigate to:
# - Database → Health (check CPU/Memory/Connections)
# - API → Logs (check if requests are being received)
```

#### **3. Check Internal Monitoring**
```bash
# Check Sentry for error patterns
open https://sentry.io/organizations/rekindle/issues/

# Check Vercel/Netlify deployment status
open https://vercel.com/rekindle/deployments
```

### **Action Plan (If Supabase Status is "Operational")**

#### **Option 1: Check Project Pausing**
**Issue:** Free tier projects pause after inactivity  
**Solution:**
1. Go to Supabase Dashboard → Project Settings
2. Check if project is "Paused"
3. Click "Resume" if paused
4. **Prevention:** Upgrade to Pro plan ($25/month)

#### **Option 2: Verify API Keys**
**Issue:** Expired or misconfigured credentials  
**Solution:**
```bash
# 1. Get current keys from Supabase Dashboard
# Project Settings → API

# 2. Compare with environment variables
echo $VITE_SUPABASE_URL
echo $VITE_SUPABASE_ANON_KEY

# 3. If mismatched, update .env.production:
# VITE_SUPABASE_URL=https://xxxxx.supabase.co
# VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 4. Redeploy
vercel --prod
```

#### **Option 3: Check RLS Policies**
**Issue:** Bad RLS policy blocks all data access  
**Solution:**
1. Go to Supabase Dashboard → Database → Policies
2. Check recently modified policies (last 24 hours)
3. Identify policy causing issue:
   ```sql
   -- Test if leads are accessible
   SELECT COUNT(*) FROM leads WHERE user_id = 'test-user-id';
   ```
4. Temporarily disable suspicious policy
5. Verify data access restored
6. Fix policy logic and re-enable

#### **Option 4: Restart Connection Pool**
**Issue:** Connection pool saturation  
**Solution:**
```bash
# This is handled automatically by Supabase
# If using custom backend:
# 1. Restart FastAPI/Node services
# 2. Clear connection pool
# 3. Monitor Supabase Dashboard → Database → Connections
```

#### **Option 5: Escalate to Supabase**
**When:** All internal checks pass, Status Page is green, issue persists  
**Action:**
1. Open Supabase Dashboard → Support
2. Include:
   - Project ID
   - Error messages (from Sentry)
   - Timeline of issue
   - Steps already taken
3. Expected Response: < 1 hour (Pro plan)

### **Communication Template**

**Status Page Update:**
```
🔴 INVESTIGATING: Database connectivity issues
We're investigating reports of users unable to access data.
Our team is working on a resolution.

Updates every 15 minutes.
ETA: [TIME]
```

**Resolution Update:**
```
✅ RESOLVED: Database connectivity restored
The issue was caused by [ROOT CAUSE].
All services are now operational.

Post-mortem: [LINK]
```

---

## ⚠️ **P2: High Error Rate (Sentry Alert)**

### **Symptoms**
- 📈 Sentry alert fires: "High volume of new errors"
- 💥 Specific error: `TypeError: Cannot read properties of undefined`
- 📞 User complaints about page crashes (e.g., Billing page)

### **Triage Steps**

#### **1. Identify Blast Radius**
```bash
# Open Sentry
open https://sentry.io/organizations/rekindle/issues/

# Answer these questions:
# - What page/component is failing? (e.g., Billing.tsx)
# - How many users affected? (1 user vs. all users)
# - What error type? (TypeError, NetworkError, etc.)
# - When did it start? (correlate with deploy time)
```

#### **2. Correlate with Deployment**
```bash
# Check Vercel deployment logs
vercel logs --since=1h

# Compare error start time with deploy time
# If within 5 minutes = likely deploy-related
```

### **Action Plan**

#### **Scenario 1: Error Correlated with Deployment**
**Action: IMMEDIATE ROLLBACK**

```bash
# Vercel rollback (instant)
vercel rollback

# Or via dashboard:
# 1. Go to Vercel Dashboard → Deployments
# 2. Find last stable deployment
# 3. Click "..." → "Promote to Production"
# 4. Confirm rollback

# Expected resolution: < 1 minute
```

#### **Scenario 2: Frontend State Management Error**
**Common Issue:** Undefined property access

```typescript
// BAD (causes error if user is null)
const name = user.name;

// GOOD (safe access)
const name = user?.name ?? 'Unknown';
```

**Fix Process:**
1. Identify failing component in Sentry stack trace
2. Add defensive checks (`?.` optional chaining)
3. Test in development
4. Deploy fix

#### **Scenario 3: Backend 500 Error**
**Common Issue:** Unhandled exception in API

```bash
# Check FastAPI logs (if applicable)
# or Supabase Function logs

# Find error trace
# Fix error handling
# Redeploy backend
```

### **Post-Resolution**

#### **Root Cause Analysis Template**
```markdown
## Incident Post-Mortem

**Date:** [DATE]  
**Duration:** [START TIME] - [END TIME]  
**Severity:** P2

### What Happened
[Brief description]

### Root Cause
[Technical cause]

### Impact
- Users affected: [NUMBER]
- Pages affected: [PAGES]
- Revenue impact: [£ AMOUNT]

### Resolution
[What fixed it]

### Prevention
- [ ] Add unit test for this scenario
- [ ] Add error boundary
- [ ] Update deployment checklist
```

---

## 🔧 **P3: OAuth Token Exchange Fails (Calendar Integration)**

### **Symptoms**
- 📅 "Connect Calendar" popup shows error or spins forever
- 🔐 FastAPI logs show `OAUTH_CALLBACK_ERROR`
- ❌ Error: "Invalid credentials" or "Redirect URI mismatch"

### **Validation Steps**

#### **1. Check MCP Server Status**
```bash
# Verify Calendar MCP server is running
curl https://your-mcp-server.com/health

# Expected response: {"status": "healthy"}
```

#### **2. Check OAuth Configuration**

**For Google Calendar:**
```bash
# 1. Go to Google Cloud Console
open https://console.cloud.google.com/apis/credentials

# 2. Verify:
# - Client ID matches VITE_GOOGLE_CLIENT_ID
# - Client Secret matches (in backend .env)
# - Authorized redirect URIs include:
#   https://rekindle.ai/api/oauth/callback
```

**For Outlook Calendar:**
```bash
# 1. Go to Azure Portal
open https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps

# 2. Verify same settings as above
```

### **Action Plan**

#### **Fix 1: Update Redirect URI**
**Issue:** Mismatch between app config and OAuth provider

```bash
# 1. Check current redirect URI in code
grep -r "REDIRECT_URI" src/

# 2. Update OAuth provider console to match
# 3. Wait 5 minutes for changes to propagate
# 4. Test OAuth flow again
```

#### **Fix 2: Regenerate Client Secret**
**Issue:** Client secret expired or rotated

```bash
# 1. Generate new secret in OAuth provider console
# 2. Update backend .env:
# GOOGLE_CLIENT_SECRET=new_secret_here

# 3. Restart backend service
# 4. Test OAuth flow
```

#### **Fix 3: Check Scopes**
**Issue:** Missing calendar permissions

```typescript
// Required scopes for Google Calendar
const SCOPES = [
  'https://www.googleapis.com/auth/calendar.readonly',
  'https://www.googleapis.com/auth/calendar.events',
];

// Verify these match OAuth provider console
```

---

## 📞 **Escalation Contacts**

### **Internal Team**
- **Primary On-Call:** Check PagerDuty
- **Backup On-Call:** Check PagerDuty
- **CTO:** [EMAIL]

### **External Vendors**
- **Supabase Support:** support@supabase.com (Pro plan: < 1 hour response)
- **Vercel Support:** support@vercel.com (Enterprise plan: < 30 min response)
- **Sentry Support:** support@sentry.io

---

## 🛠️ **Useful Commands**

### **Check Application Health**
```bash
# Frontend health
curl https://rekindle.ai/

# Backend health (if applicable)
curl https://api.rekindle.ai/health

# Supabase health
curl https://xxxxx.supabase.co/rest/v1/
```

### **View Real-Time Logs**
```bash
# Vercel logs
vercel logs --follow

# Sentry events
# Visit: https://sentry.io/organizations/rekindle/issues/
```

### **Quick Rollback**
```bash
# Vercel
vercel rollback

# Or via URL
open https://vercel.com/rekindle/deployments
```

---

## 📚 **Additional Resources**

- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [Sentry Error Tracking](https://docs.sentry.io/)
- [RLS Policy Documentation](./RLS_POLICIES.md)

---

**Last Reviewed:** November 7, 2025  
**Next Review Date:** December 7, 2025

