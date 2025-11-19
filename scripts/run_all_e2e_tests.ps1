# End-to-End Test Suite for Rekindle.ai
# Tests the complete flow: Import → Campaign → Message Send

param(
    [string]$FastAPIUrl = "http://localhost:8081",
    [string]$RedisHost = "127.0.0.1",
    [int]$RedisPort = 6379
)

$ErrorActionPreference = "Stop"

Write-Host "🧪 REKINDLE.AI E2E TEST SUITE" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test Results
$testResults = @{
    "Health Checks" = $false
    "Lead Import" = $false
    "Campaign Start" = $false
    "Redis Queue" = $false
    "Message Delivery" = $false
}

# ============================================================================
# TEST 1: Health Checks
# ============================================================================

Write-Host "📋 Test 1: Health Checks" -ForegroundColor Yellow

# Check Redis
Write-Host "  Checking Redis..." -NoNewline
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌ Redis not responding" -ForegroundColor Red
        $testResults["Health Checks"] = $false
    }
} catch {
    Write-Host " ❌ Redis not accessible" -ForegroundColor Red
    $testResults["Health Checks"] = $false
}

# Check FastAPI
Write-Host "  Checking FastAPI Server..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$FastAPIUrl/health" -Method Get -TimeoutSec 5
    if ($response.status -eq "ok") {
        Write-Host " ✅" -ForegroundColor Green
        $testResults["Health Checks"] = $true
        Write-Host "    Database: $($response.database_connection)" -ForegroundColor Gray
    } else {
        Write-Host " ❌ Server unhealthy" -ForegroundColor Red
        $testResults["Health Checks"] = $false
    }
} catch {
    Write-Host " ❌ Server not responding" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    Write-Host "    Make sure FastAPI server is running:" -ForegroundColor Yellow
    Write-Host "      cd backend/crewai_agents" -ForegroundColor Yellow
    Write-Host "      python api_server.py" -ForegroundColor Yellow
    $testResults["Health Checks"] = $false
}

Write-Host ""

# ============================================================================
# TEST 2: Authentication
# ============================================================================

Write-Host "📋 Test 2: Authentication" -ForegroundColor Yellow

$testEmail = "e2e_test_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$testPassword = "TestPass123!"

Write-Host "  Creating test user..." -NoNewline
try {
    $signupBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $signupResponse = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/auth/signup" `
        -Method Post `
        -Body $signupBody `
        -ContentType "application/json" `
        -ErrorAction Stop

    $authToken = $signupResponse.access_token
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "    Token: $($authToken.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    Write-Host "    Skipping remaining tests..." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================================================
# TEST 3: Lead Import
# ============================================================================

Write-Host "📋 Test 3: Lead Import" -ForegroundColor Yellow

$testLead = @{
    first_name = "John"
    last_name = "Doe"
    email = "john.doe.e2e@example.com"
    company = "Acme Corp"
    industry = "SaaS"
    company_size = "50-200"
    lead_score = 75
    custom_fields = @{
        acv = 5000
    }
} | ConvertTo-Json

Write-Host "  Importing test lead..." -NoNewline
try {
    $headers = @{
        "Authorization" = "Bearer $authToken"
        "Content-Type" = "application/json"
    }

    $importResponse = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/leads/import" `
        -Method Post `
        -Headers $headers `
        -Body "[$testLead]" `
        -ErrorAction Stop

    if ($importResponse.success -and $importResponse.imported_count -eq 1) {
        $leadId = $importResponse.leads[0].id
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "    Lead ID: $leadId" -ForegroundColor Gray
        $testResults["Lead Import"] = $true
    } else {
        Write-Host " ❌ Import failed" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    $testResults["Lead Import"] = $false
}

Write-Host ""

# ============================================================================
# TEST 4: Campaign Start
# ============================================================================

if ($testResults["Lead Import"] -and $leadId) {
    Write-Host "📋 Test 4: Campaign Start" -ForegroundColor Yellow

    $campaignBody = @{
        lead_ids = @($leadId)
    } | ConvertTo-Json

    Write-Host "  Starting campaign..." -NoNewline
    try {
        $campaignResponse = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/campaigns/start" `
            -Method Post `
            -Headers $headers `
            -Body $campaignBody `
            -ErrorAction Stop

        if ($campaignResponse.success -and $campaignResponse.campaigns_started -gt 0) {
            Write-Host " ✅" -ForegroundColor Green
            Write-Host "    Campaigns started: $($campaignResponse.campaigns_started)" -ForegroundColor Gray
            $testResults["Campaign Start"] = $true
        } else {
            Write-Host " ❌ Campaign start failed" -ForegroundColor Red
        }
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        $testResults["Campaign Start"] = $false
    }

    Write-Host ""
}

# ============================================================================
# TEST 5: Redis Queue Verification
# ============================================================================

Write-Host "📋 Test 5: Redis Queue Verification" -ForegroundColor Yellow

Write-Host "  Checking queue length..." -NoNewline
try {
    $queueLength = redis-cli LLEN message_scheduler_queue:waiting 2>&1
    if ($queueLength -match "^\d+$") {
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "    Jobs in queue: $queueLength" -ForegroundColor Gray
        $testResults["Redis Queue"] = $true
    } else {
        Write-Host " ❌ Could not read queue" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    Write-Host "    Make sure Redis is running and queue name is correct" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# TEST 6: Worker Status Check
# ============================================================================

Write-Host "📋 Test 6: Worker Status" -ForegroundColor Yellow
Write-Host "  ⚠️  Manual verification required:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Monitor these logs:" -ForegroundColor Cyan
Write-Host "    1. FastAPI: Look for 'ORCHESTRATION_SUCCESS' and 'redis_result=Job enqueued'" -ForegroundColor Gray
Write-Host "    2. Worker: Look for 'WORKER_JOB_START' → 'WORKER_DELIVERY_SUCCESS' → 'WORKER_JOB_SUCCESS'" -ForegroundColor Gray
Write-Host ""
Write-Host "  External verification:" -ForegroundColor Cyan
Write-Host "    3. SendGrid Dashboard: Check for sent email" -ForegroundColor Gray
Write-Host "    4. Twilio Dashboard: Check for sent SMS/WhatsApp" -ForegroundColor Gray
Write-Host "    5. Database: Verify messages.status = 'sent'" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# TEST RESULTS SUMMARY
# ============================================================================

Write-Host "📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$total = $testResults.Count

foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "  $($test.Key): $status" -ForegroundColor $color
    if ($test.Value) { $passed++ }
}

Write-Host ""
Write-Host "Results: $passed/$total tests passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
Write-Host ""

if ($passed -eq $total) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Verify messages were sent in SendGrid/Twilio dashboards" -ForegroundColor Gray
    Write-Host "  2. Check database for updated lead status" -ForegroundColor Gray
    Write-Host "  3. Review worker logs for any warnings" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "  1. Check all services are running (Redis, FastAPI, Worker)" -ForegroundColor Gray
    Write-Host "  2. Verify all environment variables are set" -ForegroundColor Gray
    Write-Host "  3. Check service logs for errors" -ForegroundColor Gray
    exit 1
}

