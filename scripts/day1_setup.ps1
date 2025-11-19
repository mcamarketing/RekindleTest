# Day 1 Setup Script - Automated Environment Verification (PowerShell)
# Run this to verify all required environment variables are set

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "REKINDLE.AI - Day 1 Setup Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
$envFile = "backend\crewai_agents\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Creating from template..."
    Copy-Item "backend\crewai_agents\.env.example" $envFile
    Write-Host "⚠️  Please fill in your values in $envFile" -ForegroundColor Yellow
    exit 1
}

# Load .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($value -match '^["\'](.*)["\']$') {
            $value = $matches[1]
        }
        $envVars[$key] = $value
    }
}

# Required variables (P0)
$requiredVars = @(
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "OPENAI_API_KEY",
    "SENDGRID_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN"
)

# Optional but recommended (P1)
$recommendedVars = @(
    "REDIS_HOST",
    "REDIS_PORT",
    "SENTRY_DSN",
    "STRIPE_SECRET_KEY"
)

Write-Host "Checking required variables (P0)..." -ForegroundColor Cyan
Write-Host ""

$missingRequired = @()
$missingRecommended = @()

foreach ($var in $requiredVars) {
    if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
        Write-Host "❌ $var`: MISSING" -ForegroundColor Red
        $missingRequired += $var
    } else {
        # Mask sensitive values
        $value = $envVars[$var]
        if ($value.Length -gt 10) {
            $masked = $value.Substring(0, 4) + "..." + $value.Substring($value.Length - 4)
        } else {
            $masked = "***"
        }
        Write-Host "✅ $var`: SET ($masked)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Checking recommended variables (P1)..." -ForegroundColor Cyan
Write-Host ""

foreach ($var in $recommendedVars) {
    if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
        Write-Host "⚠️  $var`: MISSING (recommended)" -ForegroundColor Yellow
        $missingRecommended += $var
    } else {
        Write-Host "✅ $var`: SET" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

if ($missingRequired.Count -gt 0) {
    Write-Host "❌ BLOCKING: Missing required variables" -ForegroundColor Red
    Write-Host "Please set these in $envFile`:"
    foreach ($var in $missingRequired) {
        Write-Host "  - $var" -ForegroundColor Red
    }
    exit 1
}

if ($missingRecommended.Count -gt 0) {
    Write-Host "⚠️  WARNING: Missing recommended variables" -ForegroundColor Yellow
    Write-Host "These are optional but recommended for production:"
    foreach ($var in $missingRecommended) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "You can continue, but some features may not work."
}

Write-Host "✅ All required variables are set!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Deploy to production (Railway/Render)"
Write-Host "2. Configure webhooks (SendGrid/Twilio)"
Write-Host "3. Set up monitoring (Sentry)"
Write-Host "4. Test end-to-end campaign flow"
Write-Host ""
Write-Host "See DAY1_EXECUTION_CHECKLIST.md for details"

