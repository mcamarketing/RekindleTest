# 🚀 FastAPI Server Startup Guide

## Prerequisites Check

Before starting the server, ensure:

1. **Python is installed** (Python 3.8+)
   - Check: `python --version` or `py --version` or `python3 --version`
   - If not installed: Download from [python.org](https://www.python.org/downloads/)

2. **Virtual Environment** (Recommended)
   ```powershell
   cd backend/crewai_agents
   python -m venv venv
   
   # Activate on Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   
   # Or on Windows CMD:
   venv\Scripts\activate.bat
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create `.env` file in `backend/crewai_agents/` with:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   TRACKER_API_TOKEN=your_shared_secret_token
   ANTHROPIC_API_KEY=your_anthropic_key
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   STRIPE_MCP_URL=http://mcp-stripe-server
   LINKEDIN_MCP_URL=http://mcp-linkedin-server
   ```

## Start Server

### Option 1: Manual Start (Recommended for Testing)

**PowerShell Terminal:**
```powershell
# Navigate to backend directory
cd C:\Users\Hello\OneDrive\Documents\FUF_APP\backend\crewai_agents

# Activate virtual environment (if using)
.\venv\Scripts\Activate.ps1

# Start server
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8081

# Or using 'py' command if 'python' doesn't work:
py -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8081
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8081 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Option 2: Using PM2 (For Production)

```powershell
# From project root
pm2 start ecosystem.config.js
pm2 logs fastapi-api-server
```

## Verify Server is Running

**In a new PowerShell window:**
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://127.0.0.1:8081/health" -Method Get

# Expected response:
# {"status":"ok","service":"Rekindle Agent Server","uptime":"Running"}
```

Or visit in browser: `http://127.0.0.1:8081/health`

## Set Environment Token for Tests

**In the same terminal where you'll run tests:**
```powershell
$env:TRACKER_API_TOKEN = "your_token_here"
```

**Or set it permanently in `.env` file**

## Run E2E Tests

Once server is running and token is set:

```powershell
# From project root
.\scripts\test_revenue_path.ps1
```

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Or use `py` launcher: `py --version`
- Add Python to PATH during installation

### "ModuleNotFoundError: No module named 'uvicorn'"
- Install dependencies: `pip install -r requirements.txt`
- Ensure virtual environment is activated

### "Port 8081 already in use"
- Stop the existing server (Ctrl+C)
- Or use a different port: `--port 8082`

### "SUPABASE_URL not found"
- Create `.env` file in `backend/crewai_agents/`
- Add all required environment variables

### Server starts but endpoints return 401/403
- Check `TRACKER_API_TOKEN` is set correctly
- Verify token matches what's expected in `.env`

## Next Steps After Server Starts

1. ✅ Server running on http://127.0.0.1:8081
2. ✅ Health check returns 200 OK
3. ✅ Set TRACKER_API_TOKEN environment variable
4. ✅ Run test data SQL in Supabase
5. ✅ Execute: `.\scripts\test_revenue_path.ps1`

---

**Ready to test when server is running!**

