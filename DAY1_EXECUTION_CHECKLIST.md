# Day 1 Execution Checklist - Beat Lovable Speed Plan

**Target:** Production app live + first 10 customers in 24 hours  
**Time:** 6-hour sprint (can be done in one focused session)

---

## ✅ Hour 1: Environment Setup (CRITICAL)

### 1.1 Set Environment Variables

**Location:** `backend/crewai_agents/.env`

```bash
# Copy template
cp backend/crewai_agents/.env.example backend/crewai_agents/.env
```

**Required Variables (P0 - Blocking):**
- [ ] `SUPABASE_URL` - Already set ✅
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Already set ✅
- [ ] `SUPABASE_JWT_SECRET` - Get from Supabase Dashboard > Settings > API
- [ ] `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- [ ] `SENDGRID_API_KEY` - Get from https://app.sendgrid.com/settings/api_keys
- [ ] `TWILIO_ACCOUNT_SID` - Get from https://console.twilio.com/
- [ ] `TWILIO_AUTH_TOKEN` - Get from https://console.twilio.com/
- [ ] `REDIS_HOST` - Use Upstash (free) or Redis Cloud
- [ ] `REDIS_PASSWORD` - From Redis provider

**Quick Setup:**
1. **OpenAI:** Sign up → Billing → Add payment → Create API key
2. **SendGrid:** Sign up → Verify sender → Create API key
3. **Twilio:** Sign up → Get phone number → Copy credentials
4. **Redis:** Sign up at upstash.com → Create database → Copy connection string

**Verification:**
```bash
cd backend/crewai_agents
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
```

---

## ✅ Hour 2: Production Deployment

### 2.1 Choose Platform (Railway or Render)

**Option A: Railway (Recommended - Faster)**
1. Sign up at railway.app
2. Connect GitHub repo
3. Add environment variables (copy from .env)
4. Deploy (auto-detects Python/Node)

**Option B: Render**
1. Sign up at render.com
2. Connect GitHub repo
3. Use `render.yaml` config (already created)
4. Add environment variables

### 2.2 Deploy Services

**Services to Deploy:**
1. **FastAPI Backend** (Python) - Port 8081
2. **Node.js Proxy** (Express) - Port 3001
3. **Message Worker** (Node.js) - Background worker
4. **Redis Queue** - Managed service

**Deployment Commands:**
```bash
# Railway
railway up

# Render
# Uses render.yaml automatically
```

**Verification:**
- [ ] API health check: `https://your-app.railway.app/health`
- [ ] All services running
- [ ] Environment variables loaded

---

## ✅ Hour 3: Monitoring Setup

### 3.1 Sentry Integration (Error Tracking)

1. Sign up at sentry.io (free tier)
2. Create project → Python + Node.js
3. Get DSN
4. Add to `.env`:
   ```env
   SENTRY_DSN=https://xxx@sentry.io/xxx
   SENTRY_ENVIRONMENT=production
   ```

**Already Integrated:**
- Frontend: `@sentry/react` in `package.json`
- Backend: Add to `api_server.py` (see below)

**Add to `api_server.py`:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1
    )
```

- [ ] Sentry DSN added
- [ ] Errors visible in Sentry dashboard
- [ ] Alerts configured

---

## ✅ Hour 4: Webhook Endpoints

### 4.1 Configure Webhooks

**SendGrid Webhook:**
1. Go to SendGrid > Settings > Mail Settings > Event Webhook
2. Add endpoint: `https://your-app.railway.app/webhooks/sendgrid`
3. Select events: delivered, opened, clicked, bounced, spamreport, unsubscribe
4. Save

**Twilio Webhook:**
1. Go to Twilio Console > Phone Numbers > Manage > Active Numbers
2. Click your number
3. Set Status Callback URL: `https://your-app.railway.app/webhooks/twilio`
4. Save

**Stripe Webhook:**
1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://your-app.railway.app/webhooks/stripe`
3. Select events: `customer.subscription.*`, `invoice.payment.*`
4. Copy webhook secret → Add to `.env`: `STRIPE_WEBHOOK_SECRET`

**Verification:**
- [ ] SendGrid webhook receiving events
- [ ] Twilio webhook receiving status updates
- [ ] Stripe webhook receiving payment events
- [ ] Database updates working

---

## ✅ Hour 5: End-to-End Testing

### 5.1 Test Campaign Flow

**Test Steps:**
1. **Login** → Verify JWT auth
2. **Import Leads** → Upload CSV
3. **Launch Campaign** → "Launch campaign" in chat
4. **Verify Execution:**
   - [ ] REX parses command
   - [ ] Permissions checked
   - [ ] Special Forces crew executes
   - [ ] Messages queued to Redis
   - [ ] Worker sends messages
   - [ ] Webhooks update status
   - [ ] Database updated

**Expected Results:**
- Response: "Campaign launched."
- Messages in queue
- Worker processing jobs
- Delivery status updates

**Debugging:**
```bash
# Check API logs
railway logs

# Check worker logs
railway logs --service worker

# Check Redis queue
redis-cli LLEN message_scheduler_queue
```

---

## ✅ Hour 6: Fix Top 3 Blocking Bugs

### 6.1 Common Issues & Fixes

**Issue 1: OpenAI API Key Not Working**
- **Symptom:** "OPENAI_API_KEY is required"
- **Fix:** Verify key in `.env`, restart server
- **Test:** `python -c "from openai import OpenAI; OpenAI(api_key=os.getenv('OPENAI_API_KEY'))"`

**Issue 2: Redis Connection Failed**
- **Symptom:** "Connection refused" or "ECONNREFUSED"
- **Fix:** Check REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
- **Test:** `redis-cli -h $REDIS_HOST -p $REDIS_PORT ping`

**Issue 3: SendGrid/Twilio Not Sending**
- **Symptom:** Messages queued but not sent
- **Fix:** Verify API keys, check worker logs
- **Test:** Send test email/SMS manually

**Issue 4: Database RLS Blocking**
- **Symptom:** "permission denied" errors
- **Fix:** Verify SUPABASE_SERVICE_ROLE_KEY (bypasses RLS)
- **Test:** Query directly with service role key

**Issue 5: CORS Errors**
- **Symptom:** "CORS policy" errors in browser
- **Fix:** Add frontend URL to ALLOWED_ORIGINS
- **Test:** Check browser console

---

## 🎯 Success Criteria

**Day 1 Complete When:**
- [ ] All environment variables set
- [ ] Production app deployed and accessible
- [ ] Monitoring (Sentry) configured
- [ ] Webhooks receiving events
- [ ] End-to-end campaign flow working
- [ ] First test campaign executed successfully
- [ ] No critical errors in logs

**Next Steps (Day 2):**
- Acquire first 10 customers
- Set up analytics (PostHog/Mixpanel)
- Configure email templates
- Launch Product Hunt prep

---

## 🚀 Quick Commands Reference

```bash
# Check environment variables
cd backend/crewai_agents
python -c "import os; from dotenv import load_dotenv; load_dotenv(); [print(f'{k}: SET' if os.getenv(k) else f'{k}: MISSING') for k in ['OPENAI_API_KEY', 'SENDGRID_API_KEY', 'TWILIO_ACCOUNT_SID']]"

# Test API locally
cd backend/crewai_agents
python -m uvicorn api_server:app --port 8081

# Test worker locally
cd backend/node_scheduler_worker
npm start

# Deploy to Railway
railway login
railway init
railway up

# View logs
railway logs
railway logs --service worker
```

---

## ⚠️ Critical Notes

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use service role key for backend** - Bypasses RLS
3. **Test webhooks locally** - Use ngrok for local testing
4. **Monitor costs** - OpenAI, SendGrid, Twilio have usage limits
5. **Set up alerts** - Sentry, uptime monitoring

---

**Status:** Ready to execute  
**Estimated Time:** 6 hours  
**Blockers:** Environment variables (Hour 1)

