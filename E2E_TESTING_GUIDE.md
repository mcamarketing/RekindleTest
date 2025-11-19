# 🧪 END-TO-END TESTING GUIDE

## 🎯 OVERVIEW

This guide provides comprehensive instructions for testing the entire Rekindle.ai system end-to-end, from lead import to message delivery.

---

## ✅ PREREQUISITES

### **1. Environment Variables**

**FastAPI Server** (`backend/crewai_agents/.env`):
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_JWT_SECRET=xxx

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=xxx

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://rekindle.ai
PORT=8081
ENVIRONMENT=development
```

**Node.js Worker** (`backend/node_scheduler_worker/.env`):
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=xxx
REDIS_SCHEDULER_QUEUE=message_scheduler_queue

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@rekindle.ai
SENDGRID_UNSUBSCRIBE_GROUP_ID=12345

# Twilio
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Worker Config
WORKER_CONCURRENCY=10
WORKER_MAX_JOBS=100
NODE_INSTANCE_ID=worker-001
LOG_LEVEL=info
NODE_ENV=development
```

**Stripe** (for billing tests):
```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**LinkedIn** (for research tests):
```bash
LINKEDIN_ACCESS_TOKEN=xxx
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx
```

---

## 🚀 STARTING SERVICES

### **Terminal 1: Redis**
```bash
redis-server
# Or if using cloud Redis, verify connection
redis-cli ping
# Should return: PONG
```

### **Terminal 2: FastAPI Server**
```bash
cd backend/crewai_agents
python api_server.py
# Should see: "Rekindle API Server started successfully"
# Server running on: http://0.0.0.0:8081
```

### **Terminal 3: Node.js Worker**
```bash
cd backend/node_scheduler_worker
npm install  # If not already done
npm start
# Should see: "Worker started successfully"
# Should see: "Listening for jobs on queue: message_scheduler_queue"
```

### **Terminal 4: Frontend (Optional, for UI testing)**
```bash
npm run dev
# Should see: "Local: http://localhost:5173"
```

---

## 🧪 TEST SUITE

### **Test 1: Health Checks**

**FastAPI Health:**
```bash
curl http://localhost:8081/health
# Expected: {"status":"ok","database_connection":"successful",...}
```

**Redis Connection:**
```bash
redis-cli ping
# Expected: PONG
```

**Worker Status:**
```bash
# Check worker logs - should show "Worker started successfully"
```

---

### **Test 2: Lead Import**

**Via API:**
```bash
# Get auth token first (via signup/login)
curl -X POST http://localhost:8081/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Use token for import
curl -X POST http://localhost:8081/api/v1/leads/import \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "company": "Acme Corp",
      "industry": "SaaS",
      "lead_score": 75
    }
  ]'
# Expected: {"success":true,"imported_count":1,...}
```

**Verify in Database:**
```sql
SELECT * FROM leads WHERE email = 'john.doe@example.com';
```

---

### **Test 3: Campaign Start**

```bash
# Start campaign for a lead
curl -X POST http://localhost:8081/api/v1/campaigns/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_ids": ["LEAD_UUID_HERE"]
  }'
# Expected: {"success":true,"campaigns_started":1,...}
```

**Verify:**
1. Check Redis queue: `redis-cli LLEN message_scheduler_queue:waiting`
2. Check worker logs - should show "Processing message job"
3. Check lead status in database - should be "campaign_active"

---

### **Test 4: Message Delivery**

**Verify Worker Processes Job:**
- Check worker logs:
  - "Processing message job"
  - "Email sent successfully" (or SMS/WhatsApp)
  - "Message job completed"

**Verify SendGrid/Twilio:**
- Check SendGrid dashboard for sent emails
- Check Twilio dashboard for sent SMS/WhatsApp
- Verify message content matches generated message

**Verify Database:**
```sql
-- Check messages table
SELECT * FROM messages WHERE lead_id = 'LEAD_UUID';

-- Check lead status
SELECT status, total_messages_sent, last_contact_date FROM leads WHERE id = 'LEAD_UUID';
```

---

### **Test 5: Billing Integration**

**Trigger Meeting Booking:**
```bash
# Simulate meeting booked (would normally come from reply handling)
curl -X POST http://localhost:8081/api/v1/replies/handle \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "LEAD_UUID",
    "reply_text": "Yes, let's schedule a meeting!",
    "channel": "email"
  }'
```

**Verify Stripe:**
- Check Stripe dashboard for invoice items
- Verify performance fee recorded
- Check customer created (if new)

**Verify Database:**
```sql
-- Check billing records
SELECT * FROM billing_records WHERE lead_id = 'LEAD_UUID';
```

---

### **Test 6: LinkedIn Research**

**Verify LinkedIn Integration:**
- Check ResearcherAgent logs
- Verify LinkedIn API calls made
- Check research data returned

**Note:** Requires valid LinkedIn access token and API permissions.

---

## 📊 TEST CHECKLIST

### **Infrastructure** ✅
- [ ] Redis running and accessible
- [ ] FastAPI server running on port 8081
- [ ] Node.js worker running and listening
- [ ] All environment variables set

### **Basic Operations** ✅
- [ ] Health check passes
- [ ] Can import leads
- [ ] Can start campaign
- [ ] Jobs queued to Redis
- [ ] Worker processes jobs
- [ ] Messages sent via SendGrid/Twilio
- [ ] Database updated correctly

### **Advanced Operations** ✅
- [ ] LinkedIn research works
- [ ] Stripe billing works
- [ ] Meeting booking works
- [ ] Reply handling works
- [ ] Error handling works

---

## 🐛 TROUBLESHOOTING

### **Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping

# Check connection settings
echo $REDIS_HOST
echo $REDIS_PORT
```

### **FastAPI Server Won't Start**
```bash
# Check port availability
netstat -an | findstr 8081

# Check Python dependencies
pip install -r backend/crewai_agents/requirements.txt
```

### **Worker Not Processing Jobs**
```bash
# Check Redis queue
redis-cli LLEN message_scheduler_queue:waiting

# Check worker logs for errors
# Verify environment variables set
```

### **Messages Not Sending**
```bash
# Check SendGrid API key
echo $SENDGRID_API_KEY

# Check Twilio credentials
echo $TWILIO_ACCOUNT_SID

# Check worker logs for API errors
```

---

## 🎯 SUCCESS CRITERIA

**Test Passes When:**
- ✅ Lead imported successfully
- ✅ Campaign started successfully
- ✅ Job queued to Redis
- ✅ Worker processes job
- ✅ Message sent via SendGrid/Twilio
- ✅ Database updated
- ✅ No errors in logs

---

## 📝 TEST RESULTS TEMPLATE

```
Test Date: [DATE]
Tester: [NAME]

Infrastructure:
- Redis: ✅ / ❌
- FastAPI: ✅ / ❌
- Worker: ✅ / ❌

Tests:
- Health Check: ✅ / ❌
- Lead Import: ✅ / ❌
- Campaign Start: ✅ / ❌
- Message Delivery: ✅ / ❌
- Billing: ✅ / ❌
- LinkedIn Research: ✅ / ❌

Issues Found:
- [List any issues]

Overall Status: ✅ PASS / ❌ FAIL
```

---

## 🚀 NEXT STEPS

After successful E2E testing:
1. Fix any issues found
2. Run load tests (100+ leads)
3. Deploy to staging
4. Run production smoke tests
5. **LAUNCH PILOT!** 🎉
