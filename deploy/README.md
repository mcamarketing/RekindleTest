# REX Special Forces - Deployment Guide

## Overview

This guide covers deployment of the REX autonomous orchestration system with production-grade CrewAI agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              Vercel / CloudFlare Pages                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway / Load Balancer                 │
│                    (nginx / Traefik)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
┌────────────────┐ ┌────────────┐ ┌────────────────┐
│   FastAPI      │ │  Mission   │ │   WebSocket    │
│   API Server   │ │  Workers   │ │    Server      │
│   (Gunicorn)   │ │  (RQ/Redis)│ │  (Uvicorn)     │
└────────┬───────┘ └─────┬──────┘ └────────┬───────┘
         │               │                  │
         └───────────────┼──────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Redis (Queue + Cache)                     │
│                    PostgreSQL (Supabase)                     │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for production)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (Supabase)
- Redis 7+

## Environment Variables

Create `.env` file in project root:

```bash
# Database
SUPABASE_URL=<redacted>
SUPABASE_SERVICE_ROLE_KEY=<redacted>
DATABASE_URL=<redacted>

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<redacted>
REDIS_DB=0

# OpenAI
OPENAI_API_KEY=<redacted>
OPENAI_ORG_ID=<redacted>

# SendGrid
SENDGRID_API_KEY=<redacted>
SENDGRID_FROM_EMAIL=noreply@rekindlepro.ai

# Twilio
TWILIO_ACCOUNT_SID=<redacted>
TWILIO_AUTH_TOKEN=<redacted>
TWILIO_PHONE_NUMBER=<redacted>

# Application
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=<redacted>
ALLOWED_ORIGINS=https://app.rekindlepro.ai,https://rekindlepro.ai

# Monitoring
SENTRY_DSN=<redacted>
DATADOG_API_KEY=<redacted>

# Feature Flags
ENABLE_LLM_FALLBACK=true
ENABLE_DOMAIN_WARMUP=true
ENABLE_ANALYTICS=true
```

## Local Development

### 1. Start Infrastructure

```bash
docker-compose up -d postgres redis
```

### 2. Run Database Migrations

```bash
cd backend
supabase db push
# Or manually:
psql $DATABASE_URL < ../supabase/migrations/20251121000000_create_rex_tables.sql
psql $DATABASE_URL < ../supabase/migrations/20251122000000_add_domain_pool_enhanced.sql
psql $DATABASE_URL < ../supabase/migrations/20251122000001_add_inbox_management.sql
psql $DATABASE_URL < ../supabase/migrations/20251122000002_add_agent_logs.sql
```

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 4. Start Services

**Terminal 1: API Server**
```bash
cd backend
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Mission Workers**
```bash
cd backend
python -m services.worker.mission_worker
```

**Terminal 3: Frontend Dev Server**
```bash
cd frontend
npm run dev
```

### 5. Access Application

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Rex Command Center: http://localhost:5173/rex

## Docker Deployment

### Build Images

```bash
# API Server
docker build -f deploy/Dockerfile.api -t rekindle/api:latest .

# Mission Worker
docker build -f deploy/Dockerfile.worker -t rekindle/worker:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

Services will be available at:
- API: http://localhost:8000
- Frontend: http://localhost:3000

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace rekindle-prod
```

### 2. Create Secrets

```bash
kubectl create secret generic rekindle-secrets \
  --from-env-file=.env \
  --namespace=rekindle-prod
```

### 3. Deploy Services

```bash
kubectl apply -f deploy/k8s/api-deployment.yaml
kubectl apply -f deploy/k8s/worker-deployment.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
kubectl get pods -n rekindle-prod
kubectl logs -f deployment/rekindle-api -n rekindle-prod
```

## Production Checklist

### Security

- [ ] SSL/TLS certificates configured
- [ ] API rate limiting enabled
- [ ] CORS origins properly configured
- [ ] Database RLS policies enabled
- [ ] Secrets stored in Kubernetes secrets / Vault
- [ ] PII redaction enabled for LLM calls
- [ ] GDPR consent checks implemented

### Performance

- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] CDN configured for static assets
- [ ] Image optimization enabled
- [ ] Connection pooling configured
- [ ] Horizontal pod autoscaling configured

### Monitoring

- [ ] Sentry error tracking enabled
- [ ] Datadog APM configured
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards created
- [ ] Alerts configured for critical errors
- [ ] Log aggregation (ELK/Loki) configured

### Compliance

- [ ] SOC2 audit logs enabled
- [ ] GDPR data export functionality
- [ ] User consent management
- [ ] Data retention policies configured
- [ ] Backup and disaster recovery tested

## Scaling Guidelines

### API Server

- **Low Load (< 100 req/s):** 2 replicas, 0.5 CPU, 1GB RAM each
- **Medium Load (100-500 req/s):** 4 replicas, 1 CPU, 2GB RAM each
- **High Load (> 500 req/s):** 8+ replicas, 2 CPU, 4GB RAM each

### Mission Workers

- **Low Volume (< 100 missions/day):** 2 workers
- **Medium Volume (100-1000 missions/day):** 4-8 workers
- **High Volume (> 1000 missions/day):** 16+ workers

### Database

- **Connections:** Set max_connections = (2 * API replicas * 10) + (workers * 5)
- **RAM:** Minimum 4GB, recommend 16GB+ for production
- **CPU:** Minimum 2 cores, recommend 8+ for production

## Troubleshooting

### API Server Won't Start

```bash
# Check logs
kubectl logs -f deployment/rekindle-api -n rekindle-prod

# Common issues:
# 1. Database connection failed - check DATABASE_URL
# 2. Redis connection failed - check REDIS_HOST/PORT
# 3. Port already in use - check for conflicting services
```

### Missions Not Executing

```bash
# Check worker status
kubectl get pods -l app=rekindle-worker -n rekindle-prod

# Check Redis queue
redis-cli -h redis.rekindle-prod.svc.cluster.local
> LLEN mission_queue

# Check mission logs
psql $DATABASE_URL -c "SELECT * FROM rex_logs WHERE mission_id = 'xxx' ORDER BY created_at DESC;"
```

### High Memory Usage

```bash
# Check memory by pod
kubectl top pods -n rekindle-prod

# Common causes:
# 1. Too many concurrent missions - reduce worker count
# 2. Memory leak in agent - check agent logs
# 3. Large LLM responses - implement response size limits
```

## Backup and Recovery

### Database Backup

```bash
# Manual backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Automated backups (add to cron)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/rekindle-$(date +%Y%m%d).sql.gz
```

### Redis Backup

```bash
# Save RDB snapshot
redis-cli SAVE

# Automated snapshots (redis.conf)
save 900 1
save 300 10
save 60 10000
```

### Restore from Backup

```bash
# Database
psql $DATABASE_URL < backup-20251122.sql

# Redis
redis-cli FLUSHALL
redis-cli --pipe < dump.rdb
```

## Support

For deployment issues:
- Email: engineering@rekindlepro.ai
- Slack: #rex-deployments
- Docs: https://docs.rekindlepro.ai/rex
