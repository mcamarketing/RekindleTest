# 🧪 Test Scripts

## Quick Start

### **Full E2E Test Suite**
```powershell
.\run_all_e2e_tests.ps1
```

Tests:
- Health checks (Redis, FastAPI)
- Authentication
- Lead import
- Campaign start
- Redis queue verification
- Worker status check

### **Quick Campaign Test**
```powershell
.\test_campaign_path.ps1
```

Simplified test that verifies:
- API is accessible
- Can import lead
- Can start campaign
- Jobs queued to Redis

---

## Prerequisites

1. **Redis running:**
   ```bash
   redis-server
   ```

2. **FastAPI server running:**
   ```bash
   cd backend/crewai_agents
   python api_server.py
   ```

3. **Node.js worker running:**
   ```bash
   cd backend/node_scheduler_worker
   npm start
   ```

4. **Environment variables set** (see `E2E_TESTING_GUIDE.md`)

---

## Expected Output

**Success:**
```
🧪 REKINDLE.AI E2E TEST SUITE
================================

📋 Test 1: Health Checks
  Checking Redis... ✅
  Checking FastAPI Server... ✅

📋 Test 2: Authentication
  Creating test user... ✅

📋 Test 3: Lead Import
  Importing test lead... ✅

📋 Test 4: Campaign Start
  Starting campaign... ✅

📋 Test 5: Redis Queue Verification
  Checking queue length... ✅

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

## Troubleshooting

See `E2E_TESTING_GUIDE.md` for detailed troubleshooting steps.








