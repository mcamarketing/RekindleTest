# 🚀 Quick Start: E2E Testing Guide

## Before You Begin

### Step 1: Start All Services

**Terminal 1 - FastAPI Server:**
```powershell
cd backend/crewai_agents
uvicorn api_server:app --reload --port 8081
```

**Terminal 2 - Node Worker (Optional for Campaign Path):**
```powershell
cd backend/node_scheduler_worker
npm start
```

**Terminal 3 - Frontend (Optional for UI Testing):**
```powershell
npm run dev
```

### Step 2: Set Environment Variable

```powershell
$env:TRACKER_API_TOKEN = "your_tracker_api_token_here"
```

### Step 3: Setup Test Data

Run the SQL script in Supabase SQL Editor:
- Open Supabase Dashboard → SQL Editor
- Run `scripts/setup_test_data.sql`
- This creates:
  - `user_test_billing` (test user for billing)
  - `test_user_revenue_e2e` (test user for campaigns)
  - `test_lead_campaign_e2e` (test lead with AI insights)
  - `test_campaign_e2e_001` (test campaign)

### Step 4: Run Prerequisites Check

```powershell
.\scripts\check_prerequisites.ps1
```

### Step 5: Run E2E Tests

**Run All Tests:**
```powershell
.\scripts\run_all_e2e_tests.ps1
```

**Run Individual Tests:**
```powershell
# Revenue Path only
.\scripts\test_revenue_path.ps1

# Campaign Path only
.\scripts\test_campaign_path.ps1
```

---

## What to Expect

### Revenue Path Test:
1. ✅ Calendar webhook receives meeting booking
2. ✅ Billing charge triggered (25000 pence = £250.00)
3. ✅ Stripe webhook processes invoice
4. ✅ Billing status API returns correct data

**Watch FastAPI logs for:**
- `CALENDAR_WEBHOOK_RECEIVED`
- `BILLING_TRIGGER_START`
- `BILLING_TRIGGER_CALC: fee=250.00`
- `BILLING_TRIGGER_MCP_REQUEST`
- `STRIPE_WEBHOOK_RECEIVED`

### Campaign Path Test:
1. ✅ Campaign launch API accepts request
2. ✅ Orchestration service executes
3. ✅ 5 messages generated
4. ✅ First message enqueued to Redis

**Watch FastAPI logs for:**
- `CAMPAIGN_LAUNCH_START`
- `ORCHESTRATION_START`
- `ORCHESTRATION_GENERATE_SEQUENCE`
- `ORCHESTRATION_SUCCESS`

---

## Troubleshooting

### API Server Not Accessible
- Verify FastAPI is running on port 8081
- Check firewall settings
- Verify no other service is using port 8081

### TRACKER_API_TOKEN Issues
- Must match the token set in FastAPI server environment
- Check `.env` file in `backend/crewai_agents/`

### Test Data Missing
- Re-run `setup_test_data.sql`
- Check Supabase connection
- Verify RLS policies allow service role access

### Redis Connection Failed
- Only needed for Campaign Path (message queuing)
- Can skip if testing Revenue Path only
- Verify Redis is running: `redis-cli ping`

---

## Manual Validation

After automated tests pass, manually verify:

1. **Billing UI** (`http://localhost:5173/billing`):
   - Subscription tier displayed
   - Invoices table visible
   - "Manage Subscription" button works

2. **Database** (Supabase Dashboard):
   - Check `messages` table for generated messages
   - Verify `leads` table has AI insights
   - Check `profiles` table for tier updates

3. **Redis Queue** (if Redis running):
   ```bash
   redis-cli LLEN message_scheduler_queue
   redis-cli LRANGE message_scheduler_queue 0 -1
   ```

---

## Next Steps After Tests Pass

1. ✅ All services running correctly
2. ✅ End-to-end workflows validated
3. ✅ Ready for production deployment
4. ✅ Review `DEPLOYMENT_CHECKLIST.md` for final steps

---

**Status:** Ready for Testing
**Last Updated:** 2024-12-20

