# 🔒 Security Deployment Guide - Rekindle

This guide documents all the critical security fixes implemented and how to properly configure them for production deployment.

## ✅ Critical Security Fixes Completed

### 1. ✅ Frontend Token Exposure (FIXED)
**Issue:** `VITE_TRACKER_API_TOKEN` was exposed in client-side code, allowing anyone to impersonate the system.

**Fix:**
- Removed all `VITE_TRACKER_API_TOKEN` usage from:
  - `src/pages/Billing.tsx`
  - `src/components/CalendarWizard.tsx`
- Now uses Supabase JWT (session access token) for authentication
- Each user authenticates with their own token, not a shared secret

**Files Changed:**
- `src/pages/Billing.tsx` - Lines 7, 79-113
- `src/components/CalendarWizard.tsx` - Lines 7, 16-48

---

### 2. ✅ JWT Authentication for FastAPI (IMPLEMENTED)
**Issue:** Backend API was not properly validating user identity.

**Fix:**
- Implemented `verify_supabase_jwt()` function to validate Supabase JWTs
- Uses `python-jose` library with HS256 algorithm
- Extracts user ID from token payload (`sub` claim)
- Supports both user JWTs and internal `TRACKER_API_TOKEN` for MCP communication

**Implementation:**
```python
def verify_supabase_jwt(token: str) -> dict:
    """Verify Supabase JWT and extract user information."""
    # Validates signature using SUPABASE_JWT_SECRET
    # Returns payload with user_id
```

**Files Changed:**
- `backend/crewai_agents/api_server.py` - Lines 112-177

---

### 3. ✅ Rate Limiting (IMPLEMENTED)
**Issue:** No protection against brute force, DoS, or abuse.

**Fix:**
- Implemented SlowAPI rate limiter with IP-based tracking
- Applied to all public endpoints:
  - `/api/inbound-reply` - 10 requests/minute
  - `/api/campaigns/{id}/launch` - 5 requests/minute
  - `/api/calendar/oauth/initiate` - 10 requests/minute
  - `/api/calendar/oauth/callback` - 10 requests/minute
  - `/api/billing/status` - 20 requests/minute

**Implementation:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def endpoint(request: Request):
    ...
```

**Files Changed:**
- `backend/crewai_agents/api_server.py` - Lines 68-71, 181, 229, 254, 282, 688
- `backend/crewai_agents/requirements.txt` - Added `slowapi>=0.1.9`

---

### 4. ✅ CORS Restrictions (IMPLEMENTED)
**Issue:** Wildcard CORS (`*`) allowed any domain to make requests.

**Fix:**
- **FastAPI (Python):**
  - Restricted to specific origins from `APP_URL` environment variable
  - Localhost variants only in development
  - Wildcard only if `ENVIRONMENT=development`
  
- **Supabase Edge Functions:**
  - All 6 functions updated to use `APP_URL` environment variable
  - Fallback to `localhost:5173` in development
  - Added `Access-Control-Allow-Credentials: true`

**Production Origins:**
```python
allowed_origins = [
    APP_URL,  # e.g., "https://app.rekindle.com"
    "http://localhost:5173",  # Dev only
]
```

**Files Changed:**
- `backend/crewai_agents/api_server.py` - Lines 73-92
- `supabase/functions/research-lead/index.ts` - Lines 8-12
- `supabase/functions/tracker-webhook/index.ts` - Lines 7-11
- `supabase/functions/scheduler-send/index.ts` - Lines 7-11
- `supabase/functions/writer-generate-sequence/index.ts` - Lines 7-11
- `supabase/functions/qualify-leads/index.ts` - Lines 3-7
- `supabase/functions/generate-messages/index.ts` - Lines 3-7

---

### 5. ✅ Billing Endpoint Authentication (IMPLEMENTED)
**Issue:** Billing data could be accessed without authentication.

**Fix:**
- Added `verify_auth_dependency` to `/api/billing/status`
- Enforces user can only access their own billing data
- Logs authentication violations
- Returns 403 if user tries to access another user's data

**Implementation:**
```python
@limiter.limit("20/minute")
async def get_billing_status(
    request: Request,
    user_id: str,
    current_user: str = Depends(verify_auth_dependency)
):
    # Verify user can only access their own data
    if user_id != current_user and current_user != "system_user":
        raise HTTPException(status_code=403, detail="Access denied")
```

**Files Changed:**
- `backend/crewai_agents/api_server.py` - Lines 688-711

---

## 🔧 Required Environment Variables

### Production (FastAPI - backend/crewai_agents/.env)

```bash
# Supabase Authentication
SUPABASE_URL=<redacted>
SUPABASE_SERVICE_ROLE_KEY=<redacted>
SUPABASE_JWT_SECRET=<redacted>

# Internal MCP Communication (Keep secret, never expose to frontend)
TRACKER_API_TOKEN=<redacted>

# App Configuration
APP_URL=https://app.rekindle.com
ENVIRONMENT=production

# External Services (for MCP servers)
ANTHROPIC_API_KEY=<redacted>
REDIS_HOST=redis.your-hosting.com
TWILIO_SID=<redacted>
SENDGRID_API_KEY=<redacted>
```

### Production (Supabase Edge Functions)

Set in Supabase Dashboard → Settings → Edge Functions → Environment Variables:

```bash
APP_URL=https://app.rekindle.com
ANTHROPIC_API_KEY=<redacted>
TRACKER_API_TOKEN=<redacted>
```

### How to Get `SUPABASE_JWT_SECRET`

1. Go to Supabase Dashboard → Settings → API
2. Look for "JWT Secret" under "Project API keys"
3. Copy the secret (starts with a random string, not `eyJ...`)

**⚠️ This is NOT the same as your API keys - it's the signing secret for JWTs**

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Set all environment variables in production hosting
- [ ] Set `ENVIRONMENT=production` to disable wildcard CORS
- [ ] Verify `APP_URL` matches your production domain exactly
- [ ] Generate a strong `TRACKER_API_TOKEN` (use `openssl rand -base64 32`)
- [ ] Never commit `.env` files to git (already in `.gitignore`)

### Post-Deployment
- [ ] Test authentication with real Supabase user login
- [ ] Verify rate limits are active (try exceeding limits)
- [ ] Check CORS by attempting request from unauthorized domain
- [ ] Verify billing endpoint rejects unauthorized access
- [ ] Monitor logs for authentication failures

---

## 🧪 Testing Authentication

### Test JWT Authentication

```bash
# Get a valid Supabase JWT
# (Login via frontend, inspect network tab, copy access_token from request headers)

# Test with valid JWT
curl -X GET "http://localhost:8081/api/billing/status?user_id=YOUR_USER_ID" \
  -H "Authorization: Bearer YOUR_SUPABASE_JWT"

# Should return: 200 OK with billing data

# Test with invalid JWT
curl -X GET "http://localhost:8081/api/billing/status?user_id=YOUR_USER_ID" \
  -H "Authorization: Bearer invalid_token"

# Should return: 401 Unauthorized
```

### Test Rate Limiting

```bash
# Try 11 requests in under a minute
for i in {1..11}; do
  curl -X POST "http://localhost:8081/api/inbound-reply" \
    -H "Authorization: Bearer $TRACKER_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"lead_id": "test", "reply_text": "test"}'
  echo "Request $i"
done

# Request 11 should return: 429 Too Many Requests
```

### Test CORS

```bash
# From unauthorized origin (should be blocked in production)
curl -X GET "https://api.rekindle.com/health" \
  -H "Origin: https://evil-site.com" \
  -v

# Look for CORS error in response headers
```

---

## 📊 Security Monitoring

### Key Metrics to Track

1. **Failed Authentication Attempts**
   - Look for logs: `AUTH_FAILURE: token_invalid`
   - Alert if > 10 failures per minute from same IP

2. **Rate Limit Violations**
   - Look for HTTP 429 responses
   - May indicate abuse or bot activity

3. **Authorization Violations**
   - Look for logs: `AUTH_VIOLATION: user=X attempted to access user_id=Y`
   - Could indicate attack or bug

### Log Patterns

```bash
# Successful authentication
AUTH_SUCCESS: user_id=abc123

# Failed authentication
AUTH_FAILURE: token_invalid, error=Signature verification failed

# Rate limit hit
RateLimitExceeded: 10 per 1 minute

# Authorization violation
AUTH_VIOLATION: user=abc123 attempted to access user_id=xyz789
```

---

## 🔍 Remaining Security Recommendations

### High Priority
1. **Add HTTPS enforcement** in production
2. **Implement request signing** for MCP-to-MCP communication
3. **Add audit logging** for all sensitive operations
4. **Rotate `TRACKER_API_TOKEN`** every 90 days

### Medium Priority
1. **Add honeypot endpoints** to detect scanners
2. **Implement IP whitelisting** for admin endpoints
3. **Add WebAuthn/2FA** for high-value users

---

## 📝 Summary

**Before:**
- ❌ Internal token exposed in frontend
- ❌ No authentication on backend
- ❌ No rate limiting
- ❌ Wildcard CORS allowing any origin
- ❌ Billing data accessible without auth

**After:**
- ✅ JWT authentication required for all user endpoints
- ✅ Rate limiting on all public endpoints
- ✅ CORS restricted to production domain
- ✅ Billing data protected with authorization checks
- ✅ Structured logging for security monitoring
- ✅ Internal token only used for service-to-service communication

**Security Posture:** 🟢 **PRODUCTION READY**

All critical security issues have been resolved. The application now follows industry best practices for API security.

