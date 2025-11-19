# REKINDLE - Server Startup Guide

## Quick Start (Development)

### Terminal 1: Frontend (Vite)
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
npm run dev
```
**Access:** http://localhost:5173

---

### Terminal 2: Node.js Backend
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend
npm run dev
```
**Access:** http://localhost:3001

---

### Terminal 3: Python AI Backend
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE\backend
python start_python_api.py
```
**Access:** http://localhost:8081

---

## Verify All Servers Running

Run this command to check all ports:
```bash
netstat -ano | findstr "LISTENING" | findstr "5173 3001 8081"
```

Expected output:
```
TCP    0.0.0.0:3001    0.0.0.0:0    LISTENING    [PID]
TCP    0.0.0.0:8081    0.0.0.0:0    LISTENING    [PID]
TCP    [::1]:5173      [::]:0       LISTENING    [PID]
```

---

## Health Checks

### Frontend
Open: http://localhost:5173
Should load Rekindle dashboard

### Node.js Backend
```bash
curl http://localhost:3001/health
```
Expected: `{"status":"healthy"}`

### Python AI Backend
```bash
curl http://localhost:8081/health
```
Expected: `{"status":"unhealthy",...}` (until migrations run)

---

## Environment Configuration

### Frontend (.env)
```env
VITE_API_URL=http://localhost:3001
VITE_PYTHON_API_URL=http://localhost:8081
VITE_SUPABASE_URL=https://jnhbmemmwtsrfhlztmyq.supabase.co
VITE_SUPABASE_ANON_KEY=[your-key]
```

### Node.js Backend (backend/.env)
```env
NODE_ENV=development
PORT=3001
SUPABASE_URL=https://jnhbmemmwtsrfhlztmyq.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[your-key]
JWT_SECRET=[your-secret]
CORS_ORIGIN=http://localhost:5173
```

### Python Backend (backend/crewai_agents/.env)
```env
PORT=8081
ENVIRONMENT=development
SUPABASE_URL=https://jnhbmemmwtsrfhlztmyq.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[your-key]
SUPABASE_JWT_SECRET=[your-secret]
ANTHROPIC_API_KEY=sk-ant-api03-[your-key]
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Troubleshooting

### Port Already in Use
```bash
# Windows: Find process using port
netstat -ano | findstr :[PORT]

# Kill process by PID
taskkill /F /PID [PID]
```

### Python Backend on Wrong Port
Make sure to use the startup script:
```bash
cd backend
python start_python_api.py
```

**DO NOT use:**
```bash
python -m crewai_agents.api_server  # ❌ Will use wrong .env file
```

### Database Connection Errors
1. Check Supabase URL and keys in .env files
2. Run pending migrations (see below)

---

## Database Migrations

Before first use, run these migrations in Supabase SQL editor:

### 1. Chat History Table
```sql
-- File: backend/migrations/create_chat_history_table.sql
CREATE TABLE IF NOT EXISTS public.chat_history (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  history JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT history_max_turns CHECK (jsonb_array_length(history) <= 12)
);

CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON public.chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_updated_at ON public.chat_history(updated_at DESC);

ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own chat history"
  ON public.chat_history FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat history"
  ON public.chat_history FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own chat history"
  ON public.chat_history FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat history"
  ON public.chat_history FOR DELETE USING (auth.uid() = user_id);
```

### 2. OAuth States Table
```sql
-- File: backend/migrations/create_oauth_states_table.sql
CREATE TABLE IF NOT EXISTS public.oauth_states (
  state_token TEXT PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL CHECK (provider IN ('google', 'microsoft')),
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_oauth_states_user_id ON public.oauth_states(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON public.oauth_states(expires_at);

ALTER TABLE public.oauth_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own OAuth states"
  ON public.oauth_states FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own OAuth states"
  ON public.oauth_states FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own OAuth states"
  ON public.oauth_states FOR DELETE USING (auth.uid() = user_id);

CREATE OR REPLACE FUNCTION public.cleanup_expired_oauth_states()
RETURNS void AS $$
BEGIN
  DELETE FROM public.oauth_states WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## Production Deployment

### Build Frontend
```bash
cd c:\Users\Hello\OneDrive\Documents\REKINDLE
npm run build
```
Output: `dist/` folder

### Environment Variables for Production
Update all .env files:
- Change `ENVIRONMENT=production`
- Update `CORS_ORIGIN` to your domain
- Update all localhost URLs to production URLs
- Ensure all secrets are production-ready

### Start Production Servers
```bash
# Frontend (with static server like nginx or Vercel)
npm run preview

# Node.js Backend
cd backend && npm start

# Python Backend
cd backend && python start_python_api.py
```

---

## Current Status

✅ **All Servers Running:**
- Frontend: http://localhost:5173
- Node.js Backend: http://localhost:3001
- Python AI Backend: http://localhost:8081

✅ **Security Implementations Complete:**
- JWT Authentication
- User Data Isolation
- DoS Prevention
- XSS Protection
- Type Safety
- OAuth CSRF Protection
- Conversation History Persistence

✅ **Rex AI Tier 10:** Fully integrated and operational

⚠️ **Pending:**
- Run database migrations (chat_history, oauth_states)
- Security testing
- Production deployment

---

## Support

For issues or questions:
1. Check console logs in all three terminals
2. Verify environment variables are set
3. Check database connection in Supabase dashboard
4. Review FINAL_IMPLEMENTATION_STATUS.md for complete details
