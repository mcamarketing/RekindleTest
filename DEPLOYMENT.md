# Rekindle.ai - Production Deployment Guide

**Last Updated:** 2025-01-17
**Status:** Production-Ready
**Deployment Time:** 1-2 hours

---

## Quick Start

```bash
# 1. Verify environment configuration
python scripts/verify_env.py

# 2. Deploy to Railway (recommended)
railway login
railway link
railway up

# 3. Configure webhooks (see below)

# 4. Test deployment
curl https://your-app.railway.app/health
```

---

## Deployment Options

### Option A: Railway (Recommended)

**Why Railway:**
- ✅ One-click deployment
- ✅ Auto-detects configuration (`railway.json`)
- ✅ Built-in Redis, PostgreSQL if needed
- ✅ Automatic HTTPS
- ✅ Simple environment variable management
- ✅ Generous free tier

**Steps:**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Link to Project**
   ```bash
   # Option A: Link existing project
   railway link

   # Option B: Create new project
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   # Option A: Set via CLI
   railway variables set OPENAI_API_KEY=sk-...
   railway variables set SENDGRID_API_KEY=SG....
   # ... (repeat for all P0 variables)

   # Option B: Set via Dashboard (easier)
   railway open
   # Go to Variables tab, paste all from .env
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get URL**
   ```bash
   railway open
   # Copy the deployment URL
   ```

**Configuration:**
- Railway automatically uses `railway.json` for build/deploy config
- Multi-service deployment (frontend, Node.js API, Python API)
- Auto-scaling enabled

---

### Option B: Render.com

**Why Render:**
- ✅ Blueprint deployment (`render.yaml`)
- ✅ Multiple services from one config
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Good for teams (better collaboration features)

**Steps:**

1. **Sign Up**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Blueprint**
   - Click "New +" → "Blueprint"
   - Connect GitHub repository
   - Select branch: `main`

3. **Render Detects `render.yaml`**
   - Automatically creates 4 services:
     - `rekindle-api` (Python FastAPI)
     - `rekindle-proxy` (Node.js)
     - `rekindle-worker` (Background jobs)
     - `rekindle-redis` (Redis queue)

4. **Set Environment Variables**
   - For each service, go to Environment tab
   - Add all P0 variables from `.env`
   - Click "Save Changes"

5. **Deploy**
   - Click "Apply" to start deployment
   - Wait 5-10 minutes for initial build

6. **Get URL**
   - Copy URL from `rekindle-api` service
   - Use this for frontend `VITE_API_URL`

---

### Option C: Manual Deployment (VPS/EC2/DigitalOcean)

**For advanced users who want full control**

**Steps:**

1. **Set Up Server**
   ```bash
   # Ubuntu 22.04 LTS recommended
   sudo apt update
   sudo apt install -y python3.11 python3-pip nodejs npm redis-server nginx
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/rekindle.git
   cd rekindle
   ```

3. **Install Dependencies**
   ```bash
   # Frontend
   npm install
   npm run build

   # Backend - Node.js
   cd backend
   npm install

   # Backend - Python
   cd crewai_agents
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp backend/crewai_agents/.env.example backend/crewai_agents/.env
   # Edit .env with production values
   nano backend/crewai_agents/.env
   ```

5. **Set Up Services (systemd)**

   **Python API Service:**
   ```bash
   sudo nano /etc/systemd/system/rekindle-api.service
   ```

   ```ini
   [Unit]
   Description=Rekindle Python API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/var/www/rekindle/backend/crewai_agents
   Environment="PATH=/usr/bin:/usr/local/bin"
   ExecStart=/usr/bin/python3 api_server.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   **Node.js Proxy Service:**
   ```bash
   sudo nano /etc/systemd/system/rekindle-proxy.service
   ```

   ```ini
   [Unit]
   Description=Rekindle Node.js Proxy
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/var/www/rekindle/backend
   Environment="PATH=/usr/bin:/usr/local/bin"
   Environment="NODE_ENV=production"
   ExecStart=/usr/bin/npm start
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

6. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/rekindle
   ```

   ```nginx
   server {
       listen 80;
       server_name rekindle.ai www.rekindle.ai;

       # Frontend (static files)
       location / {
           root /var/www/rekindle/dist;
           try_files $uri $uri/ /index.html;
       }

       # Node.js Proxy API
       location /api/ {
           proxy_pass http://localhost:3001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       # Python API (internal)
       location /internal/ {
           proxy_pass http://localhost:8081;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
       }

       # WebSocket
       location /ws/ {
           proxy_pass http://localhost:8081;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

7. **Enable Services**
   ```bash
   sudo systemctl enable rekindle-api rekindle-proxy
   sudo systemctl start rekindle-api rekindle-proxy
   sudo systemctl enable nginx
   sudo systemctl restart nginx
   ```

8. **Configure SSL (Let's Encrypt)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d rekindle.ai -d www.rekindle.ai
   ```

---

## Webhook Configuration

### SendGrid Webhooks (Email Events)

1. **Go to SendGrid Dashboard**
   - https://app.sendgrid.com/settings/mail_settings

2. **Enable Event Webhook**
   - Click "Event Webhook"
   - Toggle ON
   - **URL:** `https://your-app.railway.app/webhooks/sendgrid`
   - **Events to track:**
     - ✅ Delivered
     - ✅ Bounce
     - ✅ Dropped
     - ✅ Spam Report
     - ✅ Unsubscribe
     - ✅ Open
     - ✅ Click

3. **Test Webhook**
   - Click "Test Your Integration"
   - Verify events appear in logs

---

### Twilio Webhooks (SMS/WhatsApp Status)

1. **Go to Twilio Console**
   - https://console.twilio.com/

2. **Configure Phone Number**
   - Navigate to: Phone Numbers → Manage → Active Numbers
   - Click your phone number
   - Under "Messaging":
     - **Status Callback URL:** `https://your-app.railway.app/webhooks/twilio`
     - **Method:** POST

3. **Test**
   - Send a test SMS
   - Check logs for webhook delivery

---

### Stripe Webhooks (Payment Events)

1. **Go to Stripe Dashboard**
   - https://dashboard.stripe.com/webhooks

2. **Add Endpoint**
   - Click "+ Add endpoint"
   - **URL:** `https://your-app.railway.app/webhooks/stripe`
   - **Events:**
     - ✅ customer.subscription.created
     - ✅ customer.subscription.updated
     - ✅ customer.subscription.deleted
     - ✅ invoice.paid
     - ✅ invoice.payment_failed

3. **Get Signing Secret**
   - Copy the webhook signing secret
   - Add to environment: `STRIPE_WEBHOOK_SECRET=whsec_...`

4. **Test**
   - Trigger test event from Stripe
   - Verify in logs

---

## Environment Variables Checklist

### P0 (Required - App won't start)

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=xxxx

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Email
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# SMS
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_PHONE_NUMBER=+1234567890

# Security
JWT_SECRET=<64-char random string>

# Optional but recommended
REDIS_HOST=redis-12345.upstash.io
REDIS_PASSWORD=xxxx
```

### P1 (Recommended)

```bash
# Monitoring
SENTRY_DSN=https://xxxx@sentry.io/xxxx

# Billing
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Calendar
CALENDAR_ENCRYPTION_KEY=<32-char random string>
```

---

## Post-Deployment Checklist

### 1. Health Checks

```bash
# API health
curl https://your-app.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "components": {
#     "database": "healthy",
#     "redis": "healthy",
#     "orchestration": "healthy"
#   }
# }

# Webhook health
curl https://your-app.railway.app/webhooks/health
```

### 2. Test Authentication

```bash
# Sign up test user
curl -X POST https://your-app.railway.app/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Login
curl -X POST https://your-app.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 3. Test Campaign Flow

1. Import test leads (CSV upload)
2. Launch campaign via Rex chat
3. Verify messages queued
4. Check SendGrid/Twilio dashboards
5. Verify webhooks updating status

### 4. Monitor Logs

```bash
# Railway
railway logs

# Render
# View logs in dashboard: Services → rekindle-api → Logs

# Manual deployment
sudo journalctl -u rekindle-api -f
```

---

## Troubleshooting

### API Not Starting

**Symptom:** Service crashes on startup

**Check:**
1. Environment variables set? `railway variables`
2. Database connection working? Check Supabase dashboard
3. OpenAI API key valid? Test at https://platform.openai.com/api-keys

**Fix:**
```bash
railway logs --tail 100
# Look for error messages
```

### Webhooks Not Working

**Symptom:** Messages sent but status not updating

**Check:**
1. Webhook URL correct? Should be `https://` not `http://`
2. Signature verification enabled? Check logs for 401 errors
3. Webhook secrets set? `SENDGRID_WEBHOOK_SECRET`, etc.

**Fix:**
```bash
# Test webhook manually
curl -X POST https://your-app.railway.app/webhooks/sendgrid \
  -H "Content-Type: application/json" \
  -d '[{"event":"delivered","email":"test@example.com"}]'
```

### High Latency

**Symptom:** API responses slow (> 3s)

**Check:**
1. Database queries optimized? Check slow query logs
2. Redis cache working? `REDIS_HOST` set?
3. Worker processing messages? Check queue depth

**Fix:**
- Add database indexes
- Enable Redis caching
- Scale workers

### CORS Errors

**Symptom:** Frontend can't connect to API

**Check:**
1. `ALLOWED_ORIGINS` includes frontend URL?
2. Frontend `VITE_API_URL` correct?

**Fix:**
```bash
# Add frontend domain to allowed origins
railway variables set ALLOWED_ORIGINS=https://rekindle.ai,https://www.rekindle.ai
```

---

## Rollback Procedure

### Railway

```bash
# List deployments
railway status

# Rollback to previous deployment
railway rollback
```

### Render

1. Go to service → Deploys
2. Click on previous successful deploy
3. Click "Redeploy"

### Manual

```bash
# Checkout previous version
git checkout <previous-commit-hash>

# Restart services
sudo systemctl restart rekindle-api rekindle-proxy
```

---

## Monitoring & Alerts

### Sentry (Error Tracking)

1. Sign up: https://sentry.io
2. Create project (FastAPI)
3. Copy DSN
4. Add to env: `SENTRY_DSN=...`

### Uptime Monitoring

**Recommended: UptimeRobot (Free)**

1. Sign up: https://uptimerobot.com
2. Add monitor:
   - Type: HTTPS
   - URL: `https://your-app.railway.app/health`
   - Interval: 5 minutes
3. Add alert contacts (email/Slack)

### Log Aggregation

**Recommended: Logtail (Free Tier)**

1. Sign up: https://logtail.com
2. Create source (Python)
3. Add to logging config
4. View logs in dashboard

---

## Scaling

### Vertical Scaling (More Resources)

**Railway:**
```bash
# Upgrade plan for more CPU/RAM
railway plans
```

**Render:**
- Dashboard → Service → Instance Type → Upgrade

### Horizontal Scaling (More Instances)

**Railway:**
- Not needed initially (auto-scales)

**Render:**
- Dashboard → Service → Scaling → Increase replicas

### Database Scaling

**Supabase:**
- Dashboard → Settings → Database → Upgrade Plan
- Enable connection pooling
- Add read replicas

---

## Security

### SSL/TLS

- ✅ Railway: Auto-configured
- ✅ Render: Auto-configured
- ⚠️ Manual: Use Let's Encrypt (see above)

### Secrets Management

**Never commit:**
- `.env` files
- API keys
- Database credentials

**Use:**
- Railway Variables
- Render Environment Variables
- AWS Secrets Manager (production)

### Rate Limiting

Already configured in `api_server.py`:
- 10 req/min for campaign endpoints
- 60 req/min for read endpoints

### Firewall Rules

**Recommended (Manual deployment):**
```bash
# Allow only HTTPS and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Cost Estimation

### Railway (Recommended for MVP)

- **Free Tier:** $5 free credit/month
- **Hobby Plan:** $5/month (suitable for 100 users)
- **Pro Plan:** $20/month (suitable for 1000 users)

### Render

- **Free Tier:** Free (with limitations)
- **Starter Plan:** $7/service/month
- **Total:** ~$28/month (4 services)

### External Services

- **Supabase:** Free tier → $25/month (Pro)
- **SendGrid:** Free 100 emails/day → $15/month (Essentials)
- **Twilio:** Pay-as-you-go (~$0.0075/SMS)
- **OpenAI:** Pay-as-you-go (~$0.01/1K tokens)
- **Sentry:** Free tier → $26/month (Team)

**Total Monthly Cost (Early Stage):**
- **Month 1:** $0-50 (using free tiers)
- **Month 3:** $100-200 (100 customers)
- **Month 6:** $500-1000 (1000 customers)

---

## Support

**Issues:** https://github.com/your-org/rekindle/issues
**Docs:** This file + `DAY1_EXECUTION_CHECKLIST.md`
**Team:** Slack #eng-support

---

**Last Updated:** 2025-01-17
**Next Review:** 2025-02-01
