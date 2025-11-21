# [DRAFT] Phase 0: REX Special Forces Scaffold

## 🎯 Overview

This PR establishes the foundational scaffold for the production-grade REX Special Forces system - a fully autonomous AI agent orchestration platform built on CrewAI.

**Status:** Draft - Awaiting approval to proceed to Phase 1
**Branch:** `feat/rex-special-forces`
**Phase:** 0 of 9

## 📦 What's in This PR

### Backend Infrastructure

**Agent Framework (`backend/agents/crew/`):**
- ✅ `BaseAgent` class - Production-grade base class for all CrewAI agents
  - Mission lifecycle management
  - Automatic telemetry to `agent_logs` table
  - Error handling with exponential backoff
  - Idempotency via Redis caching (1-hour TTL)
  - PII redaction for GDPR-compliant LLM calls
  - Statistics tracking (success rate, duration, LLM usage)
- ✅ Agent registry system for dynamic loading
- ✅ Test suite structure

**REX Core Modules (`backend/rex/`):**
- ✅ Existing orchestration modules preserved:
  - `decision_engine.py` - 3-layer decision architecture
  - `scheduler.py` - Priority queue-based mission scheduler
  - `resource_allocator.py` - Agent/domain/API quota management
  - `analytics_engine.py` - Real-time metrics & anomaly detection
  - `message_bus.py` - Redis pub/sub messaging
  - `api_routes.py` - 9 RESTful endpoints
  - `websocket_server.py` - Real-time updates
- ✅ New module directories:
  - `integrations/` - External service adapters (SendGrid, Twilio, Calendar)
  - `domain/` - Domain pool management & warmup engine

**Worker Services (`backend/services/worker/`):**
- ✅ Structure for Redis-backed async mission workers

### Frontend

**Rex UI Components (`src/components/rex/`):**
- ✅ `CommandCenter.tsx` - Already implemented (from previous session)
- ✅ `types/rex.ts` - TypeScript definitions (500+ lines)
- ⏳ Placeholders for Phase 5 components:
  - `MissionFeed.tsx`
  - `AgentStatusDashboard.tsx`
  - `DomainPoolModal.tsx`

### Infrastructure

**Deployment Guide (`deploy/README.md`):**
- ✅ Comprehensive 300+ line deployment guide
- ✅ Docker Compose configuration
- ✅ Kubernetes manifest templates
- ✅ Environment variable documentation
- ✅ Scaling guidelines (API, workers, database)
- ✅ Monitoring & observability checklist
- ✅ SOC2/GDPR compliance checklist
- ✅ Backup & recovery procedures
- ✅ Troubleshooting guide

## 🏗️ Architecture Decisions

### 1. Deterministic-First Design

All agents prioritize deterministic logic over LLM calls:
- **80%** of operations: Pure business logic
- **15%** of operations: Rule-based decisions
- **5%** of operations: LLM reasoning (edge cases only)

### 2. GDPR & SOC2 Compliance

**PII Redaction:**
```python
# Before LLM call
redacted_data = agent.redact_pii(user_data, consent=user.llm_consent)
llm_response = await openai.call(redacted_data)
```

**Audit Trail:**
- Every agent action writes to `agent_logs` table
- Mission lifecycle tracked in `rex_missions` table
- Full audit trail for compliance

### 3. Idempotency

Redis-based idempotency with SHA-256 keys:
```python
idempotency_key = agent.generate_idempotency_key(mission_id, params)
cached_result = await agent._check_idempotency(idempotency_key)
if cached_result:
    return cached_result  # Skip re-execution
```

### 4. Error Handling

Exponential backoff with max 3 retries:
```python
backoff_seconds = 2 ** context.retry_count  # 2s, 4s, 8s
if context.retry_count >= context.max_retries:
    return AgentResult(success=False, error={'recoverable': False})
```

## 📊 Files Changed

### New Files (14):
- `backend/agents/crew/__init__.py`
- `backend/agents/crew/base_agent.py` (300+ lines)
- `backend/agents/tests/__init__.py`
- `backend/rex/integrations/__init__.py`
- `backend/rex/domain/__init__.py`
- `backend/services/worker/__init__.py`
- `deploy/README.md` (300+ lines)
- `REX_SPECIAL_FORCES_SCAFFOLD.md`
- Plus REX core modules from previous session (preserved)

### Modified Files:
- Various documentation updates
- Existing REX modules preserved

## 🧪 Testing Strategy

### Phase 0 (This PR):
- ✅ Structural validation (files created)
- ✅ Import checks (no syntax errors)
- ⏳ Unit tests for BaseAgent (Phase 3)

### Future Phases:
- **Phase 1:** Schema validation tests
- **Phase 2:** Decision engine unit tests
- **Phase 3:** Agent integration tests (one per agent)
- **Phase 4:** Domain pool state machine tests
- **Phase 5:** UI component tests
- **Phase 7:** E2E integration tests
- **Phase 8:** Security & compliance tests

## ⚠️ Known Limitations & Mitigation

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| Redis unavailability | Idempotency fails | Add DB-based fallback (Phase 1) |
| PII redaction false negatives | May leak PII to LLM | Add configurable PII field list (Phase 8) |
| Agent registry name conflicts | Agent loading fails | Add validation in `register_agent()` (Phase 3) |
| Connection pool exhaustion | Database errors | Add connection limits in production config (deployment guide) |

## 📋 Next Steps (Phase 1)

**AWAITING APPROVAL TO PROCEED**

Once this PR is reviewed and approved, Phase 1 will implement:

### Task A: Database Schemas
- [ ] `agent_logs` table with RLS policies
- [ ] Enhanced `domain_pool` with warmup state machine
- [ ] `inbox_management` table for email accounts
- [ ] Billing hooks for email account purchases
- **Deliverable:** 3 migration files

### Task B: FastAPI Contracts
- [ ] `/rex/command` - Mission creation endpoint
- [ ] `/agents/mission` - Agent webhook handler
- [ ] `/agents/status` - Health checks
- [ ] `/domain/assign` - Domain allocation API
- [ ] `/webhook/llm` - LLM callback handler
- **Deliverable:** Pydantic models + OpenAPI docs + unit tests

**Estimated Time:** 2-3 hours
**Blockers:** None (all dependencies in place)

## 🔍 Self-Review

### Assumptions:
1. ✅ Supabase Postgres as primary database
2. ✅ Redis for caching, queue, and idempotency
3. ✅ OpenAI GPT-4 for LLM reasoning
4. ✅ FastAPI for REST API layer
5. ✅ React + TypeScript + Tailwind for frontend

### Potential Issues:
1. ⚠️ **Line ending warnings (CRLF/LF):** Windows development environment - Git config set to auto-convert
2. ⚠️ **Large commit (99 files):** Includes previous REX work + new scaffold - future commits will be atomic
3. ⚠️ **No tests yet:** BaseAgent tests will be added in Phase 3 alongside first agent implementation

### Next PR Preview:
- Phase 1 will be much smaller: 3 SQL files + 5 Python files + tests
- Each agent in Phase 3 will be a separate commit/PR
- UI components in Phase 5 will be iterative (one component per commit)

## ✅ Checklist

- [x] Branch created: `feat/rex-special-forces`
- [x] Scaffold structure complete
- [x] BaseAgent class with all features
- [x] Deployment guide comprehensive
- [x] Self-review completed
- [x] Commit message follows convention
- [x] Push successful
- [ ] CI/tests pass (will add tests in Phase 3)
- [ ] Founder review requested
- [ ] Approval to proceed to Phase 1

## 📝 Commit History

```
ce51c2a - chore: scaffold rex special-forces & UI shells
```

## 🔗 Related Documentation

- [REX_SPECIAL_FORCES_SCAFFOLD.md](REX_SPECIAL_FORCES_SCAFFOLD.md) - Phase tracker
- [REX_COMPLETION_SUMMARY.md](REX_COMPLETION_SUMMARY.md) - Previous REX work
- [REX_IMPLEMENTATION_STATUS.md](REX_IMPLEMENTATION_STATUS.md) - Implementation status
- [deploy/README.md](deploy/README.md) - Deployment guide

---

**Reviewers:** @founder
**Labels:** `rex`, `phase-0`, `scaffold`, `draft`
**Priority:** High
**Breaking Changes:** None
