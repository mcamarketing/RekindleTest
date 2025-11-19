# Pre-Flight Check - Verify all services are ready for E2E testing

Write-Host "🔍 PRE-FLIGHT CHECKLIST" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

$allReady = $true

# Check Redis
Write-Host "1. Redis Server..." -NoNewline
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host " ✅ Running" -ForegroundColor Green
    } else {
        Write-Host " ❌ Not responding" -ForegroundColor Red
        Write-Host "   Start with: redis-server" -ForegroundColor Yellow
        $allReady = $false
    }
} catch {
    Write-Host " ❌ Not accessible" -ForegroundColor Red
    Write-Host "   Start with: redis-server" -ForegroundColor Yellow
    $allReady = $false
}

# Check FastAPI
Write-Host "2. FastAPI Server..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8081/health" -Method Get -TimeoutSec 2
    if ($response.status -eq "ok") {
        Write-Host " ✅ Running on port 8081" -ForegroundColor Green
    } else {
        Write-Host " ❌ Unhealthy" -ForegroundColor Red
        $allReady = $false
    }
} catch {
    Write-Host " ❌ Not running" -ForegroundColor Red
    Write-Host "   Start with:" -ForegroundColor Yellow
    Write-Host "     cd backend/crewai_agents" -ForegroundColor Yellow
    Write-Host "     python api_server.py" -ForegroundColor Yellow
    $allReady = $false
}

# Check Node Worker (can't easily check, but verify process)
Write-Host "3. Node.js Worker..." -NoNewline
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host " ✅ Node.js processes running" -ForegroundColor Green
    Write-Host "   (Verify worker is listening for jobs)" -ForegroundColor Gray
} else {
    Write-Host " ⚠️  No Node.js processes found" -ForegroundColor Yellow
    Write-Host "   Start with:" -ForegroundColor Yellow
    Write-Host "     cd backend/node_scheduler_worker" -ForegroundColor Yellow
    Write-Host "     npm start" -ForegroundColor Yellow
}

# Check Environment Files
Write-Host "4. Environment Files..." -NoNewline
$apiEnv = Test-Path "backend/crewai_agents/.env"
$workerEnv = Test-Path "backend/node_scheduler_worker/.env"
if ($apiEnv -and $workerEnv) {
    Write-Host " ✅ Found" -ForegroundColor Green
} else {
    Write-Host " ⚠️  Missing" -ForegroundColor Yellow
    if (-not $apiEnv) {
        Write-Host "   Missing: backend/crewai_agents/.env" -ForegroundColor Yellow
    }
    if (-not $workerEnv) {
        Write-Host "   Missing: backend/node_scheduler_worker/.env" -ForegroundColor Yellow
    }
}

# Check Test Script
Write-Host "5. Test Script..." -NoNewline
if (Test-Path "scripts/run_all_e2e_tests.ps1") {
    Write-Host " ✅ Ready" -ForegroundColor Green
} else {
    Write-Host " ❌ Missing" -ForegroundColor Red
    $allReady = $false
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan

if ($allReady) {
    Write-Host "✅ ALL CHECKS PASSED - READY FOR TESTING" -ForegroundColor Green
    Write-Host ""
    Write-Host "Execute:" -ForegroundColor Cyan
    Write-Host "  cd scripts" -ForegroundColor White
    Write-Host "  .\run_all_e2e_tests.ps1" -ForegroundColor White
} else {
    Write-Host "❌ SOME CHECKS FAILED - FIX BEFORE TESTING" -ForegroundColor Red
    Write-Host ""
    Write-Host "See instructions above to start missing services." -ForegroundColor Yellow
}

Write-Host ""






