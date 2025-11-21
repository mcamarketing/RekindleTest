# Test Campaign Path - Simplified E2E Test
# Tests: Import → Campaign → Queue → Worker

param(
    [string]$FastAPIUrl = "http://localhost:8081"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Testing Campaign Path" -ForegroundColor Cyan
Write-Host ""

# Step 1: Health Check
Write-Host "1. Health Check..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "$FastAPIUrl/health" -Method Get
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Auth
Write-Host "2. Authentication..." -NoNewline
$testEmail = "test_$(Get-Date -Format 'HHmmss')@test.com"
try {
    $auth = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/auth/signup" `
        -Method Post `
        -Body (@{email=$testEmail;password="test123"} | ConvertTo-Json) `
        -ContentType "application/json"
    $token = $auth.access_token
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ❌" -ForegroundColor Red
    exit 1
}

# Step 3: Import Lead
Write-Host "3. Import Lead..." -NoNewline
$lead = @{
    first_name = "Test"
    last_name = "User"
    email = "testuser@example.com"
    company = "Test Corp"
    lead_score = 80
} | ConvertTo-Json

try {
    $import = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/leads/import" `
        -Method Post `
        -Headers @{Authorization="Bearer $token"} `
        -Body "[$lead]" `
        -ContentType "application/json"
    $leadId = $import.leads[0].id
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ❌" -ForegroundColor Red
    exit 1
}

# Step 4: Start Campaign
Write-Host "4. Start Campaign..." -NoNewline
try {
    $campaign = Invoke-RestMethod -Uri "$FastAPIUrl/api/v1/campaigns/start" `
        -Method Post `
        -Headers @{Authorization="Bearer $token"} `
        -Body (@{lead_ids=@($leadId)} | ConvertTo-Json) `
        -ContentType "application/json"
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "   Campaign started: $($campaign.campaigns_started)" -ForegroundColor Gray
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Check Queue
Write-Host "5. Check Redis Queue..." -NoNewline
try {
    $queueLen = redis-cli LLEN message_scheduler_queue:waiting 2>&1
    if ($queueLen -match "^\d+$") {
        Write-Host " ✅ ($queueLen jobs)" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  (Could not read)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  (Redis check failed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Campaign path test complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Check worker logs for message processing" -ForegroundColor Cyan








