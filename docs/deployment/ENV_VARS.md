# Environment Variables Reference

**Last Updated**: 2025-01-23

This document lists all environment variables used by RekindlePro, organized by category.

---

## Critical (Required for All Environments)

### Database (Supabase)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` | Backend, Frontend |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (BACKEND ONLY - SECRET!) | `eyJhbGciOiJ...` | Backend API, Worker |
| `SUPABASE_ANON_KEY` | Anonymous/public key (Frontend safe) | `eyJhbGciOiJ...` | Frontend only |
| `SUPABASE_JWT_SECRET` | JWT signing secret | `your-jwt-secret-32-chars-min` | Backend API |

**Security Note**: NEVER use `SUPABASE_SERVICE_ROLE_KEY` in frontend code. Only use `SUPABASE_ANON_KEY` for frontend.

---

### Redis (Queue & Cache)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `REDIS_HOST` | Redis server hostname | `red-xxx.redis.render.com` | Backend, Worker |
| `REDIS_PORT` | Redis server port | `6379` | Backend, Worker |
| `REDIS_PASSWORD` | Redis password (SECRET!) | Generated strong password | Backend, Worker |
| `REDIS_URL` | Full Redis connection URL | `redis://:password@host:6379/0` | Alternative to above |

**Generation**: Use `openssl rand -base64 32` for strong password.

---

### OpenAI (LLM)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `OPENAI_API_KEY` | OpenAI API key (SECRET!) | `sk-proj-...` | Backend, CrewAI Agents |

**Cost Monitoring**: Set budget alerts in OpenAI dashboard (recommended: $100/month for Stage A).

---

## Email & SMS (Third-Party APIs)

### SendGrid (Email Delivery)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `SENDGRID_API_KEY` | SendGrid API key (SECRET!) | `SG.xxxx...` | Backend, Worker |

**Setup**: Create SendGrid account, verify sender domain, generate API key with "Mail Send" permission.

---

### Twilio (SMS Delivery - Optional)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `TWILIO_ACCOUNT_SID` | Twilio account SID | `ACxxxxxxxxxxxxxxx` | Backend, Worker |
| `TWILIO_AUTH_TOKEN` | Twilio auth token (SECRET!) | `your_auth_token` | Backend, Worker |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | `+15551234567` | Worker |

**Note**: Only required if using SMS features. Can be omitted for email-only deployments.

---

## Monitoring & Observability

### Sentry (Error Tracking)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `SENTRY_DSN` | Sentry DSN URL | `https://xxx@sentry.io/123456` | Backend, Frontend |
| `SENTRY_ENVIRONMENT` | Environment name for Sentry | `production`, `staging`, `development` | Backend |

**Setup**: Create Sentry project for backend (FastAPI) and frontend (React), get DSN from project settings.

**Frontend Variable**: Use `VITE_SENTRY_DSN` prefix for Vite to expose to browser.

---

## Application Configuration

### Backend API

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `PORT` | API server port | `8081` | `8000` |
| `NODE_ENV` | Node environment | `production`, `development` | `development` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `https://app.com,https://www.app.com` | `*` (dev only) |
| `APP_URL` | Frontend app URL | `https://yourdomain.com` | `http://localhost:5173` |
| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `ERROR` | `INFO` |

**CORS Security**: In production, NEVER use `*` for `ALLOWED_ORIGINS`. List specific domains.

---

### Frontend (Vite)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `VITE_SUPABASE_URL` | Supabase URL (frontend) | `https://xxxxx.supabase.co` | Frontend (browser) |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key (frontend) | `eyJhbGciOiJ...` | Frontend (browser) |
| `VITE_API_BASE_URL` | Backend API URL | `https://api.yourdomain.com` | Frontend (browser) |
| `VITE_SENTRY_DSN` | Sentry DSN (frontend) | `https://xxx@sentry.io/123456` | Frontend (browser) |

**Vite Prefix**: All frontend env vars MUST start with `VITE_` to be exposed to browser.

---

## Optional / Advanced

### Calendar Integration (Calendly - Optional)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `CALENDLY_API_KEY` | Calendly API token (SECRET!) | `your_calendly_token` | Backend |

**Note**: Only required if using calendar booking features.

---

### Google Calendar (Alternative to Calendly - Optional)

| Variable | Description | Example | Where Used |
|----------|-------------|---------|------------|
| `GOOGLE_CALENDAR_CREDENTIALS` | Google service account JSON | `{"type":"service_account",...}` | Backend |

---

### Security (Advanced)

| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `JWT_SECRET` | JWT signing secret (if not using Supabase JWT) | 32+ character random string | N/A |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per user | `100` | `100` |
| `SESSION_TIMEOUT_MINUTES` | Session timeout | `30` | `30` |

**Generation**: `openssl rand -hex 32` for JWT_SECRET.

---

## Environment-Specific Configurations

### Development (Local)

```bash
# .env (local development)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ... (dev project)
SUPABASE_ANON_KEY=eyJ... (dev project)
SUPABASE_JWT_SECRET=your-dev-jwt-secret

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=local_redis_pass

OPENAI_API_KEY=sk-proj-... (use test key if available)
SENDGRID_API_KEY=SG.test_key

NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
APP_URL=http://localhost:5173

SENTRY_DSN= (leave empty or use dev DSN)
LOG_LEVEL=DEBUG
```

### Staging

```bash
# Render/Railway environment variables (staging)
SUPABASE_URL=https://staging-xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ... (staging project)
# ... same as production but with staging resources

NODE_ENV=staging
ALLOWED_ORIGINS=https://staging.yourdomain.com
APP_URL=https://staging.yourdomain.com
SENTRY_ENVIRONMENT=staging
```

### Production

```bash
# Render/Railway environment variables (production)
SUPABASE_URL=https://prod-xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ... (production project - ROTATE QUARTERLY)
# ... all production resources

NODE_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
APP_URL=https://yourdomain.com
SENTRY_ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## How to Set Environment Variables

### Local Development

1. Copy `.env.rex.example` to `.env`:
   ```bash
   cp .env.rex.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   nano .env  # or use your editor
   ```

3. **NEVER commit `.env` to git** (already in `.gitignore`)

---

### Render (Production)

1. Go to service → Settings → Environment
2. Click "Add Environment Variable"
3. Paste key-value pairs from this document
4. Click "Save Changes"
5. Service will auto-redeploy with new variables

**Bulk Add**: Use "Add from .env" to paste multiple at once.

---

### Vercel (Frontend)

1. Go to project → Settings → Environment Variables
2. Choose environment: Production / Preview / Development
3. Add variables with `VITE_` prefix
4. Redeploy to apply changes

---

### Railway (Alternative)

1. Go to project → Variables
2. Add variables in "Raw Editor" or one-by-one
3. Railway auto-redeploys on variable changes

---

## Security Best Practices

### Secrets Management

1. **Never commit secrets to git**
   - All secrets in `.env` (gitignored)
   - Use `.env.example` template with placeholder values

2. **Rotate secrets regularly**
   - Database passwords: Annually
   - API keys: Quarterly
   - JWT secrets: Quarterly

3. **Use strong passwords**
   - Generate with: `openssl rand -base64 32`
   - Minimum 32 characters for production

4. **Separate environments**
   - Different secrets for dev/staging/prod
   - Never reuse production secrets in development

5. **Limit secret access**
   - Backend-only secrets: `SUPABASE_SERVICE_ROLE_KEY`, `SENDGRID_API_KEY`
   - Frontend-safe: `SUPABASE_ANON_KEY`, `VITE_SUPABASE_URL`

---

## Verification Checklist

After setting environment variables, verify:

### Backend Health Check

```bash
curl https://your-api-url/health

# Should return:
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "timestamp": "..."
}
```

### Frontend API Connection

```javascript
// In browser console at your-app-url:
console.log(import.meta.env.VITE_API_BASE_URL)
// Should show: https://api.yourdomain.com

fetch(import.meta.env.VITE_API_BASE_URL + '/health')
  .then(r => r.json())
  .then(console.log)
// Should show health response
```

### Sentry Integration

```bash
# Trigger test error
curl -X POST https://your-api-url/test-error

# Check Sentry dashboard for error
```

---

## Troubleshooting

### Issue: "Environment variable not found"

**Cause**: Variable not set in platform or misspelled

**Fix**:
1. Check platform dashboard (Render/Vercel)
2. Verify variable name matches exactly (case-sensitive)
3. Redeploy service after adding variable

---

### Issue: Frontend can't access env vars

**Cause**: Missing `VITE_` prefix

**Fix**:
```bash
# Wrong:
API_BASE_URL=https://api.com

# Correct:
VITE_API_BASE_URL=https://api.com
```

---

### Issue: CORS errors from frontend

**Cause**: `ALLOWED_ORIGINS` doesn't include frontend domain

**Fix**:
```bash
# In backend env vars:
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Include all domains (with and without www)
```

---

## Quick Reference

**Required for Stage A deployment:**

```
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY (backend)
SUPABASE_ANON_KEY (frontend)
SUPABASE_JWT_SECRET
REDIS_HOST
REDIS_PORT
REDIS_PASSWORD
OPENAI_API_KEY
SENDGRID_API_KEY
ALLOWED_ORIGINS
APP_URL
SENTRY_DSN (recommended)
```

**Optional but recommended:**

```
TWILIO_ACCOUNT_SID (if using SMS)
TWILIO_AUTH_TOKEN (if using SMS)
TWILIO_PHONE_NUMBER (if using SMS)
CALENDLY_API_KEY (if using calendar)
SENTRY_ENVIRONMENT
LOG_LEVEL
```

---

## Support

For questions about environment variables:
- Check this document
- Review `.env.rex.example` for format
- See `STAGE_A_DEPLOYMENT.md` for deployment steps
