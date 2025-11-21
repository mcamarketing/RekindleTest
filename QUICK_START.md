# 🚀 Rekindle Quick Start Guide

## Fix Connection Refused Error

The `ERR_CONNECTION_REFUSED` error means the backend server isn't running. Follow these steps:

### Option 1: Use Startup Script (Recommended)

**Windows:**
```powershell
.\start-dev.ps1
```

**Mac/Linux:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

This will automatically:
- Check dependencies
- Start backend on port 3001
- Start frontend on port 5173
- Open separate windows for each server

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
cd backend
npm install
npm run dev
```

**Terminal 2 - Frontend:**
```powershell
npm install
npm run dev
```

### Verify Servers Are Running

1. **Backend Health Check:**
   ```powershell
   curl http://localhost:3001/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Frontend:**
   Open browser: `http://localhost:5173`

3. **Check Console:**
   - Backend terminal should show: `✅ Backend server running on port 3001`
   - Frontend terminal should show: `Local: http://localhost:5173`

---

## Environment Setup

### Frontend (.env in root)
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:3001/api
```

### Backend (backend/.env)
```env
NODE_ENV=development
PORT=3001
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
CORS_ORIGIN=http://localhost:5173
```

**Get Supabase keys from:** https://app.supabase.com → Your Project → Settings → API

---

## Initialize Database

1. Go to Supabase Dashboard → SQL Editor
2. Run the `initialize_ai_agents.sql` file
3. This creates all 28 AI agents in the database

---

## Meet Rex - Your AI Assistant

Rex is your Rekindle AI Expert widget that:
- **Name:** Rex (Rekindle Expert)
- **Capabilities:** Orchestrates 28 specialized AI agents
- **Features:**
  - Real-time insights and recommendations
  - Campaign planning assistance
  - Lead analysis
  - Performance optimization tips
  - FAQ system
  - Voice input ready

Rex appears as a floating widget in the bottom-right corner of the app.

---

## Troubleshooting

### Port Already in Use

**Windows:**
```powershell
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -ti:3001 | xargs kill
```

### Backend Won't Start

1. Check `backend/.env` exists and has correct values
2. Run `cd backend && npm install`
3. Check Node.js version: `node --version` (should be 18+)

### Frontend Can't Connect

1. Verify backend is running: `curl http://localhost:3001/health`
2. Check CORS_ORIGIN in `backend/.env` matches frontend URL
3. Check browser console for errors

### Database Connection Issues

1. Verify Supabase credentials in `.env` files
2. Check Supabase project is active
3. Run `initialize_ai_agents.sql` in Supabase SQL Editor

---

## Next Steps

1. ✅ Start both servers
2. ✅ Initialize database agents
3. ✅ Login to the app
4. ✅ Import your first leads
5. ✅ Create your first campaign
6. ✅ Chat with Rex about features

See `APP_COMPLETION_CHECKLIST.md` for full feature checklist.

---

## Support

- **Rex Widget:** Click the chat icon in bottom-right
- **Documentation:** See `APP_COMPLETION_CHECKLIST.md`
- **Backend Guide:** See `BACKEND_INTEGRATION_GUIDE.md`




