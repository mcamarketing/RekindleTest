# Quick Setup Checklist

**Use this checklist to set up your environment in 30 minutes.**

---

## ✅ Generated Keys (Copy These Now)

```bash
# Copy these to your backend .env file:
JWT_SECRET=oJxue8trw8YEYmDD1oSYamQqhf7J6evmllWjt64UArnJZk7HUU1pgZ0E335FlffRPgrUGddRHHRmFUp8o4QZyQ
CALENDAR_ENCRYPTION_KEY=CChwG6fXLoH6DczAfDVaYc4k1VklM4sMy2aKCkqi6y8=
```

---

## 📋 Frontend Setup (5 minutes)

### 1. Create `.env.local`:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
cp .env.example .env.local
```

### 2. Get Supabase credentials:
- Go to: https://app.supabase.com/project/_/settings/api
- Copy **Project URL** and **anon public key**

### 3. Edit `.env.local`:
```bash
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...YOUR_ANON_KEY
VITE_API_URL=http://localhost:3001/api
```

### 4. Verify:
```bash
npm run build
```
Should see: `✓ built in XXXms`

---

## 📋 Backend Setup (25 minutes)

### 1. Create `.env`:
```bash
cd backend\crewai_agents
cp .env.example .env
```

### 2. Add the generated keys (ALREADY DONE ✅):
```bash
# These are already generated - just copy to .env:
JWT_SECRET=oJxue8trw8YEYmDD1oSYamQqhf7J6evmllWjt64UArnJZk7HUU1pgZ0E335FlffRPgrUGddRHHRmFUp8o4QZyQ
CALENDAR_ENCRYPTION_KEY=CChwG6fXLoH6DczAfDVaYc4k1VklM4sMy2aKCkqi6y8=
```

### 3. Get credentials from external services:

**Supabase (3 vars) - 5 min:**
- URL: https://app.supabase.com/project/_/settings/api
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (⚠️ NOT the anon key!)
- `SUPABASE_JWT_SECRET`

**OpenAI (1 var) - 2 min:**
- URL: https://platform.openai.com/api-keys
- `OPENAI_API_KEY`

**Anthropic (1 var) - 2 min:**
- URL: https://console.anthropic.com/settings/keys
- `ANTHROPIC_API_KEY`

**SendGrid (3 vars) - 5 min:**
- URL: https://app.sendgrid.com/settings/api_keys
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL` (must be verified)
- `SENDGRID_WEBHOOK_VERIFICATION_KEY` (from Mail Settings → Event Webhook)

**Twilio (3 vars) - 5 min:**
- URL: https://console.twilio.com
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

**Stripe (2 vars) - 3 min:**
- URL: https://dashboard.stripe.com/apikeys
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET` (from Webhooks section)

### 4. Verify setup:
```bash
python scripts/verify_env.py
```
Should see: `✅ P0 Variables: 14/14 configured (100%)`

---

## 🧪 Run Tests (5 minutes)

```bash
cd backend\crewai_agents
pytest tests/test_phase0_fixes.py -v
```

Should see: `15 passed`

---

## 🚀 Start the App (2 minutes)

### Terminal 1 - Backend:
```bash
cd backend\crewai_agents
python api_server.py
```

### Terminal 2 - Frontend:
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
npm run dev
```

### Open browser:
http://localhost:5173

---

## 📊 Progress Tracker

**Frontend:**
- [ ] Created `.env.local`
- [ ] Added `VITE_SUPABASE_URL`
- [ ] Added `VITE_SUPABASE_ANON_KEY`
- [ ] Added `VITE_API_URL`
- [ ] Build succeeded (`npm run build`)

**Backend:**
- [ ] Created `.env`
- [ ] Added `JWT_SECRET` ✅ (generated)
- [ ] Added `CALENDAR_ENCRYPTION_KEY` ✅ (generated)
- [ ] Added `SUPABASE_URL`
- [ ] Added `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Added `SUPABASE_JWT_SECRET`
- [ ] Added `OPENAI_API_KEY`
- [ ] Added `ANTHROPIC_API_KEY`
- [ ] Added `SENDGRID_API_KEY`
- [ ] Added `SENDGRID_FROM_EMAIL`
- [ ] Added `SENDGRID_WEBHOOK_VERIFICATION_KEY`
- [ ] Added `TWILIO_ACCOUNT_SID`
- [ ] Added `TWILIO_AUTH_TOKEN`
- [ ] Added `TWILIO_PHONE_NUMBER`
- [ ] Added `STRIPE_SECRET_KEY`
- [ ] Verification passed (`python scripts/verify_env.py`)

**Testing:**
- [ ] Smoke tests passed (`pytest tests/test_phase0_fixes.py -v`)
- [ ] Backend started successfully
- [ ] Frontend started successfully
- [ ] Can access app at http://localhost:5173

---

## 🆘 Quick Help

**Frontend build fails:**
```bash
# Check .env.local exists and has all 3 variables
cat .env.local
```

**Backend verify_env fails:**
```bash
# See which variables are missing
python scripts/verify_env.py
# Add the missing ones to .env
```

**Tests fail:**
```bash
# Run with details
pytest tests/test_phase0_fixes.py -v --tb=short
```

---

**Total Time:** ~30 minutes
**Next Step:** See [ENVIRONMENT_SETUP_GUIDE.md](ENVIRONMENT_SETUP_GUIDE.md) for detailed instructions
