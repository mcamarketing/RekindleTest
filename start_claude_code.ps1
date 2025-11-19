# Claude Code Startup Script
# Run this script to launch Claude Code interactively

Write-Host "🚀 Starting Claude Code..." -ForegroundColor Cyan
Write-Host ""

# Ensure Node.js is in PATH
$env:Path = "$env:Path;C:\Program Files\nodejs"

# Check if Claude Code is installed
$claudePath = "$env:APPDATA\npm\claude.cmd"
if (Test-Path $claudePath) {
    Write-Host "✅ Claude Code found at: $claudePath" -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🎯 Launching Claude Code..." -ForegroundColor Cyan
    Write-Host "   (You can now interact with Claude Code directly)" -ForegroundColor Gray
    Write-Host ""
    
    # Launch Claude Code interactively
    & $claudePath
} else {
    Write-Host "❌ Claude Code not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Claude Code:" -ForegroundColor Yellow
    Write-Host "  npm install -g @anthropic-ai/claude-code" -ForegroundColor White
    Write-Host ""
}

