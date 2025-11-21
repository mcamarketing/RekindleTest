# REX Orchestration API

Production-grade FastAPI server for Rex autonomous orchestration system.

## Overview

The Rex API provides HTTP/REST endpoints for:

- **Mission Management**: Create, query, and cancel missions
- **Agent Webhooks**: Agents report progress and events
- **Domain Pool**: Allocate warm domains, manage warmup, trigger rotation
- **Inbox Management**: Allocate email accounts, upgrade billing tiers
- **LLM Callbacks**: Async LLM processing webhooks

## Architecture

```
rex/
├── app.py                 # FastAPI application (middleware, error handlers)
├── api_models.py          # Pydantic request/response models
├── api_endpoints.py       # Route handlers (business logic)
├── requirements.txt       # Python dependencies
├── pytest.ini             # Test configuration
├── tests/
│   ├── __init__.py
│   └── test_api_endpoints.py  # Unit tests with mocked dependencies
└── README.md              # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend/rex
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export REDIS_URL="redis://localhost:6379"
```

### 3. Run the Server

```bash
# Development mode (auto-reload)
uvicorn backend.rex.app:app --reload --port 8080

# Production mode
uvicorn backend.rex.app:app --host 0.0.0.0 --port 8080 --workers 4
```

### 4. Access API Docs

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## API Endpoints

### Mission Management

**Create Mission**
```http
POST /rex/command
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "lead_reactivation",
  "priority": 75,
  "campaign_id": "campaign_123",
  "lead_ids": ["lead_1", "lead_2"]
}
```

**Get Mission Status**
```http
GET /rex/command/{mission_id}?include_logs=true&include_tasks=true
```

**Cancel Mission**
```http
POST /rex/command/{mission_id}/cancel
Content-Type: application/json

{
  "mission_id": "mission_abc123",
  "reason": "User requested cancellation"
}
```

**Bulk Create Missions**
```http
POST /rex/command/bulk
Content-Type: application/json

{
  "missions": [
    {
      "user_id": "...",
      "type": "lead_reactivation",
      "priority": 50
    },
    ...
  ]
}
```

### Agent Webhooks

**Report Mission Update**
```http
POST /agents/mission
Content-Type: application/json

{
  "mission_id": "mission_abc123",
  "agent_name": "ReviverAgent",
  "event_type": "mission_progress",
  "progress": 0.45,
  "data": {
    "leads_processed": 45,
    "leads_qualified": 12
  }
}
```

**Get Agent Status**
```http
GET /agents/status?agent_name=ReviverAgent
```

### Domain Management

**Allocate Domain**
```http
POST /domain/assign
Content-Type: application/json

{
  "user_id": "...",
  "campaign_id": "campaign_123",
  "min_reputation_score": 0.7
}
```

**Start Domain Warmup**
```http
POST /domain/warmup
Content-Type: application/json

{
  "domain": "mail.example.com",
  "user_id": "..."
}
```

**Check Domain Health**
```http
GET /domain/health/mail.example.com
```

**Trigger Domain Rotation**
```http
POST /domain/rotate
Content-Type: application/json

{
  "domain": "mail.example.com",
  "reason": "high_bounce_rate",
  "immediate": true
}
```

### Inbox Management

**Allocate Inbox**
```http
POST /inbox/allocate
Content-Type: application/json

{
  "user_id": "...",
  "campaign_id": "campaign_123",
  "preferred_provider": "sendgrid"
}
```

**Upgrade Inbox Tier**
```http
POST /inbox/upgrade
Content-Type: application/json

{
  "inbox_id": "inbox_123",
  "new_tier": "pro",
  "stripe_subscription_id": "sub_123"
}
```

### Webhooks

**LLM Callback**
```http
POST /webhook/llm
Content-Type: application/json

{
  "correlation_id": "...",
  "mission_id": "...",
  "agent_name": "ReviverAgent",
  "prompt_hash": "abc123",
  "response": {...},
  "model": "gpt-4",
  "tokens_used": 250,
  "cost_usd": 0.005,
  "duration_ms": 1200
}
```

## Testing

### Run Unit Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=backend.rex --cov-report=html

# Specific test file
pytest tests/test_api_endpoints.py

# Specific test
pytest tests/test_api_endpoints.py::test_create_mission_success

# Verbose mode
pytest -v
```

### Test Coverage

Target: **80%+ code coverage**

Current coverage includes:
- All endpoint routes
- Pydantic validation
- Database operations (mocked)
- Redis pub/sub (mocked)
- Error handling

## Dependencies

Core:
- **FastAPI** (0.109.0) - Web framework
- **Uvicorn** (0.27.0) - ASGI server
- **Pydantic** (2.5.3) - Data validation

Database:
- **Supabase** (2.3.0) - Postgres client
- **Redis** (5.0.1) - Caching & pub/sub

Testing:
- **Pytest** (7.4.4) - Test framework
- **pytest-asyncio** (0.23.3) - Async test support
- **pytest-cov** (4.1.0) - Coverage reporting

## Database Schema

The API relies on these database tables (created by migrations):

- **rex_missions**: Mission lifecycle tracking
- **rex_domain_pool**: Domain pool with warmup state machine
- **inbox_management**: Email account management with billing
- **agent_logs**: Comprehensive audit trail

See `supabase/migrations/20251122*.sql` for schema definitions.

## Production Deployment

### Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional
REDIS_URL=redis://localhost:6379  # Defaults to localhost
PORT=8080  # Defaults to 8080
LOG_LEVEL=info  # info, debug, warning, error
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/rex/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/rex/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:
```bash
docker build -t rex-api .
docker run -p 8080:8080 --env-file .env rex-api
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rex-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rex-api
  template:
    metadata:
      labels:
        app: rex-api
    spec:
      containers:
      - name: rex-api
        image: rex-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: rex-secrets
              key: supabase-url
        - name: SUPABASE_SERVICE_ROLE_KEY
          valueFrom:
            secretKeyRef:
              name: rex-secrets
              key: supabase-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ping
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Error Handling

All endpoints return consistent error responses:

**422 Unprocessable Entity** (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**404 Not Found**
```json
{
  "detail": "Mission not found: mission_abc123"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error",
  "message": "Failed to create mission: connection timeout"
}
```

## Monitoring

### Health Checks

- **GET /health**: Load balancer health check
- **GET /ping**: Simple connectivity test
- **GET /**: Service info and version

### Logging

All requests logged with:
- HTTP method and path
- Status code
- Duration in milliseconds

```
2025-11-22 14:30:00 - rex_api - INFO - POST /rex/command - 201 - 145ms
```

### Metrics

Response headers include:
- **X-Process-Time**: Request processing time in ms

### Redis Pub/Sub

Mission updates published to Redis channels:
- Channel: `mission:{mission_id}`
- Payload: JSON with event_type, agent_name, progress, data

Frontend can subscribe for real-time updates.

## Security

### Authentication

Currently uses Supabase service role key for all operations.

TODO: Add JWT authentication with user context.

### Rate Limiting

TODO: Add rate limiting middleware using Redis.

### CORS

Configured to allow all origins (development mode).

**Production**: Restrict to specific origins:
```python
allow_origins=["https://yourdomain.com"]
```

## Roadmap

- [ ] JWT authentication with user context
- [ ] Rate limiting middleware
- [ ] WebSocket support for real-time updates
- [ ] Prometheus metrics endpoint
- [ ] Distributed tracing with OpenTelemetry
- [ ] API versioning (v1, v2)
- [ ] GraphQL endpoint option
- [ ] Async task queue integration

## Contributing

1. Create feature branch from `feat/rex-special-forces`
2. Write tests for new endpoints
3. Ensure 80%+ coverage: `pytest --cov`
4. Update this README with new endpoints
5. Commit with clear message
6. Open PR with description

## License

Proprietary - Rekindle AI
