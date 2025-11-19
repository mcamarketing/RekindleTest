# 🔧 Environment Variables Setup

Copy this content to your `.env` and `.env.production` files.

## Required Variables

```bash
# Supabase Configuration (Required)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Sentry Error Monitoring (Optional - Phase 1 Quick Win)
# Get your DSN from https://sentry.io/settings/projects/
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Environment
# Options: development, production
VITE_ENV=development
```

## How to Get Supabase Keys

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy **Project URL** → `VITE_SUPABASE_URL`
5. Copy **anon public** key → `VITE_SUPABASE_ANON_KEY`

## How to Get Sentry DSN

1. Go to https://sentry.io/signup/ (create account if needed)
2. Create new project: **Platform: React**, **Name: Rekindle Production**
3. Copy the DSN from the setup page
4. Add to `.env.production` → `VITE_SENTRY_DSN`

## Vercel/Netlify Setup

Add these environment variables in your deployment platform:

**Vercel:**
- Go to Project → Settings → Environment Variables
- Add each variable above
- Redeploy

**Netlify:**
- Go to Site Settings → Build & deploy → Environment
- Add each variable above
- Redeploy

