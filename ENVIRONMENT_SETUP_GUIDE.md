# Environment Setup Guide - Phase 0

**Generated:** November 17, 2025
**Purpose:** Step-by-step guide to configure environment variables for development and production

---

## 🔑 Generated Keys (Ready to Use)

I've generated these keys for you. **Copy them to your `.env` files:**

```bash
# Calendar OAuth Token Encryption (Phase 0 Fix #5)
CALENDAR_ENCRYPTION_KEY=CChwG6fXLoH6DczAfDVaYc4k1VklM4sMy2aKCkqi6y8=

# JWT Authentication Secret
JWT_SECRET=oJxue8trw8YEYmDD1oSYamQqhf7J6evmllWjt64UArnJZk7HUU1pgZ0E335FlffRPgrUGddRHHRmFUp8o4QZyQ
```

⚠️ **SECURITY WARNING:** These are real keys. Never commit them to git!

---

## 📋 Step 1: Frontend Setup (.env.local)

### Create the file:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
cp .env.example .env.local
```

### Edit `.env.local` with these values:

```bash
# =============================================================================
# REKINDLE Frontend Environment Variables
# =============================================================================

# Supabase Configuration (Phase 0 Fix #1)
VITE_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...YOUR_ANON_KEY_HERE

# API Configuration (Phase 0 Fix #2)
VITE_API_URL=http://localhost:3001/api
```

### Where to get Supabase credentials:

1. **Go to:** https://app.supabase.com/project/_/settings/api
2. **Copy "Project URL"** → `VITE_SUPABASE_URL`
   - Should look like: `https://abcdefg123456.supabase.co`
3. **Copy "anon public" key** → `VITE_SUPABASE_ANON_KEY`
   - Should start with: `eyJ`
   - ⚠️ **DO NOT use "service_role" key** - that's for backend only!

### Verify frontend setup:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
npm run build
```

**Expected output:**
```
✓ built in XXXms
```

**If you see errors:**
- ❌ "Missing required Supabase environment variables" → Check `.env.local` exists and has both variables
- ❌ "Invalid Supabase URL format" → URL must start with `https://` and include `.supabase.co`
- ❌ "Invalid Supabase anon key format" → Key must start with `eyJ`

---

## 📋 Step 2: Backend Setup (.env)

### Create the file:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
cp .env.example .env
```

### Edit `.env` with these values:

```bash
# =============================================================================
# REKINDLE Backend Environment Variables
# =============================================================================

# =============================================================================
# REQUIRED - Supabase
# =============================================================================
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_JWT_SECRET=YOUR_JWT_SECRET_FROM_SUPABASE

# =============================================================================
# REQUIRED - AI
# =============================================================================
ANTHROPIC_API_KEY=sk-ant-...YOUR_ANTHROPIC_KEY
OPENAI_API_KEY=sk-...YOUR_OPENAI_KEY

# =============================================================================
# REQUIRED - Email (SendGrid)
# =============================================================================
SENDGRID_API_KEY=SG...YOUR_SENDGRID_KEY
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=Rekindle AI
SENDGRID_WEBHOOK_VERIFICATION_KEY=YOUR_WEBHOOK_VERIFICATION_KEY

# =============================================================================
# REQUIRED - SMS (Twilio)
# =============================================================================
TWILIO_ACCOUNT_SID=AC...YOUR_ACCOUNT_SID
TWILIO_AUTH_TOKEN=...YOUR_AUTH_TOKEN
TWILIO_PHONE_NUMBER=+1234567890

# =============================================================================
# REQUIRED - Billing (Stripe)
# =============================================================================
STRIPE_SECRET_KEY=sk_test_...YOUR_STRIPE_KEY
STRIPE_WEBHOOK_SECRET=whsec_...YOUR_WEBHOOK_SECRET

# =============================================================================
# REQUIRED - Authentication & Encryption (GENERATED FOR YOU)
# =============================================================================
JWT_SECRET=oJxue8trw8YEYmDD1oSYamQqhf7J6evmllWjt64UArnJZk7HUU1pgZ0E335FlffRPgrUGddRHHRmFUp8o4QZyQ
CALENDAR_ENCRYPTION_KEY=CChwG6fXLoH6DczAfDVaYc4k1VklM4sMy2aKCkqi6y8=

# =============================================================================
# OPTIONAL - Server Configuration
# =============================================================================
PORT=8081
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
APP_URL=http://localhost:8081

# =============================================================================
# OPTIONAL - Calendar OAuth (if using calendar features)
# =============================================================================
# GOOGLE_CALENDAR_CLIENT_ID=...
# GOOGLE_CALENDAR_CLIENT_SECRET=...
# GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8081/calendar/callback

# MICROSOFT_CALENDAR_CLIENT_ID=...
# MICROSOFT_CALENDAR_CLIENT_SECRET=...
# MICROSOFT_CALENDAR_REDIRECT_URI=http://localhost:8081/calendar/callback

# =============================================================================
# OPTIONAL - Monitoring
# =============================================================================
# SENTRY_DSN=https://...@sentry.io/...
# SENTRY_ENVIRONMENT=development

# =============================================================================
# OPTIONAL - Redis
# =============================================================================
# REDIS_HOST=127.0.0.1
# REDIS_PORT=6379
```

---

## 🔍 Where to Get Each Backend Variable

### Supabase (3 variables)
1. **Go to:** https://app.supabase.com/project/_/settings/api
2. **Project URL** → `SUPABASE_URL`
3. **service_role secret key** → `SUPABASE_SERVICE_ROLE_KEY`
   - ⚠️ This bypasses RLS - keep it secret!
4. **JWT Secret** → `SUPABASE_JWT_SECRET`
   - Found in same page under "JWT Settings"

### Anthropic (1 variable)
1. **Go to:** https://console.anthropic.com/settings/keys
2. **Create API key** → `ANTHROPIC_API_KEY`
   - Should start with: `sk-ant-`

### OpenAI (1 variable)
1. **Go to:** https://platform.openai.com/api-keys
2. **Create new key** → `OPENAI_API_KEY`
   - Should start with: `sk-`
   - ⚠️ **CRITICAL:** Agents won't work without this!

### SendGrid (3 variables)
1. **API Key:**
   - Go to: https://app.sendgrid.com/settings/api_keys
   - Create key with "Mail Send" permissions → `SENDGRID_API_KEY`
   - Should start with: `SG.`

2. **From Email:**
   - Go to: https://app.sendgrid.com/settings/sender_auth
   - Verify sender domain → `SENDGRID_FROM_EMAIL`
   - Example: `noreply@yourdomain.com`

3. **Webhook Verification Key (NEW - Phase 0 Fix #4):**
   - Go to: https://app.sendgrid.com/settings/mail_settings
   - Click "Event Webhook"
   - Enable webhook and copy "Verification Key" → `SENDGRID_WEBHOOK_VERIFICATION_KEY`
   - ⚠️ **REQUIRED:** Prevents webhook spoofing attacks

### Twilio (3 variables)
1. **Go to:** https://console.twilio.com
2. **Account SID** → `TWILIO_ACCOUNT_SID`
   - Should start with: `AC`
3. **Auth Token** → `TWILIO_AUTH_TOKEN`
4. **Phone Number:**
   - Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
   - Buy a number → `TWILIO_PHONE_NUMBER`
   - Format: `+1234567890`

### Stripe (2 variables)
1. **Secret Key:**
   - Go to: https://dashboard.stripe.com/apikeys
   - Copy "Secret key" → `STRIPE_SECRET_KEY`
   - Should start with: `sk_test_` (test) or `sk_live_` (production)

2. **Webhook Secret:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Create webhook endpoint
   - Copy "Signing secret" → `STRIPE_WEBHOOK_SECRET`
   - Should start with: `whsec_`

### Generated Keys (ALREADY DONE ✅)
- `JWT_SECRET` - Already generated above
- `CALENDAR_ENCRYPTION_KEY` - Already generated above

---

## ✅ Step 3: Verify Setup

### Verify backend environment:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
python scripts/verify_env.py
```

**Expected output:**
```
✅ P0 Variables: 14/14 configured (100%)
✅ READY TO DEPLOY
```

**If you see errors:**
- Look for specific variable names marked as ❌ MISSING
- Check that you copied the values correctly
- Ensure no extra spaces or quotes

### Test encryption setup:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
python -c "from utils.token_encryption import validate_encryption_setup; validate_encryption_setup(); print('✅ Encryption OK')"
```

### Test database connection:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
python -c "from utils.database import SupabaseDB; db = SupabaseDB(); result = db.supabase.table('profiles').select('id').limit(1).execute(); print('✅ Database OK' if result.data is not None else '❌ Database FAILED')"
```

### Run smoke tests:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
pytest tests/test_phase0_fixes.py -v
```

**Expected output:**
```
test_phase0_fixes.py::TestOAuthTokenEncryption::test_encrypt_token_success PASSED
test_phase0_fixes.py::TestOAuthTokenEncryption::test_decrypt_token_success PASSED
test_phase0_fixes.py::TestOAuthTokenEncryption::test_encryption_roundtrip PASSED
...
============= 15 passed in X.XXs =============
```

---

## 🚀 Step 4: Start the Application

### Start backend:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend\crewai_agents
python api_server.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8081
```

### Start frontend (in new terminal):
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Test the application:
1. Open browser: http://localhost:5173
2. You should see the Rekindle dashboard
3. Try logging in or creating an account

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] `.env` and `.env.local` are in `.gitignore`
- [ ] Never committed `.env` files to git
- [ ] Used `service_role` key only in backend
- [ ] Used `anon` key only in frontend
- [ ] Different credentials for dev/staging/prod
- [ ] All P0 variables configured
- [ ] Encryption key is Fernet-generated (not token_urlsafe)
- [ ] Webhook verification keys configured
- [ ] All tests passing

---

## 📊 Environment Variable Summary

| Variable | Required | Where Used | Got It? |
|----------|----------|------------|---------|
| **Frontend (3)** |
| VITE_SUPABASE_URL | ✅ Yes | Frontend | ☐ |
| VITE_SUPABASE_ANON_KEY | ✅ Yes | Frontend | ☐ |
| VITE_API_URL | ⚠️ Prod only | Frontend | ☐ |
| **Backend (14)** |
| SUPABASE_URL | ✅ Yes | Backend | ☐ |
| SUPABASE_SERVICE_ROLE_KEY | ✅ Yes | Backend | ☐ |
| SUPABASE_JWT_SECRET | ✅ Yes | Backend | ☐ |
| ANTHROPIC_API_KEY | ✅ Yes | Backend | ☐ |
| OPENAI_API_KEY | ✅ Yes | Backend | ☐ |
| SENDGRID_API_KEY | ✅ Yes | Backend | ☐ |
| SENDGRID_FROM_EMAIL | ✅ Yes | Backend | ☐ |
| SENDGRID_WEBHOOK_VERIFICATION_KEY | ✅ Yes | Backend | ☐ |
| TWILIO_ACCOUNT_SID | ✅ Yes | Backend | ☐ |
| TWILIO_AUTH_TOKEN | ✅ Yes | Backend | ☐ |
| TWILIO_PHONE_NUMBER | ✅ Yes | Backend | ☐ |
| STRIPE_SECRET_KEY | ✅ Yes | Backend | ☐ |
| JWT_SECRET | ✅ Yes | Backend | ✅ Generated |
| CALENDAR_ENCRYPTION_KEY | ✅ Yes | Backend | ✅ Generated |

**Total Required:** 17 variables (14 backend + 3 frontend)
**Already Generated:** 2 (JWT_SECRET, CALENDAR_ENCRYPTION_KEY)
**Need to Obtain:** 15

---

## 🆘 Troubleshooting

### Frontend won't build
```bash
# Error: Missing required Supabase environment variables
# Solution: Create .env.local and add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY

# Error: Invalid Supabase URL format
# Solution: Ensure URL starts with https:// and includes .supabase.co

# Error: Invalid Supabase anon key format
# Solution: Ensure key starts with eyJ (it's a JWT)
```

### Backend won't start
```bash
# Error: CALENDAR_ENCRYPTION_KEY environment variable is required
# Solution: Add the generated key to .env

# Error: SENDGRID_WEBHOOK_VERIFICATION_KEY not configured
# Solution: Get the key from SendGrid dashboard and add to .env

# Error: Database connection failed
# Solution: Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are correct
```

### Tests failing
```bash
# Run with verbose output to see specific failures
pytest tests/test_phase0_fixes.py -v --tb=short

# If encryption tests fail:
# - Check CALENDAR_ENCRYPTION_KEY is set
# - Ensure it's a Fernet key (not token_urlsafe)

# If transaction tests fail:
# - Check database connection
# - Verify SUPABASE_SERVICE_ROLE_KEY is correct
```

---

## 📚 Related Documentation

- **Phase 0 Summary:** [PHASE0_FIXES_SUMMARY.md](PHASE0_FIXES_SUMMARY.md)
- **Required Variables:** [REQUIRED_ENV_VARS.md](REQUIRED_ENV_VARS.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Launch Status:** [LAUNCH_STATUS.md](LAUNCH_STATUS.md)

---

**Generated:** November 17, 2025
**Next Steps:** Follow this guide to set up your environment, then run verification tests.

