# 🚀 QUICK START - PILOT LAUNCH

## ⚡ 5-MINUTE SETUP

### **1. Install Dependencies**

**Python (FastAPI Server):**
```bash
cd backend/crewai_agents
pip install -r requirements.txt
```

**Node.js (Worker):**
```bash
cd backend/node_scheduler_worker
npm install
```

### **2. Set Environment Variables**

**FastAPI Server** (`backend/crewai_agents/.env`):
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_JWT_SECRET=xxx
ANTHROPIC_API_KEY=sk-ant-xxx
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=xxx
ALLOWED_ORIGINS=http://localhost:5173,https://rekindle.ai
PORT=8081
ENVIRONMENT=production
```

**Node.js Worker** (`backend/node_scheduler_worker/.env`):
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=xxx
REDIS_SCHEDULER_QUEUE=message_scheduler_queue
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@rekindle.ai
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890
WORKER_CONCURRENCY=10
NODE_INSTANCE_ID=worker-001
```

### **3. Start Redis**
```bash
redis-server
# Or use cloud Redis (Redis Cloud, AWS ElastiCache, etc.)
```

### **4. Start Services**

**Terminal 1 - FastAPI Server:**
```bash
cd backend/crewai_agents
python api_server.py
# Should see: "Rekindle API Server started successfully"
```

**Terminal 2 - Node.js Worker:**
```bash
cd backend/node_scheduler_worker
npm start
# Should see: "Worker started successfully"
```

**Terminal 3 - Frontend:**
```bash
npm run dev
# Should see: "Local: http://localhost:5173"
```

### **5. Test End-to-End**

1. **Import Leads:**
   - Go to `/leads/import`
   - Upload CSV or sync CRM
   - Verify leads appear in `/leads`

2. **Start Campaign:**
   - Select leads
   - Click "Start Campaign"
   - Verify API call succeeds

3. **Verify Queue:**
   - Check Redis: `redis-cli LLEN message_scheduler_queue:waiting`
   - Should see jobs queued

4. **Verify Worker:**
   - Check worker logs
   - Should see "Processing message job"
   - Should see "Message sent successfully"

5. **Verify Database:**
   - Check lead status updated
   - Check messages logged

---

## ✅ VERIFICATION

**All Systems Green When:**
- ✅ FastAPI server responds to `/health`
- ✅ Worker logs show "Worker started successfully"
- ✅ Redis connection works
- ✅ Can import leads
- ✅ Can start campaign
- ✅ Messages queue in Redis
- ✅ Worker processes jobs
- ✅ Messages send successfully
- ✅ Lead status updates

---

## 🎯 PILOT LAUNCH CHECKLIST

- [ ] All environment variables set
- [ ] Redis running
- [ ] FastAPI server running
- [ ] Node.js worker running
- [ ] Frontend running
- [ ] End-to-end test passes
- [ ] Can import leads
- [ ] Can start campaigns
- [ ] Messages send successfully
- [ ] Database updates correctly

**READY TO LAUNCH!** 🚀






