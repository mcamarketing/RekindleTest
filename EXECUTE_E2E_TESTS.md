# 🚀 EXECUTE E2E TESTS - FINAL VALIDATION

## ⚡ PRE-FLIGHT CHECKLIST (10 MINUTES)

### **1. Start Services**

**Terminal 1: Redis**
```bash
redis-server
# Verify: redis-cli ping (should return PONG)
```

**Terminal 2: FastAPI Server**
```bash
cd backend/crewai_agents
python api_server.py
# Should see: "Rekindle API Server started successfully"
# Watch for: "ORCHESTRATION_SUCCESS" and "redis_result=Job enqueued"
```

**Terminal 3: Node.js Worker**
```bash
cd backend/node_scheduler_worker
npm install  # If not already done
npm start
# Should see: "Worker started successfully"
# Watch for: "WORKER_JOB_START" → "WORKER_DELIVERY_SUCCESS" → "WORKER_JOB_SUCCESS"
```

### **2. Set Environment Variables**

**FastAPI Server** (Terminal 2):
```bash
# Ensure .env file exists in backend/crewai_agents/
# Or export variables:
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
export ANTHROPIC_API_KEY=...
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
```

**Node.js Worker** (Terminal 3):
```bash
# Ensure .env file exists in backend/node_scheduler_worker/
# Or export variables:
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
export SENDGRID_API_KEY=...
export TWILIO_ACCOUNT_SID=...
export TWILIO_AUTH_TOKEN=...
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
```

### **3. Load Test Data**

**In Supabase SQL Editor:**
```sql
-- Run scripts/setup_test_data.sql
```

Or manually:
```sql
INSERT INTO leads (id, user_id, first_name, last_name, email, company, lead_score, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM profiles LIMIT 1),
    'John',
    'Doe',
    'john.doe.e2e@example.com',
    'Acme Corp',
    75,
    'new'
);
```

---

## 🧪 EXECUTE THE TEST

**Terminal 4: Run Test Suite**
```powershell
cd scripts
.\run_all_e2e_tests.ps1
```

---

## 👀 CRITICAL VALIDATION (MONITOR THESE)

### **FastAPI Logs (Terminal 2)**
**Look for:**
- ✅ `ORCHESTRATION_SUCCESS: lead_id=..., messages_queued=...`
- ✅ `redis_result=Job enqueued: X messages for lead ...`

**If missing:** Campaign workflow didn't complete or Redis queue failed.

### **Node Worker Logs (Terminal 3)**
**Look for sequence:**
1. ✅ `WORKER_JOB_START` (job picked up)
2. ✅ `WORKER_DELIVERY_SUCCESS` (message sent)
3. ✅ `WORKER_JOB_SUCCESS` (job completed)

**If missing:** Worker not processing jobs or API calls failing.

### **External Dashboards (REAL PROOF)**

**SendGrid Dashboard:**
- Go to: https://app.sendgrid.com/activity
- Look for: Email sent to test lead
- Verify: Subject, body, recipient match test data

**Twilio Dashboard:**
- Go to: https://console.twilio.com/
- Look for: SMS/WhatsApp sent
- Verify: Message content matches test data

### **Database Verification**

**In Supabase SQL Editor:**
```sql
-- Check messages table
SELECT 
    id,
    lead_id,
    channel,
    status,
    sent_at,
    external_message_id
FROM messages
WHERE lead_id IN (
    SELECT id FROM leads WHERE email LIKE '%e2e%' OR email LIKE '%test%'
)
ORDER BY created_at DESC
LIMIT 10;

-- Should show: status = 'sent', sent_at IS NOT NULL

-- Check lead status
SELECT 
    id,
    email,
    status,
    total_messages_sent,
    last_contact_date
FROM leads
WHERE email LIKE '%e2e%' OR email LIKE '%test%';

-- Should show: status = 'campaign_active', total_messages_sent > 0
```

---

## ✅ SUCCESS CRITERIA

**Test Passes When:**
- ✅ All 5 automated tests pass
- ✅ FastAPI logs show `ORCHESTRATION_SUCCESS`
- ✅ FastAPI logs show `redis_result=Job enqueued`
- ✅ Worker logs show `WORKER_JOB_START`
- ✅ Worker logs show `WORKER_DELIVERY_SUCCESS`
- ✅ Worker logs show `WORKER_JOB_SUCCESS`
- ✅ SendGrid dashboard shows sent email
- ✅ Twilio dashboard shows sent SMS/WhatsApp (if SMS/WhatsApp channel used)
- ✅ Database shows `messages.status = 'sent'`
- ✅ Database shows `leads.total_messages_sent > 0`

---

## 🐛 TROUBLESHOOTING

### **FastAPI: No ORCHESTRATION_SUCCESS**
- Check: Is `orchestration_service.run_full_campaign()` being called?
- Check: Are there errors in FastAPI logs?
- Fix: Verify environment variables, check database connection

### **FastAPI: No redis_result=Job enqueued**
- Check: Is Redis connected?
- Check: Is `add_message_job()` being called?
- Fix: Verify Redis connection, check `redis_queue.py` logs

### **Worker: No WORKER_JOB_START**
- Check: Is worker connected to Redis?
- Check: Are jobs in queue? (`redis-cli LLEN message_scheduler_queue:waiting`)
- Fix: Verify Redis connection, check queue name matches

### **Worker: No WORKER_DELIVERY_SUCCESS**
- Check: Are SendGrid/Twilio API keys set?
- Check: Are there API errors in worker logs?
- Fix: Verify API credentials, check API rate limits

### **Database: messages.status != 'sent'**
- Check: Did `logMessage()` function run?
- Check: Are there database errors in worker logs?
- Fix: Verify Supabase connection, check table permissions

---

## 📊 EXPECTED TEST OUTPUT

```
🧪 REKINDLE.AI E2E TEST SUITE
================================

📋 Test 1: Health Checks
  Checking Redis... ✅
  Checking FastAPI Server... ✅
    Database: successful

📋 Test 2: Authentication
  Creating test user... ✅
    Token: eyJhbGciOiJIUzI1NiIs...

📋 Test 3: Lead Import
  Importing test lead... ✅
    Lead ID: 00000000-0000-0000-0000-000000000100

📋 Test 4: Campaign Start
  Starting campaign... ✅
    Campaigns started: 1

📋 Test 5: Redis Queue Verification
  Checking queue length... ✅
    Jobs in queue: 1

📋 Test 6: Worker Status
  ⚠️  Manual verification required:
    1. FastAPI: Look for 'ORCHESTRATION_SUCCESS' and 'redis_result=Job enqueued'
    2. Worker: Look for 'WORKER_JOB_START' → 'WORKER_DELIVERY_SUCCESS' → 'WORKER_JOB_SUCCESS'
    3. SendGrid Dashboard: Check for sent email
    4. Twilio Dashboard: Check for sent SMS/WhatsApp
    5. Database: Verify messages.status = 'sent'

📊 TEST RESULTS SUMMARY
========================
  Health Checks: ✅ PASS
  Lead Import: ✅ PASS
  Campaign Start: ✅ PASS
  Redis Queue: ✅ PASS

Results: 4/4 tests passed

🎉 ALL TESTS PASSED!
```

---

## 🎯 EXECUTE NOW

**Ready to run? Execute:**

```powershell
cd scripts
.\run_all_e2e_tests.ps1
```

**Then monitor all three service terminals for the log markers above.**

**This is the final validation. Everything else is theoretical until this passes.** 🚀









