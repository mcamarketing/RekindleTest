# Stage A Deployment Guide - RekindlePro (0–5 Clients)

**Target**: Foundation deployment for 0–5 client organizations
**Estimated Time**: 2–3 hours
**Prerequisites**: Render/Railway account, Supabase account, domain name

---

## Overview

This guide walks you through deploying RekindlePro in **Stage A** configuration:
- Single API instance (Render or Railway)
- Managed Postgres (Supabase)
- Managed Redis (Render Redis or Upstash)
- Static frontend (Vercel/Netlify)
- Single worker process
- Basic monitoring (Sentry + platform health checks)

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Render account** (or Railway account)
- [ ] **Supabase project** created
- [ ] **Domain name** registered (for production)
- [ ] **GitHub repository** connected to deployment platform
- [ ] **Sentry account** (free tier) for error monitoring
- [ ] **OpenAI API key** (for LLM features)
- [ ] **SendGrid API key** (for email delivery)
- [ ] **Twilio account** (optional, for SMS)

---

## Step 1: Set Up Supabase (Database)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in:
   - **Project name**: `rekindlepro-production`
   - **Database password**: Generate strong password (save it!)
   - **Region**: Choose closest to your users
4. Wait 2 minutes for project provisioning

### 1.2 Run Database Migrations

```bash
# From repo root
cd supabase/migrations

# Apply migrations via Supabase CLI (if installed)
supabase db push

# OR manually via Supabase SQL Editor:
# Copy/paste contents of each migration file in order
```

### 1.3 Enable Row-Level Security (RLS)

```sql
-- Run in Supabase SQL Editor
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_missions ENABLE ROW LEVEL SECURITY;
ALTER TABLE rex_domain_pool ENABLE ROW LEVEL SECURITY;
-- ... (repeat for all tables)

-- Create RLS policies (see supabase/migrations/ for full policies)
```

### 1.4 Get Supabase Connection Details

From Supabase dashboard → Settings → API:

- **Project URL**: `https://xxxxx.supabase.co`
- **Anon/Public Key**: `eyJhbGc...` (for frontend)
- **Service Role Key**: `eyJhbGc...` (for backend - KEEP SECRET!)

---

## Step 2: Set Up Redis (Queue)

### Option A: Render Redis (Recommended)

1. In Render dashboard, click "New" → "Redis"
2. Configure:
   - **Name**: `rekindlepro-redis`
   - **Plan**: Starter ($7/month)
   - **Region**: Same as API
3. After creation, note:
   - **Internal Redis URL**: `redis://...` (for internal connections)
   - **External Redis URL**: `rediss://...` (if needed externally)

### Option B: Upstash Redis (Alternative)

1. Go to [upstash.com](https://upstash.com)
2. Create new Redis database
3. Choose region closest to API
4. Copy connection details (host, port, password)

---

## Step 3: Deploy Backend API

### 3.1 Prepare Environment Variables

Create a file with these variables (you'll paste them in Render UI):

```bash
# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc... (from Step 1.4)
SUPABASE_JWT_SECRET=xxx (from Supabase → Settings → API)

# Redis
REDIS_HOST=red-xxxxx.redis.render.com (from Step 2)
REDIS_PORT=6379
REDIS_PASSWORD=xxx (from Step 2)

# OpenAI
OPENAI_API_KEY=sk-xxx (your OpenAI API key)

# SendGrid (Email)
SENDGRID_API_KEY=SG.xxx (your SendGrid API key)

# Twilio (Optional - SMS)
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890

# Sentry (Error Monitoring)
SENTRY_DSN=https://xxx@sentry.io/xxx (from Step 4)
SENTRY_ENVIRONMENT=production

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
APP_URL=https://yourdomain.com

# Application
PORT=8081
NODE_ENV=production
```

### 3.2 Deploy to Render

**Using render.yaml (Automated):**

1. In Render dashboard, click "New" → "Blueprint"
2. Connect your GitHub repository
3. Select the repository
4. Render will auto-detect `render.yaml`
5. Click "Approve"
6. Render will create 3 services:
   - `rekindle-api` (FastAPI backend)
   - `rekindle-proxy` (Node.js proxy)
   - `rekindle-worker` (Queue worker)
   - `rekindle-redis` (Redis instance)

**Manual Setup (If not using render.yaml):**

1. Click "New" → "Web Service"
2. Connect GitHub repo
3. Configure:
   - **Name**: `rekindlepro-api`
   - **Environment**: Python 3.11
   - **Build Command**: `cd backend/crewai_agents && pip install -r requirements.txt`
   - **Start Command**: `cd backend/crewai_agents && uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter ($7/month)
4. Add all environment variables from Step 3.1
5. Click "Create Web Service"

### 3.3 Verify Backend Deployment

```bash
# Check health endpoint
curl https://your-api-url.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "timestamp": "2025-01-23T..."
}
```

---

## Step 4: Deploy Worker Service

### 4.1 Deploy Worker to Render

1. In Render dashboard, click "New" → "Background Worker"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `rekindlepro-worker`
   - **Environment**: Node
   - **Build Command**: `cd backend/node_scheduler_worker && npm install`
   - **Start Command**: `cd backend/node_scheduler_worker && npm start`
   - **Plan**: Starter ($7/month)
4. Add environment variables (same as API, except PORT)
5. Click "Create Background Worker"

### 4.2 Verify Worker is Running

Check Render logs:
```
[INFO] Worker started
[INFO] Connected to Redis at redis://...
[INFO] Listening for jobs on queue: campaigns
```

---

## Step 5: Deploy Frontend

### Option A: Vercel (Recommended for Static Sites)

```bash
# Install Vercel CLI
npm install -g vercel

# From repo root
cd /path/to/rekindle

# Login to Vercel
vercel login

# Deploy
vercel --prod

# During setup:
# - Framework: Vite
# - Build Command: npm run build
# - Output Directory: dist
# - Install Command: npm install
```

**Environment Variables in Vercel:**

Add via Vercel dashboard → Settings → Environment Variables:

```
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc... (anon key, not service role!)
VITE_API_BASE_URL=https://your-api-url.onrender.com
```

### Option B: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod

# Build command: npm run build
# Publish directory: dist
```

Add environment variables in Netlify dashboard.

### Option C: Render Static Site

1. Render dashboard → "New" → "Static Site"
2. Connect GitHub repo
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add environment variables

---

## Step 6: Configure Sentry (Error Monitoring)

### 6.1 Create Sentry Project

1. Go to [sentry.io](https://sentry.io) (free tier)
2. Create new project
3. Choose **FastAPI** for backend
4. Choose **React** for frontend
5. Copy the **DSN** (looks like `https://xxx@sentry.io/123456`)

### 6.2 Add Sentry DSN to Environments

**Backend (Render):**
- Go to service → Environment → Add Variable
- `SENTRY_DSN=https://xxx@sentry.io/123456`
- `SENTRY_ENVIRONMENT=production`

**Frontend (Vercel/Netlify):**
- Add environment variable:
- `VITE_SENTRY_DSN=https://xxx@sentry.io/123456`

### 6.3 Test Sentry Integration

**Backend:**
```bash
# Trigger a test error
curl -X POST https://your-api-url.onrender.com/test-error
```

**Frontend:**
- Open browser console
- Type: `throw new Error("Sentry test")`
- Check Sentry dashboard for error

---

## Step 7: Configure Domain & HTTPS

### 7.1 Add Custom Domain to Render

1. Render service → Settings → Custom Domains
2. Click "Add Custom Domain"
3. Enter: `api.yourdomain.com` (for backend)
4. Render provides CNAME record: `xxx.onrender.com`

### 7.2 Configure DNS

In your DNS provider (Cloudflare, Namecheap, etc.):

```
Type    Name    Value                   TTL
CNAME   api     xxx.onrender.com        Auto
CNAME   www     your-vercel.app         Auto
```

### 7.3 Verify HTTPS

```bash
# Should auto-redirect to HTTPS
curl -I http://api.yourdomain.com
# Look for: Location: https://api.yourdomain.com

# Check SSL
curl https://api.yourdomain.com/health
```

---

## Step 8: Configure Platform Health Checks

### 8.1 Render Health Checks

1. Go to service → Settings → Health Check
2. Configure:
   - **Path**: `/health`
   - **Protocol**: HTTPS
   - **Port**: Leave blank (uses service port)
   - **Timeout**: 30 seconds
   - **Interval**: 60 seconds
3. Save

### 8.2 Uptime Monitoring

Render includes basic uptime monitoring. For additional monitoring:

**Option: UptimeRobot (Free)**

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add monitor:
   - **Type**: HTTPS
   - **URL**: `https://api.yourdomain.com/health`
   - **Interval**: 5 minutes
3. Set alert email to ops@yourdomain.com

---

## Step 9: Verify Complete Deployment

### 9.1 System Health Check

```bash
# Backend health
curl https://api.yourdomain.com/health

# Expected:
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "orchestration": "healthy",
  "timestamp": "..."
}
```

### 9.2 Frontend Check

1. Visit `https://yourdomain.com`
2. Should load React app
3. Check browser console for errors
4. Verify API calls work (sign up flow)

### 9.3 Worker Check

```bash
# Check Render logs for worker
# Should see:
[INFO] Worker processing job: campaign_xxx
[INFO] Job completed successfully
```

### 9.4 Database Check

```bash
# Via Supabase dashboard:
# Table Editor → profiles → Should see user data
# SQL Editor → Run: SELECT COUNT(*) FROM profiles;
```

---

## Step 10: Post-Deployment Configuration

### 10.1 Test End-to-End Flow

1. **Sign up**: Create test user account
2. **Create campaign**: Add leads, configure outreach
3. **Trigger agent**: Run Rex mission
4. **Check logs**: Verify agent execution in Sentry/Render logs
5. **Verify data**: Check Supabase for campaign/lead data

### 10.2 Configure CORS

Verify CORS is correctly set:

```bash
# Test from browser console at yourdomain.com:
fetch('https://api.yourdomain.com/health')
  .then(r => r.json())
  .then(console.log)

# Should NOT show CORS error
```

If CORS error, update `ALLOWED_ORIGINS` in backend env vars:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 10.3 Enable RLS Policies

```sql
-- Via Supabase SQL Editor
-- Verify RLS is enforced:
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- All tables should show rowsecurity = true
```

---

## Troubleshooting

### Issue: Backend /health returns 500

**Check:**
- Supabase connection: Is `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` correct?
- Redis connection: Is Redis accessible from backend?

**Fix:**
```bash
# Test Supabase connection
curl -X GET 'https://xxxxx.supabase.co/rest/v1/profiles?limit=1' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"

# Test Redis (from Render shell)
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping
# Should return: PONG
```

### Issue: Worker not processing jobs

**Check:**
- Worker logs in Render dashboard
- Redis connection in worker
- Job format in queue

**Fix:**
```bash
# Check Redis queue
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD
> LLEN campaigns
# Should show number of pending jobs
```

### Issue: Frontend not connecting to API

**Check:**
- `VITE_API_BASE_URL` is set correctly
- CORS configured on backend
- Network tab in browser DevTools

**Fix:**
```javascript
// In browser console:
console.log(import.meta.env.VITE_API_BASE_URL)
// Should show: https://api.yourdomain.com
```

---

## Stage A Deployment Checklist

After completing all steps, verify:

### Infrastructure
- [ ] Supabase project created and migrations applied
- [ ] Redis instance provisioned (Render/Upstash)
- [ ] Backend API deployed to Render/Railway
- [ ] Worker service deployed and running
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Custom domain configured with HTTPS

### Observability
- [ ] `/health` endpoint returns 200
- [ ] Sentry error tracking enabled (backend + frontend)
- [ ] Platform health checks configured
- [ ] Uptime monitoring configured (UptimeRobot optional)

### Security
- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] CORS restricted to production domain
- [ ] RLS enabled on all Supabase tables
- [ ] Strong passwords for Redis/Postgres

### Documentation
- [ ] Deployment documented (this file)
- [ ] Environment variables list created (`ENV_VARS.md`)
- [ ] Runbook for common issues started

---

## Next Steps

Once Stage A is deployed and verified:

1. **Monitor for 1 week**: Watch logs, errors, performance
2. **Onboard first 1–3 pilot clients**
3. **Track metrics**: Client count, API requests/day, queue depth
4. **Plan for Stage B**: When approaching 5 clients, review `REKINDLEPRO_INFRA_ROADMAP.md` for Stage B requirements

---

## Support

- **Deployment Issues**: Check Render/Railway/Vercel logs
- **Application Errors**: Check Sentry dashboard
- **Database Issues**: Check Supabase logs and SQL Editor
- **Questions**: Refer to `docs/infra/REKINDLEPRO_CURRENT_STATE.md`
