# RekindlePro Infrastructure Roadmap - Staged Scaling Plan

**Version**: 1.0
**Last Updated**: 2025-01-23

## Overview

This document defines the infrastructure scaling plan for RekindlePro as the platform grows from 0 to 200+ client organizations. Each stage has clear triggers, requirements, and checklists.

---

## Stage A: 0–5 Clients (Pre-Pilot / Foundation)

### Trigger Conditions
- **Client org count**: 0–5 active organizations
- **OR** Revenue: <$5K MRR
- **OR** Total campaigns: <100 active

### Infrastructure Requirements

#### Compute
- **API**: Single small instance (1 vCPU, 512MB–1GB RAM)
  - Render: Starter plan or Railway: Starter
- **Workers**: Single worker instance (1 vCPU, 512MB RAM)
- **Frontend**: Static hosting (Vercel Free / Netlify Free / Render Static)

#### Database
- **Postgres**: Managed service (Supabase Free or Render Postgres Starter)
  - Storage: <1GB
  - Connections: <10 concurrent
- **Backups**: Platform-managed daily backups

#### Caching / Queues
- **Redis**: Managed starter plan (Render Redis Starter / Upstash Free)
  - Memory: 25–50MB
  - Persistence: AOF enabled

#### Networking
- **HTTPS**: Enforced via platform (Render/Railway/Vercel auto-provision)
- **CDN**: Optional (Vercel/Netlify includes by default)

### Monitoring & Observability

#### Required
- [ ] Health check endpoint (`/health`) deployed and documented
- [ ] Sentry (or equivalent) enabled for backend
- [ ] Sentry (or equivalent) enabled for frontend
- [ ] Platform health checks configured (Render/Railway uptime monitoring)

#### Logging
- [ ] Structured JSON logs to stdout/stderr
- [ ] Log retention: 7 days minimum (platform default)

#### Alerts
- [ ] Platform uptime alerts (email to ops@)
- [ ] Sentry error notifications (critical errors only)

### Security & Compliance

#### Required
- [ ] HTTPS enforced on all endpoints
- [ ] Secrets stored in platform environment variables (no hardcoded values)
- [ ] `.env` files gitignored
- [ ] RLS (Row-Level Security) enabled on all Supabase tables
- [ ] CORS configured (specific origins, no wildcards in production)

#### Compliance
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR-compliant data retention policy documented

### Documentation

#### Required Docs
- [ ] `docs/deployment/STAGE_A_DEPLOYMENT.md` - Step-by-step deployment guide
- [ ] `docs/deployment/ENV_VARS.md` - All environment variables documented
- [ ] `README.md` - Quick start for local development

### Stage A Checklist

**Infrastructure:**
- [x] Managed Postgres (Supabase) configured
- [ ] Redis instance provisioned and connected
- [ ] Frontend deployed to static hosting
- [ ] Backend deployed to Render/Railway
- [ ] Worker deployed and processing queue

**Observability:**
- [ ] Health endpoint accessible at `/health`
- [ ] Sentry DSN configured for backend
- [ ] Sentry DSN configured for frontend
- [ ] Platform uptime monitoring enabled

**Security:**
- [x] All secrets in environment variables
- [x] No hardcoded passwords in config files
- [ ] HTTPS enforced
- [ ] CORS restricted to production domain

**Documentation:**
- [ ] Deployment guide written
- [ ] Environment variables documented
- [ ] Runbook for common operations

---

## Stage B: 5–20 Clients (Early Pilot)

### Trigger Conditions
- **Client org count**: 5–20 active organizations
- **OR** Revenue: $5K–$20K MRR
- **OR** API requests: >10K per day
- **OR** Queue depth: Consistently >100 pending jobs

### Infrastructure Requirements

#### Compute
- **API**: 2+ instances with autoscaling (1 vCPU, 1GB RAM each)
  - Render: Standard plan with autoscaling
  - OR Railway: Pro plan with horizontal scaling
- **Workers**: 2+ worker instances (dedicated by task type)
  - Worker 1: Campaign/outreach tasks
  - Worker 2: Analytics/reporting tasks
- **Frontend**: Static hosting (upgraded plan if needed for bandwidth)

#### Database
- **Postgres**: Upgraded managed service
  - Supabase Pro or Render Postgres Standard
  - Storage: 1–10GB
  - Connections: 20–50 concurrent
  - Connection pooling enabled
- **Backups**: Automated hourly backups, 7-day retention

#### Caching / Queues
- **Redis**: Upgraded plan (Render Redis Standard / Upstash Pro)
  - Memory: 256MB–1GB
  - Persistence: AOF + RDB snapshots
  - Separate queues per task type

#### Networking
- **Load Balancer**: Platform-managed (Render/Railway handles this)
- **CDN**: Enabled (Cloudflare Free or platform default)
- **Rate Limiting**: 100 req/min per user (enforced at API level)

### Monitoring & Observability

#### Required
- [ ] Application metrics exported (Prometheus format or platform metrics)
- [ ] Error rate alert: >2% for 10 minutes
- [ ] Queue depth alert: >500 for 15 minutes
- [ ] Database slow query monitoring enabled
- [ ] LLM API failure rate tracked

#### Dashboards
- [ ] Platform metrics dashboard (Render/Railway built-in)
- [ ] Sentry performance monitoring enabled (10% sample rate)

#### Logging
- [ ] Structured JSON logs
- [ ] Log retention: 14 days
- [ ] Log search capability (via platform or external service)

### Security & Compliance

#### Required
- [ ] WAF (Web Application Firewall) enabled (Cloudflare or platform WAF)
- [ ] Rate limiting enforced at edge
- [ ] API key rotation documented and tested
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)

#### Compliance
- [ ] Data Processing Agreement (DPA) template ready
- [ ] GDPR data export API implemented
- [ ] Data deletion workflow tested

### Documentation

#### Required Docs
- [ ] `docs/deployment/STAGE_B_DEPLOYMENT.md`
- [ ] `docs/runbooks/SCALING_WORKERS.md`
- [ ] `docs/runbooks/DATABASE_UPGRADE.md`
- [ ] `docs/monitoring/ALERT_PLAYBOOK.md`

### Stage B Checklist

**Infrastructure:**
- [ ] API autoscaling configured (min 2, max 5 instances)
- [ ] Worker pools separated by task type
- [ ] Redis upgraded to Standard plan
- [ ] Database upgraded to Pro tier
- [ ] Connection pooling enabled

**Observability:**
- [ ] Metrics dashboard created
- [ ] Error rate alerts configured
- [ ] Queue depth alerts configured
- [ ] Slow query monitoring enabled
- [ ] LLM failure tracking implemented

**Security:**
- [ ] WAF enabled
- [ ] Rate limiting at 100 req/min per user
- [ ] API key rotation process documented
- [ ] Security headers configured

**Documentation:**
- [ ] Stage B deployment guide
- [ ] Worker scaling runbook
- [ ] Alert response playbook

---

## Stage C: 20–50 Clients (Full Pilot)

### Trigger Conditions
- **Client org count**: 20–50 active organizations
- **OR** Revenue: $20K–$50K MRR
- **OR** API requests: >50K per day
- **OR** Database size: >10GB

### Infrastructure Requirements

#### Compute
- **API**: 3–10 instances with autoscaling (2 vCPU, 2GB RAM each)
- **Workers**: Dedicated worker pools
  - Heavy missions worker pool (2–5 instances)
  - Deliverability worker pool (1–2 instances)
  - Analytics worker pool (1–2 instances)
  - Notifications worker (1 instance)
- **Frontend**: CDN-backed static hosting (upgraded bandwidth)

#### Database
- **Postgres**: Production-grade managed service
  - Supabase Team or RDS db.t3.medium
  - Storage: 10–50GB with auto-scaling
  - Connections: 100 concurrent
  - Read replica for analytics queries (optional but recommended)
- **Backups**: Automated hourly backups, 30-day retention, point-in-time recovery

#### Caching / Queues
- **Redis**: Production plan (Render Redis Pro / Upstash Professional)
  - Memory: 1–4GB
  - High availability: Multi-AZ or replication
  - Separate Redis instances per concern (cache, queue, sessions)

#### Networking
- **Load Balancer**: Dedicated load balancer with SSL termination
- **CDN**: Global CDN (Cloudflare Pro or AWS CloudFront)
- **DDoS Protection**: Enabled (Cloudflare or similar)

### Monitoring & Observability

#### Required
- [ ] Full metrics stack (Prometheus + Grafana or Datadog)
- [ ] APM (Application Performance Monitoring) - New Relic / Datadog
- [ ] Custom business metrics dashboards
- [ ] SLA tracking dashboard (uptime, p95 latency, error rate)
- [ ] Database performance monitoring (query analysis, connection pool stats)

#### Alerts
- [ ] Uptime <99.5% in 1-hour window
- [ ] Error rate >1% for 5 minutes
- [ ] p95 latency >2s for 10 minutes
- [ ] Database connections >80% capacity
- [ ] Worker queue lag >1000 jobs for 15 minutes
- [ ] LLM API costs >$500/day anomaly

#### Logging
- [ ] Centralized log aggregation (Datadog / Logtail / CloudWatch)
- [ ] Log retention: 30 days
- [ ] Log-based alerts for critical errors

### Security & Compliance

#### Required
- [ ] Penetration testing completed (annually)
- [ ] Secrets rotation automated (quarterly)
- [ ] Audit logs for all admin actions
- [ ] IP whitelisting for admin endpoints
- [ ] Multi-factor authentication (MFA) enforced for admin users

#### Compliance
- [ ] SOC 2 Type I preparation started
- [ ] GDPR compliance verified by legal
- [ ] Data residency options documented (if EU clients)
- [ ] Security questionnaire responses prepared

### Documentation

#### Required Docs
- [ ] `docs/sla/SERVICE_LEVEL_AGREEMENT.md` - Internal SLA targets
- [ ] `docs/runbooks/INCIDENT_RESPONSE.md` - On-call playbook
- [ ] `docs/architecture/SYSTEM_ARCHITECTURE.md` - Updated architecture diagram
- [ ] `docs/compliance/GDPR_COMPLIANCE.md`

### Stage C Checklist

**Infrastructure:**
- [ ] API autoscaling 3–10 instances
- [ ] Worker pools separated and scaled
- [ ] Database read replica for analytics
- [ ] Redis multi-AZ or replicated
- [ ] Global CDN configured

**Observability:**
- [ ] Metrics stack deployed
- [ ] APM integrated
- [ ] SLA dashboard created
- [ ] Business metrics tracked
- [ ] Incident alerting configured

**Security:**
- [ ] Penetration test completed
- [ ] Secret rotation automated
- [ ] Audit logs implemented
- [ ] MFA enforced for admins

**Documentation:**
- [ ] Internal SLA documented
- [ ] Incident response playbook
- [ ] Updated architecture diagrams

---

## Stage D: 50–200 Clients (Post-Pilot / Open Sales)

### Trigger Conditions
- **Client org count**: 50–200 active organizations
- **OR** Revenue: $50K–$200K MRR
- **OR** API requests: >200K per day

### Infrastructure Requirements

#### Compute
- **Microservices Split**:
  - API service (5–20 instances, 2 vCPU, 4GB RAM)
  - Orchestration service (3–10 instances)
  - Analytics service (2–5 instances)
  - Notifications service (2–5 instances)
- **Autoscaling**: CPU-based (target 70%) and request-based

#### Database
- **Postgres**: Multi-region or sharded
  - Primary: db.r5.large (2 vCPU, 16GB RAM)
  - Read replicas: 2+ for analytics and reporting
  - Separate analytics database (data warehouse or read replica)

#### Caching / Queues
- **Redis**: Clustered Redis (3+ nodes, 8–16GB total)
- **Message Queue**: Consider migrating to RabbitMQ or AWS SQS for reliability

### Monitoring & Observability

#### Required
- [ ] Distributed tracing (Jaeger / Datadog APM)
- [ ] Service mesh observability (if using Kubernetes)
- [ ] Cost monitoring dashboard (cloud spend per client)
- [ ] Customer-facing status page (status.rekindlepro.ai)

#### SLOs
- [ ] 99.9% uptime target
- [ ] p95 latency <500ms
- [ ] Error rate <0.5%

### Security & Compliance

#### Required
- [ ] SOC 2 Type II certification achieved
- [ ] GDPR DPA template finalized
- [ ] ISO 27001 preparation (optional)
- [ ] Formal security training for eng team

### Stage D Checklist

**Infrastructure:**
- [ ] Microservices architecture deployed
- [ ] Database read replicas (2+)
- [ ] Redis cluster (3+ nodes)
- [ ] Global CDN with multi-region

**Observability:**
- [ ] Distributed tracing
- [ ] Cost monitoring
- [ ] Customer status page
- [ ] SLO tracking

**Security:**
- [ ] SOC 2 Type II certified
- [ ] GDPR DPA finalized

---

## Stage E: 200+ Clients (Serious SaaS)

### Trigger Conditions
- **Client org count**: 200+ active organizations
- **OR** Revenue: $200K+ MRR

### Infrastructure Requirements

#### Compute
- **Kubernetes or equivalent**: Full orchestration (EKS, GKE, AKS)
- **Horizontal pod autoscaling**: All services
- **Multi-region deployment**: Primary + failover region

#### Database
- **Postgres**: Sharded or federated
  - Read replicas in each region
  - Separate analytics data warehouse (Snowflake, BigQuery)

#### ML / AI
- **LLM Strategy**: Mix of OpenAI + self-hosted models (cost optimization)
- **Model serving**: Dedicated inference service

### Monitoring & Observability

#### Required
- [ ] Full observability stack (logs, metrics, traces)
- [ ] Chaos engineering (automated failure testing)
- [ ] Formal incident response rotations

#### SLOs
- [ ] 99.95% uptime
- [ ] p99 latency <1s
- [ ] Error rate <0.1%

### Security & Compliance

#### Required
- [ ] ISO 27001 certified
- [ ] HIPAA compliance (if needed)
- [ ] Formal penetration testing (quarterly)

### Stage E Checklist

**Infrastructure:**
- [ ] Kubernetes deployed
- [ ] Multi-region active-active
- [ ] Analytics data warehouse
- [ ] Self-hosted LLM option

**Observability:**
- [ ] Chaos engineering
- [ ] Incident rotations
- [ ] 99.95% uptime SLO

**Security:**
- [ ] ISO 27001 certified
- [ ] Quarterly pen tests

---

## Appendix: Quick Reference

| Stage | Clients | API Instances | Workers | DB Tier | Redis | Monitoring |
|-------|---------|---------------|---------|---------|-------|------------|
| A | 0–5 | 1 | 1 | Free/Starter | Starter | Basic (Sentry) |
| B | 5–20 | 2+ | 2+ | Pro | Standard | Metrics + Alerts |
| C | 20–50 | 3–10 | 5+ pools | Production | Pro/HA | Full APM |
| D | 50–200 | 10–20 | Autoscaled | Multi-replica | Cluster | Distributed tracing |
| E | 200+ | K8s cluster | K8s pods | Sharded/DW | Cluster | Full stack + chaos |
