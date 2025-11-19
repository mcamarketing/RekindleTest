# Simple Server Starter - Just run this!

Write-Host "`n🚀 Starting Rekindle Servers...`n" -ForegroundColor Cyan

# Kill any existing node processes on these ports
Write-Host "Cleaning up old processes..." -ForegroundColor Yellow
Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start Backend
Write-Host "`n📦 Starting Backend (port 3001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '🔧 BACKEND SERVER' -ForegroundColor Green; Write-Host 'Port: 3001' -ForegroundColor Cyan; Write-Host ''; npm run dev"

# Wait a bit
Start-Sleep -Seconds 4

# Start Frontend  
Write-Host "📦 Starting Frontend (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🎨 FRONTEND SERVER' -ForegroundColor Green; Write-Host 'Port: 5173' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Write-Host "`n✅ Servers starting in separate windows!`n" -ForegroundColor Green
Write-Host "📊 Backend:  http://localhost:3001" -ForegroundColor Cyan
Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "`n💡 Wait 10-15 seconds, then open http://localhost:5173 in your browser`n" -ForegroundColor Yellow


