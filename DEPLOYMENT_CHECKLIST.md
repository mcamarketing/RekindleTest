# 🚀 Rekindle MVP Launch Checklist

## Pre-Launch Checklist

### ✅ Completed
- [x] AI Research Engine (LinkedIn + Job Signals + News)
- [x] Multi-Channel Agent Framework (CrewAI)
- [x] Node.js Scheduler Worker (BullMQ)
- [x] FastAPI Bridge Server
- [x] Calendar Integration Wizard
- [x] Stripe Webhook Integration
- [x] Billing UI & Subscription Management
- [x] Structured Logging (All Services)
- [x] Corporate Identity (MCP Authentication)

### 🔄 In Progress / To Do
- [ ] Environment Variables Setup
- [ ] Service Startup Scripts
- [ ] End-to-End Testing
- [ ] Domain Reputation Check
- [ ] Production Secrets Management

---

## Environment Variables Reference

### **1. FastAPI Server** (`backend/crewai_agents/api_server.py`)

Required:
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Authentication
TRACKER_API_TOKEN=your_shared_secret_token

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620

# MCP Servers (Internal)
STRIPE_MCP_URL=http://mcp-stripe-server
LINKEDIN_MCP_URL=http://mcp-linkedin-server
CALENDAR_MCP_URL=http://mcp-calendar-server

# Redis (for job queue)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### **2. Node.js Scheduler Worker** (`backend/node_scheduler_worker/worker.js`)

Required:
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_SCHEDULER_QUEUE=message_scheduler_queue

# Logging (Optional)
LOG_AGGREGATOR_URL=http://your-log-aggregator/api/logs
NODE_INSTANCE_ID=worker-001  # Optional: unique instance identifier
```

### **3. Frontend (Vite + React)**

Required (`.env`):
```bash
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key

# API Endpoints
VITE_PYTHON_API_URL=http://localhost:8081
VITE_TRACKER_API_TOKEN=your_shared_secret_token
```

### **4. Supabase Edge Functions**

Required (Supabase Dashboard → Project Settings → Edge Functions → Secrets):

```bash
# Research Lead Function
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620
LINKEDIN_MCP_URL=http://mcp-linkedin-server
LINKEDIN_MCP_API_KEY=your_linkedin_mcp_key
TRACKER_API_TOKEN=your_shared_secret_token
NEWS_API_KEY=your_news_api_key  # Optional
BUILTWITH_API_KEY=your_builtwith_key  # Optional

# Tracker Webhook Function
PY_TRACKER_API_URL=http://your-fastapi-server:8081
TRACKER_API_TOKEN=your_shared_secret_token
```

---

## Service Startup Instructions

### **1. PM2 Configuration**

Start all services with PM2:
```bash
# Install PM2 globally (if not installed)
npm install -g pm2

# Start all services
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs node-scheduler-worker
pm2 logs fastapi-api-server

# Restart a service
pm2 restart fastapi-api-server

# Stop all services
pm2 stop all
```

### **2. Manual Startup (Development)**

#### FastAPI Server:
```bash
cd backend/crewai_agents
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8081 --reload
```

#### Node.js Worker:
```bash
cd backend/node_scheduler_worker
npm install
npm start  # or: node worker.js
```

#### Frontend:
```bash
npm install
npm run dev
```

---

## End-to-End Testing Checklist

### **1. Research Pipeline**
- [ ] Import leads via CSV (`/leads/import`)
- [ ] Click "Start AI Research"
- [ ] Verify lead status changes to "researching"
- [ ] Check `leads.ai_insights` populated (LinkedIn + Job Signals)
- [ ] Verify `leads.ai_score` calculated correctly

### **2. Campaign Launch**
- [ ] Create campaign with selected leads
- [ ] Click "Start Campaign"
- [ ] Verify FastAPI endpoint `/api/campaigns/{id}/launch` receives request
- [ ] Check Redis queue for scheduled jobs
- [ ] Verify messages generated in `messages` table (status='queued')

### **3. Message Delivery**
- [ ] Verify Node.js worker processes jobs from Redis
- [ ] Check message status updates to 'sent'
- [ ] Verify `sent_at` timestamp populated
- [ ] Check structured logs for delivery events

### **4. Inbound Reply Tracking**
- [ ] Simulate inbound reply webhook
- [ ] Verify FastAPI `/api/inbound-reply` processes request
- [ ] Check lead status/sentiment updated
- [ ] Verify Slack notification sent (if configured)

### **5. Calendar Integration**
- [ ] Test OAuth flow (`/api/calendar/oauth/initiate`)
- [ ] Complete OAuth callback (`/api/calendar/oauth/callback`)
- [ ] Verify tokens stored in Supabase
- [ ] Simulate meeting booking webhook (`/api/calendar/webhook`)
- [ ] Verify billing charge triggered

### **6. Billing & Stripe**
- [ ] Access `/billing` page
- [ ] Verify subscription status displayed
- [ ] Click "Manage Subscription" (should open Stripe Portal)
- [ ] Test Stripe webhook (`/api/billing/webhook`)
- [ ] Verify invoice status updates

---

## Production Deployment Considerations

### **1. Security**
- [ ] All secrets moved to managed secrets store (not `.env` files)
- [ ] `TRACKER_API_TOKEN` set and enforced for all internal API calls
- [ ] MCP servers in private subnet (not publicly accessible)
- [ ] Supabase RLS policies configured correctly
- [ ] CORS configured for production domain

### **2. Monitoring & Observability**
- [ ] Structured logging enabled (all services)
- [ ] Log aggregator endpoint configured (optional)
- [ ] PM2 logs directory configured (`/var/log/rekindle/`)
- [ ] Health check endpoints responding (`/health`)

### **3. Scalability**
- [ ] Redis connection pooling configured
- [ ] Supabase connection limits considered
- [ ] PM2 instances count adjusted for load
- [ ] Worker instances scaled as needed

### **4. Domain & Email**
- [ ] Domain reputation checked (for email deliverability)
- [ ] SPF/DKIM records configured
- [ ] Sending domain warmed up (if new)
- [ ] Email provider (SendGrid/SMTP) configured

---

## Quick Reference Commands

```bash
# Check all services running
pm2 status

# View all logs
pm2 logs

# Restart everything
pm2 restart all

# Stop everything
pm2 stop all

# Save PM2 configuration
pm2 save
pm2 startup  # Enable auto-start on boot

# Check FastAPI health
curl http://localhost:8081/health

# Check Redis connection
redis-cli ping

# Test billing endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8081/api/billing/status?user_id=USER_ID"
```

---

## Troubleshooting

### **Worker not processing jobs:**
1. Check Redis connection: `redis-cli ping`
2. Check queue name: `redis-cli LLEN message_scheduler_queue`
3. Check worker logs: `pm2 logs node-scheduler-worker`

### **FastAPI not responding:**
1. Check if running: `pm2 status`
2. Check logs: `pm2 logs fastapi-api-server`
3. Verify environment variables loaded
4. Test health endpoint: `curl http://localhost:8081/health`

### **Messages not generating:**
1. Check Supabase connection
2. Verify Anthropic API key
3. Check orchestration service logs
4. Verify lead has `ai_insights` populated

---

## Next Steps After Launch

1. **Monitor First Week:**
   - Track error rates in logs
   - Monitor Redis queue depth
   - Check message delivery success rate
   - Monitor API response times

2. **Iterate:**
   - Gather user feedback
   - Improve message quality (prompt engineering)
   - Optimize research signals
   - Add more channels as needed

3. **Scale:**
   - Increase PM2 instances based on load
   - Scale Redis if queue depth grows
   - Consider database read replicas
   - Add CDN for static assets

---

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")
**Status:** Ready for Production Testing

