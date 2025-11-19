# 🧪 E2E Testing Summary

## Current Status

✅ **Test Suite Created:**
- Revenue Path E2E Test (`test_revenue_path.ps1`)
- Campaign Path E2E Test (`test_campaign_path.ps1`)
- Master Test Runner (`run_all_e2e_tests.ps1`)
- Prerequisites Checker (`check_prerequisites.ps1`)
- Test Data SQL (`setup_test_data.sql`)

✅ **Documentation:**
- Comprehensive E2E Testing Guide (`E2E_TESTING_GUIDE.md`)
- Quick Start Guide (`QUICK_START_TESTING.md`)
- Deployment Checklist (`DEPLOYMENT_CHECKLIST.md`)

## Next Steps to Run Tests

### 1. Start FastAPI Server
```powershell
cd backend/crewai_agents
uvicorn api_server:app --reload --port 8081
```

### 2. Setup Test Data
Run `scripts/setup_test_data.sql` in Supabase SQL Editor to create:
- `user_test_billing` (tier: pro, ACV: 5000.00)
- `test_user_revenue_e2e` (for campaign tests)
- `test_lead_campaign_e2e` (with AI insights)
- `test_campaign_e2e_001` (draft campaign)

### 3. Set Environment Variable
```powershell
$env:TRACKER_API_TOKEN = "your_token_here"
```

### 4. Run Tests
```powershell
# Check prerequisites first
.\scripts\check_prerequisites.ps1

# Run all tests
.\scripts\run_all_e2e_tests.ps1
```

## Expected Test Flow: Revenue Path

**Test User:** `user_test_billing`

**Test Steps:**
1. **Calendar Webhook** → `POST /api/calendar/webhook`
   - Payload: Meeting confirmed event
   - Expected: HTTP 200, billing charge triggered
   - Watch logs for: `CALENDAR_WEBHOOK_RECEIVED`, `BILLING_TRIGGER_START`

2. **Billing Charge Calculation:**
   - ACV: 5000.00
   - Fee Rate: 5% (0.05)
   - Min Fee: 50.00
   - Calculated: max(5000 * 0.05, 50.00) = **250.00 GBP**
   - Amount sent to Stripe MCP: **25000** (pence)
   - Watch logs for: `BILLING_TRIGGER_CALC: fee=250.00`

3. **Stripe Webhook** → `POST /api/billing/webhook`
   - Payload: Invoice paid event
   - Expected: HTTP 200, invoice status updated
   - Watch logs for: `STRIPE_WEBHOOK_RECEIVED`, `STRIPE_WEBHOOK_INVOICE_PAID`

4. **Billing Status** → `GET /api/billing/status?user_id=user_test_billing`
   - Expected Response:
     ```json
     {
       "tier": "Pro",
       "status": "active",
       "billing_cycle": "monthly",
       "invoices": [...],
       "stripe_portal_url": "..."
     }
     ```

## What to Monitor

### FastAPI Logs Should Show:
```
CALENDAR_WEBHOOK_RECEIVED: user_id=user_test_billing, event_type=meeting.confirmed
BILLING_TRIGGER_START: user_id=user_test_billing, meeting_id=m_xxx
BILLING_TRIGGER_CALC: user_id=user_test_billing, fee=250.00, currency=GBP, acv=5000.00
BILLING_TRIGGER_MCP_REQUEST: url=http://mcp-stripe-server/..., user_id=user_test_billing
STRIPE_WEBHOOK_RECEIVED: event_id=evt_xxx, event_type=invoice.paid
BILLING_STATUS_REQUEST: user_id=user_test_billing
BILLING_STATUS_SUCCESS: user_id=user_test_billing, tier=Pro, status=active
```

### Validation Points:
- ✅ Calendar webhook receives payload
- ✅ Background task queues billing charge
- ✅ Fee calculated correctly (250.00 GBP)
- ✅ Stripe MCP called with 25000 pence
- ✅ Billing webhook processes event
- ✅ Billing status API returns correct tier/status
- ✅ Frontend UI displays subscription correctly

## Ready to Test!

Once you:
1. Start FastAPI server
2. Set TRACKER_API_TOKEN
3. Run setup_test_data.sql

You can execute:
```powershell
.\scripts\test_revenue_path.ps1
```

This will validate the **complete Revenue Path** from meeting booking to billing UI!

---

**Note:** The API server must be running for tests to execute. The prerequisite checker will verify this before running tests.

