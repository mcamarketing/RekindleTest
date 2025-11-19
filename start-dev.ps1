# Rekindle Development Startup Script
# Starts both frontend and backend servers

Write-Host "🚀 Starting Rekindle Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

# Check if ports are available
if (Test-Port -Port 3001) {
    Write-Host "⚠️  Port 3001 is already in use. Backend may already be running." -ForegroundColor Yellow
}

if (Test-Port -Port 5173) {
    Write-Host "⚠️  Port 5173 is already in use. Frontend may already be running." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Installing dependencies if needed..." -ForegroundColor Cyan

# Install frontend dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Install backend dependencies
if (-not (Test-Path "backend\node_modules")) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "🔧 Starting servers..." -ForegroundColor Cyan
Write-Host ""

# Start backend in a new window
Write-Host "Starting backend server on port 3001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '🔧 Backend Server' -ForegroundColor Cyan; Write-Host ''; npm run dev" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting frontend server on port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🎨 Frontend Server' -ForegroundColor Cyan; Write-Host ''; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Servers starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Backend:  http://localhost:3001" -ForegroundColor Cyan
Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tip: Check the PowerShell windows for server logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window (servers will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

