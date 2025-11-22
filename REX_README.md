# REX Autonomous Orchestration System

**Production-Ready AI Agent Orchestration for Lead Reactivation**

## Overview

Rex is an autonomous orchestration system managing 8 specialized AI agents across multi-step workflows to maximize lead reactivation performance with minimal human intervention.

### Key Features

- **8 Specialized Agents**: ReviverAgent, DeliverabilityAgent, PersonalizerAgent, ICPIntelligenceAgent, ScraperAgent, OutreachAgent, AnalyticsAgent, SpecialForcesCoordinator
- **Three-Layer Decision Architecture**: 80% state machine, 15% business rules, 5% LLM reasoning
- **Production-Grade Infrastructure**: Docker, CI/CD, monitoring, security hardening
- **Multi-Channel Outreach**: Email, SMS, LinkedIn with intelligent delivery
- **Real-Time Analytics**: Performance tracking, A/B testing, optimization recommendations

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Rex Command Center                       │
│                  (React UI + Real-time Updates)              │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Rex Decision Engine                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ State Machine│→ │ Rule Engine  │→ │ LLM Reasoner │      │
│  │   (80%)      │  │    (15%)     │  │    (5%)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    8 Specialized Agents                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Reviver  │ │Deliver-  │ │Personal- │ │   ICP    │       │
│  │  Agent   │ │ability   │ │izer      │ │Intelli-  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Scraper  │ │ Outreach │ │Analytics │ │  Special │       │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Forces  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data & Integration Layer                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Supabase │ │  Redis   │ │ SendGrid │ │  Twilio  │       │
│  │Postgres  │ │  Cache   │ │   Email  │ │   SMS    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Agent Specializations

1. **ReviverAgent**: Dead lead reactivation with probability scoring
2. **DeliverabilityAgent**: Domain health monitoring and automatic rotation
3. **PersonalizerAgent**: AI-powered message generation with 4 copywriting frameworks
4. **ICPIntelligenceAgent**: ICP extraction and weighted lead scoring
5. **ScraperAgent**: Multi-source data enrichment with caching
6. **OutreachAgent**: Multi-channel delivery with rate limiting
7. **AnalyticsAgent**: Performance analytics and A/B testing
8. **SpecialForcesCoordinator**: Multi-agent workflow orchestration

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Supabase account (or local setup)
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/rekindlepro.git
cd rekindlepro

# Install dependencies
npm install
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run with Docker Compose
docker-compose -f docker-compose.rex.yml up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Setup

```bash
# Frontend (React + Vite)
npm run dev

# Backend (FastAPI + Uvicorn)
cd backend
uvicorn rex.app:app --reload --port 8000

# Run tests
npm test
pytest backend/rex/tests/
```

## API Documentation

### Create Mission

```bash
POST /rex/command
{
  "user_id": "uuid",
  "type": "lead_reactivation",
  "priority": 75,
  "lead_ids": ["lead-1", "lead-2"]
}
```

### Get Mission Status

```bash
GET /rex/command/{mission_id}?include_logs=true
```

### Webhook Endpoints

```bash
# Agent mission updates
POST /agent/mission

# Domain allocation
POST /domain/assign

# Inbox sync
POST /inbox/sync

# SendGrid webhook
POST /webhook/sendgrid

# Twilio webhook
POST /webhook/twilio
```

## Deployment

### Docker Production

```bash
# Build images
docker build -f Dockerfile.backend -t rex-backend:latest .
docker build -f Dockerfile -t rex-frontend:latest .

# Run production stack
docker-compose -f docker-compose.rex.yml --profile production up -d
```

### Railway/Render

```bash
# Deploy to Railway
railway up

# Deploy to Render
render deploy
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Redis
REDIS_URL=redis://user:pass@host:6379/0

# API Keys
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Security
CORS_ORIGINS=https://yourapp.com
JWT_SECRET=your-secret-key
```

## Monitoring & Observability

### Metrics Tracked

- **Decision Engine Stats**: State machine/rule/LLM distribution
- **Agent Performance**: Success rate, avg duration, error rate
- **Campaign Metrics**: Open rate, click rate, reply rate, ROI
- **Infrastructure Health**: CPU, memory, request latency

### Logging

```python
# Structured logging with context
logger.info(
    "Mission completed",
    extra={
        "mission_id": mission_id,
        "agent": "ReviverAgent",
        "duration_ms": 1234,
        "success": True
    }
)
```

### Alerts

- **High error rate**: > 5% errors in 5 minutes
- **Slow response**: p95 latency > 2 seconds
- **Failed missions**: > 10 failures in 1 hour
- **Domain health**: Reputation score < 0.7

## Testing

### Unit Tests

```bash
# Backend
pytest backend/rex/tests/ -v --cov=rex

# Frontend
npm test -- --coverage
```

### Integration Tests

```bash
# E2E workflow tests
pytest backend/rex/tests/integration/
```

### Load Tests

```bash
# Locust load testing
locust -f backend/tests/load_tests.py --users 100 --spawn-rate 10
```

## Security

See [SECURITY.md](./SECURITY.md) for comprehensive security documentation.

### Security Highlights

- **RLS policies** on all database tables
- **PII redaction** before LLM calls
- **Rate limiting**: 100 req/min per user
- **Input validation**: Pydantic models for all API inputs
- **Encrypted secrets**: Environment variables only
- **Webhook validation**: HMAC signature verification

## Performance

### Benchmarks

- **Mission creation**: < 50ms p95
- **Decision engine**: < 100ms p95
- **Agent execution**: 1-5 seconds avg
- **Workflow completion**: 30-90 seconds avg

### Optimization

- **Redis caching**: LLM responses cached (60-80% hit rate)
- **Connection pooling**: Database connections pooled
- **Async I/O**: Full async/await throughout
- **Batch processing**: Bulk operations where possible

## Troubleshooting

### Common Issues

**Mission stuck in "queued"**
```bash
# Check agent status
GET /agent/status

# Restart backend
docker-compose restart rex_backend
```

**High LLM costs**
```bash
# Check cache hit rate
GET /rex/stats

# Increase cache TTL in decision_engine.py
```

**Domain reputation drop**
```bash
# Check domain health
GET /domain/health

# Trigger rotation
POST /domain/rotate
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- **Code style**: Black formatter, PEP 8
- **Testing**: 80%+ coverage required
- **Documentation**: Docstrings for all functions
- **Security**: Follow SECURITY.md guidelines

## Roadmap

### Q1 2025
- [x] Core 8 agents implementation
- [x] Decision engine with 3-layer architecture
- [x] UI components for domain and mission management
- [x] Docker + CI/CD setup
- [ ] Production deployment to Railway

### Q2 2025
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Voice call integration
- [ ] Mobile app (React Native)

### Q3 2025
- [ ] Enterprise features (SSO, audit logs)
- [ ] White-label support
- [ ] API rate limiting tiers
- [ ] Advanced A/B testing framework

## License

Proprietary - RekindlePro, Inc.

## Support

- **Documentation**: https://docs.rekindlepro.ai
- **Email**: support@rekindlepro.ai
- **Slack**: https://rekindlepro.slack.com
- **Status**: https://status.rekindlepro.ai

## Acknowledgments

- **CrewAI**: Agent orchestration framework
- **FastAPI**: High-performance Python web framework
- **Supabase**: Backend-as-a-service platform
- **OpenAI**: GPT-4 for LLM reasoning

---

**Built with ❤️ by the RekindlePro Engineering Team**

Last updated: 2025-01-22
