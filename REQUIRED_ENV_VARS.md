# Required Environment Variables - Phase 0

**Generated:** November 17, 2025
**Status:** Post-Phase 0 requirements
**Purpose:** Checklist for deployment environment configuration

---

## 🎯 Quick Start

### Generate Keys
```bash
# 1. Calendar encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. JWT secret
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## 📋 Frontend Environment Variables

**File:** `frontend/.env.local` (create from `.env.example`)

```bash
# Supabase Configuration (Fix 1 - REQUIRED)
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Configuration (Fix 2 - REQUIRED for production only)
# In development, will fallback to http://localhost:3001/api with warning
# In production builds, THIS IS REQUIRED or build will fail
VITE_API_URL=https://your-api.railway.app/api
```

### How to Get Frontend Values

**Supabase:**
1. Go to: https://app.supabase.com/project/YOUR_PROJECT/settings/api
2. Copy "Project URL" → `VITE_SUPABASE_URL`
3. Copy "anon public" key → `VITE_SUPABASE_ANON_KEY`

**API URL:**
- Development: Leave unset (will use localhost)
- Production: Set to your deployed backend URL

---

## 📋 Backend Environment Variables

**File:** `backend/crewai_agents/.env` (create from `.env.example`)

### 🔴 P0 Variables (CRITICAL - Required for basic operation)

```bash
# Database
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# AI/ML
OPENAI_API_KEY=sk-...

# Authentication
JWT_SECRET=<generate with: python -c "import secrets; print(secrets.token_urlsafe(64))">

# Email (SendGrid)
SENDGRID_API_KEY=SG...
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890

# OAuth Token Encryption (Fix 5 - NEW REQUIREMENT)
CALENDAR_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# Webhook Security (Fix 4 - NEW REQUIREMENT)
SENDGRID_WEBHOOK_VERIFICATION_KEY=<from SendGrid dashboard>
```

### 🟡 P1 Variables (Optional but recommended)

```bash
# Error Tracking
SENTRY_DSN=https://...@sentry.io/...

# Rate Limiting (if using external Redis)
REDIS_URL=redis://...

# Payment Processing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Feature Flags
ENABLE_CALENDAR_SYNC=true
ENABLE_AI_AGENTS=true
```

### 🟢 Optional Variables

```bash
# Key Rotation (Fix 5 - For zero-downtime key rotation)
CALENDAR_ENCRYPTION_KEY_OLD=<old key during rotation>

# Additional Webhooks
TWILIO_WEBHOOK_SECRET=<from Twilio dashboard>
STRIPE_WEBHOOK_SECRET=<from Stripe dashboard>

# Development
DEBUG=false
LOG_LEVEL=info
```

---

## 🔑 How to Get Backend Values

### Supabase
1. Go to: https://app.supabase.com/project/YOUR_PROJECT/settings/api
2. Copy "Project URL" → `SUPABASE_URL`
3. Copy "service_role secret" key → `SUPABASE_SERVICE_ROLE_KEY`
   - ⚠️ **WARNING:** Never expose service role key to frontend!

### OpenAI
1. Go to: https://platform.openai.com/api-keys
2. Create new key → `OPENAI_API_KEY`

### SendGrid
1. Go to: https://app.sendgrid.com/settings/api_keys
2. Create new key with "Mail Send" permissions → `SENDGRID_API_KEY`
3. Go to: https://app.sendgrid.com/settings/sender_auth
4. Verify sender email → `SENDGRID_FROM_EMAIL`
5. Go to: https://app.sendgrid.com/settings/mail_settings
6. Enable "Event Webhook" → Copy "Verification Key" → `SENDGRID_WEBHOOK_VERIFICATION_KEY`

### Twilio
1. Go to: https://console.twilio.com
2. Copy "Account SID" → `TWILIO_ACCOUNT_SID`
3. Copy "Auth Token" → `TWILIO_AUTH_TOKEN`
4. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
5. Get your phone number → `TWILIO_PHONE_NUMBER` (format: +1234567890)

### JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copy output to JWT_SECRET
```

### Calendar Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to CALENDAR_ENCRYPTION_KEY
```

---

## ✅ Verification

### Verify All Variables Set
```bash
cd backend/crewai_agents
python scripts/verify_env.py

# Expected output:
# ✅ P0 Variables: 11/11 configured (100%)
# ✅ P1 Variables: 3/5 configured (60%)
# ✅ READY TO DEPLOY
```

### Test Encryption Setup
```bash
cd backend/crewai_agents
python -c "
from utils.token_encryption import validate_encryption_setup
validate_encryption_setup()
print('✅ Encryption setup valid')
"
```

### Test Database Connection
```bash
cd backend/crewai_agents
python -c "
from utils.database import SupabaseDB
db = SupabaseDB()
result = db.supabase.table('profiles').select('id').limit(1).execute()
print('✅ Database connection OK' if result.data is not None else '❌ Database connection FAILED')
"
```

---

## 🚨 Security Warnings

### ❌ NEVER Do This
```bash
# DO NOT commit .env files
git add .env  # ❌ WRONG

# DO NOT hardcode secrets in code
const apiKey = "sk-abc123..."  // ❌ WRONG

# DO NOT share service role keys with frontend
VITE_SUPABASE_SERVICE_KEY=...  # ❌ WRONG - service keys are backend-only!

# DO NOT use production keys in development
# Keep separate .env files for dev/staging/prod
```

### ✅ DO This Instead
```bash
# Commit only .env.example with dummy values
git add .env.example  # ✅ CORRECT

# Use environment variables
const apiKey = process.env.OPENAI_API_KEY  // ✅ CORRECT

# Frontend gets only anon key
VITE_SUPABASE_ANON_KEY=...  # ✅ CORRECT

# Separate environments
.env.development
.env.staging
.env.production
```

---

## 📝 Deployment Platform Setup

### Railway
```bash
# Set variables via CLI
railway variables set SUPABASE_URL=https://...
railway variables set OPENAI_API_KEY=sk-...
# ... etc

# Or via dashboard:
# https://railway.app/project/YOUR_PROJECT/variables
```

### Render
```bash
# Set variables via dashboard:
# https://dashboard.render.com/web/YOUR_SERVICE/env

# Or via render.yaml:
envVars:
  - key: SUPABASE_URL
    value: https://...
  - key: OPENAI_API_KEY
    sync: false  # Mark as secret
```

### Vercel (Frontend)
```bash
# Set variables via CLI
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production
vercel env add VITE_API_URL production

# Or via dashboard:
# https://vercel.com/YOUR_PROJECT/settings/environment-variables
```

---

## 🔄 Key Rotation Procedure

### Rotating Calendar Encryption Key

**Step 1: Prepare**
```bash
# Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Save as NEW_KEY
```

**Step 2: Set Both Keys**
```bash
# In .env or deployment platform
CALENDAR_ENCRYPTION_KEY=<NEW_KEY>
CALENDAR_ENCRYPTION_KEY_OLD=<CURRENT_KEY>
```

**Step 3: Re-encrypt Tokens**
```bash
python -c "
from utils.token_encryption import rotate_token_encryption
from utils.database import SupabaseDB

db = SupabaseDB()
connections = db.supabase.table('calendar_connections').select('*').execute()

for conn in connections.data:
    new_access = rotate_token_encryption(conn['access_token_encrypted'])
    new_refresh = rotate_token_encryption(conn['refresh_token_encrypted']) if conn.get('refresh_token_encrypted') else None

    db.supabase.table('calendar_connections').update({
        'access_token_encrypted': new_access,
        'refresh_token_encrypted': new_refresh
    }).eq('id', conn['id']).execute()

print(f'✅ Rotated {len(connections.data)} tokens')
"
```

**Step 4: Remove Old Key**
```bash
# After verifying all tokens rotated successfully
# Remove CALENDAR_ENCRYPTION_KEY_OLD from environment
```

---

## 📊 Environment Variable Summary

| Variable | Required | Phase | Where to Get | Used By |
|----------|----------|-------|--------------|---------|
| VITE_SUPABASE_URL | ✅ Yes | P0 | Supabase Dashboard | Frontend |
| VITE_SUPABASE_ANON_KEY | ✅ Yes | P0 | Supabase Dashboard | Frontend |
| VITE_API_URL | ✅ Prod only | P0 | Your deployment URL | Frontend |
| SUPABASE_URL | ✅ Yes | P0 | Supabase Dashboard | Backend |
| SUPABASE_SERVICE_ROLE_KEY | ✅ Yes | P0 | Supabase Dashboard | Backend |
| OPENAI_API_KEY | ✅ Yes | P0 | OpenAI Platform | Backend |
| JWT_SECRET | ✅ Yes | P0 | Generate locally | Backend |
| SENDGRID_API_KEY | ✅ Yes | P0 | SendGrid Dashboard | Backend |
| SENDGRID_FROM_EMAIL | ✅ Yes | P0 | SendGrid Verified Sender | Backend |
| SENDGRID_WEBHOOK_VERIFICATION_KEY | ✅ Yes | P0 | SendGrid Webhook Settings | Backend |
| TWILIO_ACCOUNT_SID | ✅ Yes | P0 | Twilio Console | Backend |
| TWILIO_AUTH_TOKEN | ✅ Yes | P0 | Twilio Console | Backend |
| TWILIO_PHONE_NUMBER | ✅ Yes | P0 | Twilio Phone Numbers | Backend |
| CALENDAR_ENCRYPTION_KEY | ✅ Yes | P0 | Generate locally | Backend |
| CALENDAR_ENCRYPTION_KEY_OLD | ⚠️ Optional | P0 | During key rotation | Backend |
| SENTRY_DSN | ⚠️ Recommended | P1 | Sentry Dashboard | Backend |
| REDIS_URL | ⚠️ Optional | P1 | Redis provider | Backend |
| STRIPE_SECRET_KEY | ⚠️ Optional | P1 | Stripe Dashboard | Backend |

**Total Required for P0:** 14 variables (3 frontend + 11 backend)

---

## 🎯 Quick Copy Template

### Frontend (.env.local)
```bash
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=
```

### Backend (.env)
```bash
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
OPENAI_API_KEY=
JWT_SECRET=
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=
SENDGRID_WEBHOOK_VERIFICATION_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
CALENDAR_ENCRYPTION_KEY=
```

---

**Last Updated:** November 17, 2025
**Next Review:** Before production deployment
**Related Docs:** [PHASE0_FIXES_SUMMARY.md](PHASE0_FIXES_SUMMARY.md), [DEPLOYMENT.md](DEPLOYMENT.md)
