# Git Setup Script
# Run this to configure git and push to GitHub

Write-Host "=== Git Setup for Rekindle.ai ===" -ForegroundColor Cyan
Write-Host ""

# Get user info
$userName = Read-Host "Enter your name (for git commits)"
$userEmail = Read-Host "Enter your email (for git commits)"

# Configure git
Write-Host "`nConfiguring git..." -ForegroundColor Yellow
git config --global user.name "$userName"
git config --global user.email "$userEmail"
git config --global init.defaultBranch main
git config core.autocrlf true

Write-Host "✓ Git configured" -ForegroundColor Green

# Create commit
Write-Host "`nCreating initial commit..." -ForegroundColor Yellow
git commit -m "feat: Initial commit with Phase 0 production security fixes

BREAKING CHANGES:
- Supabase credentials must be set via environment variables
- API URL must be configured in production deployments
- CALENDAR_ENCRYPTION_KEY required for OAuth integrations
- SENDGRID_WEBHOOK_VERIFICATION_KEY required for webhooks

Security Improvements (Phase 0):
- Remove hardcoded Supabase credentials from frontend
- Fix API URL configuration with fail-fast validation
- Implement atomic database transactions
- Enable webhook signature verification
- Encrypt OAuth tokens at rest with key rotation support
- Add health endpoint rate limiting (60/minute)
- Add comprehensive smoke tests (15+ test cases)

Files Modified:
- src/lib/supabase.ts - Environment variable validation
- src/lib/api.ts - Production-safe API URL handling
- backend/crewai_agents/api_server.py - OAuth encryption + rate limiting
- backend/crewai_agents/webhooks.py - Signature verification
- backend/crewai_agents/crews/special_forces_crews.py - Atomic transactions

Files Created:
- backend/crewai_agents/utils/db_transaction.py - Transaction utilities
- backend/crewai_agents/utils/token_encryption.py - OAuth encryption
- backend/crewai_agents/tests/test_phase0_fixes.py - Smoke tests
- PHASE0_FIXES_SUMMARY.md - Implementation summary
- REQUIRED_ENV_VARS.md - Environment setup guide
- ENVIRONMENT_SETUP_GUIDE.md - Complete setup instructions
- .env.example - Frontend environment template

Ready for production deployment after environment configuration.

Co-Authored-By: Claude Code <noreply@anthropic.com>"

Write-Host "✓ Commit created" -ForegroundColor Green

# GitHub setup
Write-Host "`n=== GitHub Setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/new"
Write-Host "2. Repository name: rekindle-ai (or your choice)"
Write-Host "3. Visibility: Private (recommended)"
Write-Host "4. DO NOT initialize with README"
Write-Host "5. Click 'Create repository'"
Write-Host ""

$continue = Read-Host "Have you created the GitHub repository? (y/n)"

if ($continue -eq "y") {
    $githubUsername = Read-Host "Enter your GitHub username"
    $repoName = Read-Host "Enter repository name (e.g., rekindle-ai)"

    Write-Host "`nAdding GitHub remote..." -ForegroundColor Yellow
    git remote add origin "https://github.com/$githubUsername/$repoName.git"

    Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
    Write-Host "You may be prompted for your GitHub credentials." -ForegroundColor Gray
    Write-Host "Use a Personal Access Token, not password." -ForegroundColor Gray
    Write-Host "Create token at: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host ""

    git branch -M main
    git push -u origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "View your repo at: https://github.com/$githubUsername/$repoName" -ForegroundColor Cyan
    } else {
        Write-Host "`n✗ Push failed. Check your credentials and try again." -ForegroundColor Red
        Write-Host "Manual push command:" -ForegroundColor Yellow
        Write-Host "  git push -u origin main" -ForegroundColor Gray
    }
} else {
    Write-Host "`nSkipping push. Run this when ready:" -ForegroundColor Yellow
    Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/rekindle-ai.git" -ForegroundColor Gray
    Write-Host "  git branch -M main" -ForegroundColor Gray
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
