# Stage 3: LLM Training Pipeline

**Date**: 2025-01-23
**Status**: ✅ Complete
**Branch**: `feat/rex-special-forces`
**Part of**: Flywheel Architecture - Proprietary LLM Brain Loop

---

## Overview

Stage 3 implements the **LLM training pipeline** that transforms outcome labels into a continuously-improving proprietary AI brain. This closes the learning loop: every message sent generates training data that makes the next message better.

### The Flywheel

```
Outcome Labels (Stage 2)
     ↓
Data Formatter → GPT-4 Training Examples (JSONL)
     ↓
Model Trainer → Fine-Tuned GPT-4 Model (weekly)
     ↓
Model Registry → Track Performance & A/B Test
     ↓
Agents Use New Model → Better Results
     ↓
More Outcomes → More Training Data (COMPOUNDS)
```

**Key Insight**: Every closed deal makes the AI better at closing deals. Every reply makes it better at generating replies. The more you use it, the smarter it gets. This is the defensive moat.

---

## Components Implemented

### 1. Data Formatter (`data_formatter.py`)

**Purpose**: Transform `outcome_labels` into GPT-4 fine-tuning format (JSONL).

**Key Method**: `export_training_data()`

```python
formatter = OutcomeDataFormatter(supabase)

# Export training examples
examples = await formatter.export_training_data(
    organization_id="uuid",  # None = global model
    min_quality_score=0.6,  # Quality threshold (0.0-1.0)
    include_negative_examples=True,  # Learn from failures
    limit=10000
)

# Each example:
{
    "messages": [
        {
            "role": "system",
            "content": "You are an expert B2B sales copywriter..."
        },
        {
            "role": "user",
            "content": "Write a message for: Industry=SaaS, Role=VP Sales, Framework=PAS, Tone=professional..."
        },
        {
            "role": "assistant",
            "content": "Subject: Transform your sales process\n\nHi {{first_name}}, ...\n\n**Outcome:** Deal closed: $15,000"
        }
    ],
    "metadata": {
        "outcome_id": "uuid",
        "quality_score": 0.85,
        "deal_value": 15000
    }
}
```

**Quality Score Calculation** (0.0 to 1.0):
- Delivered: +0.1
- Opened: +0.1
- Clicked: +0.15
- Replied: +0.2
- Positive reply (sentiment > 0.5): +0.2
- Meeting booked: +0.3
- Meeting completed: +0.4
- Deal closed: +0.5
- High-value deal ($50K+): +0.2
- ICP match bonus: up to +0.1

**Example Scores**:
- Deal closed ($50K, perfect ICP): 1.0 (maximum quality)
- Meeting completed: 0.8
- Positive reply: 0.6
- Opened but no reply: 0.2
- Bounced: 0.1

**Export to JSONL**:
```python
count = await formatter.export_to_jsonl(
    output_path="./training_data/training_20250123.jsonl",
    organization_id="uuid",
    min_quality_score=0.6
)
# Writes JSONL file ready for OpenAI upload
```

---

### 2. Model Trainer (`model_trainer.py`)

**Purpose**: Manage GPT-4 fine-tuning via OpenAI API.

**Full Training Cycle**:
```python
trainer = GPT4ModelTrainer(openai_api_key)

result = await trainer.full_training_cycle(
    training_file_path="./training_data/training.jsonl",
    model_suffix="rekindle-v2-1-0",
    wait_for_completion=True  # Blocks until training done
)

# Returns:
{
    "job_id": "ftjob-abc123",
    "status": "succeeded",
    "model_id": "ft:gpt-4o-2024-08-06:org:rekindle-v2-1-0:xyz789",
    "trained_tokens": 50000,
    "created_at": datetime(...),
    "finished_at": datetime(...)
}
```

**Step-by-Step Methods**:

1. **Upload Training File**:
```python
file_id = await trainer.upload_training_file("./training.jsonl")
# Returns: "file-abc123"
```

2. **Create Fine-Tuning Job**:
```python
job_id = await trainer.create_fine_tuning_job(
    training_file_id=file_id,
    suffix="rekindle-v2-1-0",
    hyperparameters={
        "n_epochs": 3,  # Number of training passes
        "batch_size": "auto",
        "learning_rate_multiplier": "auto"
    }
)
# Returns: "ftjob-abc123"
```

3. **Monitor Progress**:
```python
status = await trainer.get_job_status(job_id)
# Returns: {"status": "queued" | "running" | "succeeded" | "failed"}

# Or wait for completion
final_status = await trainer.wait_for_completion(
    job_id=job_id,
    poll_interval=60,  # Check every 60s
    max_wait_time=86400  # Max 24 hours
)
```

4. **Test Model**:
```python
response = await trainer.test_model(
    model_id="ft:gpt-4:...",
    test_prompt="Write a message for VP of Sales in SaaS...",
    system_prompt="You are an expert B2B sales copywriter..."
)
# Returns: Generated message from fine-tuned model
```

**Base Model**: `gpt-4o-2024-08-06` (latest GPT-4 with fine-tuning support)

---

### 3. Model Registry (`model_registry.py` + Database)

**Purpose**: Track all models, their performance, and deployment status.

**Database Schema** (`model_registry` table):

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `model_id` | TEXT | OpenAI model ID (e.g., "ft:gpt-4:org:suffix:id") |
| `model_version` | TEXT | Semantic version (e.g., "v2.1.0") |
| `base_model` | TEXT | Base model ("gpt-4o-2024-08-06") |
| `status` | TEXT | 'training' \| 'ready' \| 'deployed' \| 'archived' \| 'failed' |
| `deployed_at` | TIMESTAMPTZ | When deployed |
| `traffic_percentage` | FLOAT | % of traffic (0-100) |
| `ab_test_group` | TEXT | 'control' \| 'variant_a' \| 'variant_b' |
| **Training Stats** |||
| `training_examples_count` | INT | Number of training examples |
| `positive_examples` | INT | Positive examples (deals, meetings) |
| `deals_in_training` | INT | Closed deals in training data |
| **Performance Metrics** |||
| `total_messages_sent` | INT | Messages sent with this model |
| `total_replies` | INT | Replies received |
| `total_meetings_booked` | INT | Meetings booked |
| `total_deals_closed` | INT | Deals closed |
| `total_revenue` | DECIMAL | Total revenue attributed |
| `reply_rate` | FLOAT | Calculated: replies / messages |
| `meeting_rate` | FLOAT | Calculated: meetings / messages |
| `close_rate` | FLOAT | Calculated: deals / messages |
| **Comparison** |||
| `reply_rate_vs_baseline` | FLOAT | % improvement over baseline |
| `meeting_rate_vs_baseline` | FLOAT | % improvement |
| `close_rate_vs_baseline` | FLOAT | % improvement |

**Views**:
- `active_models`: All deployed or ready-to-deploy models
- `model_leaderboard`: Performance rankings (by close rate, reply rate, revenue)

**Usage**:

```python
registry = ModelRegistry(supabase)

# Register new model after training
registry_id = await registry.register_model(
    model_id="ft:gpt-4:org:rekindle-v2-1-0:xyz",
    model_version="v2.1.0",
    base_model="gpt-4o-2024-08-06",
    fine_tuning_job_id="ftjob-abc123",
    training_stats={
        "training_examples_count": 500,
        "positive_examples": 350,
        "deals_in_training": 50
    }
)

# Deploy model
await registry.deploy_model(
    registry_id=registry_id,
    traffic_percentage=100.0,
    ab_test_group="control"
)

# Update performance (called periodically)
await registry.update_model_performance(
    registry_id=registry_id,
    messages_sent=100,
    replies=12,
    meetings_booked=5,
    deals_closed=2,
    revenue=30000.0
)

# Get leaderboard
leaderboard = await registry.get_leaderboard(min_samples=100)
# Returns top models ranked by performance
```

---

### 4. Training Orchestrator (`training_orchestrator.py`)

**Purpose**: Orchestrate the complete weekly training cycle end-to-end.

**Main Method**: `run_training_cycle()`

```python
orchestrator = TrainingOrchestrator(
    supabase=supabase,
    openai_api_key=openai_api_key,
    output_dir="./training_data"
)

result = await orchestrator.run_training_cycle(
    organization_id=None,  # None = global model
    model_version=None,  # Auto-generates v2.1.0, v2.2.0, etc.
    min_quality_score=0.6,
    deploy_immediately=False,  # Manual deployment
    ab_test_percentage=10.0  # If deploying, 10% A/B test
)

# Returns:
{
    "status": "success",
    "model_id": "ft:gpt-4:org:rekindle-v2-1-0:xyz",
    "model_version": "v2.1.0",
    "registry_id": "uuid",
    "job_id": "ftjob-abc123",
    "training_stats": {...},
    "training_duration_seconds": 3600,  # 1 hour
    "deployed": False
}
```

**Weekly Training Flow**:

1. **Check Training Data** (min 50 examples required)
2. **Export to JSONL** (filter by quality score)
3. **Generate Version** (auto-increment: v2.1.0 → v2.2.0)
4. **Upload to OpenAI**
5. **Start Fine-Tuning** (typically 30-60 minutes)
6. **Wait for Completion** (polls every 60s)
7. **Register Model** (add to model_registry)
8. **Test Model** (run sample prompt)
9. **(Optional) Deploy with A/B Test**

**A/B Testing**:

```python
# Set up A/B test: current model (90%) vs new model (10%)
await orchestrator._deploy_with_ab_test(
    new_model_id=new_model_uuid,
    organization_id=None,
    variant_traffic=10.0
)

# After 1 week, promote winner
result = await orchestrator.promote_ab_test_winner(organization_id=None)

# Returns:
{
    "winner": "variant",  # or "control"
    "winner_id": "uuid",
    "improvement_percentage": +15.5,  # 15.5% improvement
    "control_score": 0.045,
    "variant_score": 0.052
}
```

**Performance Score** (weighted):
- Close rate: 50% (most important)
- Meeting rate: 30%
- Reply rate: 20%

**Scheduled Training**:
```python
# Call this from cron job (every Monday 2am UTC)
result = await orchestrator.schedule_weekly_training(
    organization_id=None,
    min_quality_score=0.6,
    deploy_immediately=False  # Manual review before deploy
)
```

---

### 5. API Endpoints (`api_endpoints.py`)

**Purpose**: HTTP API for managing training pipeline.

**Endpoints**:

#### `POST /training/run`
Trigger training cycle manually.

**Request**:
```json
{
  "organization_id": "uuid",  // null for global
  "model_version": "v2.5.0",  // null to auto-generate
  "min_quality_score": 0.6,
  "deploy_immediately": false,
  "ab_test_percentage": 10.0
}
```

**Response**:
```json
{
  "status": "success",
  "model_id": "ft:gpt-4:org:rekindle-v2-5-0:xyz",
  "model_version": "v2.5.0",
  "registry_id": "uuid",
  "training_duration_seconds": 3600,
  "deployed": false
}
```

#### `GET /training/status/{job_id}`
Get status of fine-tuning job.

**Response**:
```json
{
  "id": "ftjob-abc123",
  "status": "succeeded",
  "model": "gpt-4o-2024-08-06",
  "fine_tuned_model": "ft:gpt-4:org:suffix:id",
  "trained_tokens": 50000,
  "finished_at": 1706123456
}
```

#### `GET /training/models?status=deployed`
List all models (filterable by status, organization).

**Response**:
```json
{
  "total": 5,
  "models": [
    {
      "id": "uuid",
      "model_id": "ft:gpt-4:...",
      "model_version": "v2.1.0",
      "status": "deployed",
      "traffic_percentage": 90.0,
      "reply_rate": 0.12,
      "close_rate": 0.02
    }
  ]
}
```

#### `POST /training/deploy/{registry_id}`
Deploy a model to production.

**Request**:
```json
{
  "traffic_percentage": 100.0,
  "ab_test_group": "control"
}
```

#### `POST /training/promote-winner`
Promote A/B test winner to 100% traffic.

**Response**:
```json
{
  "winner": "variant",
  "improvement_percentage": 15.5,
  "control_score": 0.045,
  "variant_score": 0.052
}
```

#### `GET /training/stats`
Get training data statistics.

**Response**:
```json
{
  "total_examples": 500,
  "positive_examples": 350,
  "negative_examples": 100,
  "neutral_examples": 50,
  "deals_closed": 50,
  "meetings_booked": 120,
  "replies": 300
}
```

#### `GET /training/leaderboard?min_samples=100`
Get model performance leaderboard.

**Response**:
```json
{
  "total": 3,
  "leaderboard": [
    {
      "model_id": "ft:gpt-4:...",
      "model_version": "v2.2.0",
      "close_rate": 0.025,
      "reply_rate": 0.14,
      "total_revenue": 150000,
      "close_rate_rank": 1
    }
  ]
}
```

---

## Weekly Training Cycle (Production)

### Setup Cron Job

**On Server** (e.g., Render, Railway, Linux server):

```bash
# Edit crontab
crontab -e

# Add this line: Every Monday at 2am UTC
0 2 * * 1 curl -X POST https://your-api.com/training/run \
  -H "Content-Type: application/json" \
  -d '{"min_quality_score": 0.6, "deploy_immediately": false, "ab_test_percentage": 10.0}'
```

**Or use Python scheduler** (e.g., APScheduler):

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon', hour=2, minute=0)
async def weekly_training():
    orchestrator = create_training_orchestrator(supabase, openai_api_key)
    result = await orchestrator.schedule_weekly_training()
    logger.info(f"Weekly training complete: {result}")

scheduler.start()
```

### Timeline

**Week 1-2**: Capture outcomes (Stage 2)
- Messages sent → Outcomes tracked
- Target: 100+ quality outcomes

**Week 3**: First training cycle
- Export 100+ examples
- Train v2.1.0
- Deploy at 10% (A/B test)

**Week 4**: Monitor A/B test
- Track control vs variant performance
- Promote winner if > 5% improvement

**Week 5+**: Continuous improvement
- Weekly retraining with new outcomes
- Flywheel accelerates (more data → better model → more success → more data)

---

## Cost Estimation

### OpenAI Fine-Tuning Costs (GPT-4o)

**Training**:
- $25 per 1M tokens trained
- Typical training: 50K-100K tokens
- **Cost per training cycle: $1.25 - $2.50**

**Inference** (using fine-tuned model):
- Input: $3.75 per 1M tokens
- Output: $15 per 1M tokens
- Typical message: 500 input + 200 output = 700 tokens
- **Cost per message: $0.004 (0.4 cents)**

**Weekly Training Cost** (52 weeks/year):
- Training: $2.50 × 52 = $130/year
- **Inference** (500K messages/year): $2,000/year
- **Total**: ~$2,130/year

**ROI**: If proprietary model improves close rate by 10%, revenue increase >> training costs.

---

## Success Metrics

Track these to measure flywheel acceleration:

| Metric | Month 1 | Month 3 | Month 6 | Month 12 |
|--------|---------|---------|---------|----------|
| **Training cycles completed** | 1 | 4 | 8 | 16 |
| **Training examples** | 100 | 500 | 2,000 | 10,000 |
| **Model version** | v2.1.0 | v2.4.0 | v2.8.0 | v3.2.0 |
| **Reply rate improvement** | Baseline | +5% | +12% | +20% |
| **Close rate improvement** | Baseline | +8% | +15% | +25% |
| **Models in production** | 1 | 2 | 3 | 5 |

---

## Files Created

```
backend/rex/training_pipeline/
  __init__.py                      # Package exports
  data_formatter.py                # Outcome → GPT-4 format
  model_trainer.py                 # OpenAI fine-tuning API
  model_registry.py                # Model tracking & deployment
  training_orchestrator.py         # End-to-end cycle
  api_endpoints.py                 # FastAPI routes

supabase/migrations/
  20251123000001_create_model_registry.sql  # Database schema

backend/rex/
  app.py                          # Updated: Register training_router

docs/architecture/
  STAGE_3_LLM_TRAINING_PIPELINE.md  # This file
```

---

## Next Steps

### Immediate (Week 1)
- [ ] Apply `model_registry` migration to Supabase
- [ ] Test training cycle with mock data
- [ ] Set up weekly cron job

### Short-Term (Month 1)
- [ ] Run first real training cycle (after 100+ outcomes)
- [ ] Deploy v2.1.0 with 10% A/B test
- [ ] Monitor performance for 1 week
- [ ] Promote winner if improvement > 5%

### Long-Term (Months 2-6)
- [ ] Automate A/B test promotion (if winner > 10% better)
- [ ] Add data warehouse integration (export to Snowflake/BigQuery)
- [ ] Implement multi-organization training (org-specific models)
- [ ] Add training data curation UI (manual labeling for edge cases)
- [ ] Implement ensemble models (combine multiple fine-tuned models)

---

## Stage 4 Preview: Agent Intelligence

Stage 3 gives us the training pipeline. Stage 4 will make agents **use** the trained models and **learn** from their results:

1. **Agent Model Selection**
   - Agents query `active_models` to get deployed model
   - Route traffic based on `traffic_percentage` (A/B test)

2. **Agent Learning from Outcomes**
   - Agents query `get_winning_strategies()` from `agent_outcome_integration`
   - Adapt framework/tone based on what's working

3. **Reinforcement Learning**
   - Track which agent decisions lead to best outcomes
   - Build agent strategy leaderboard
   - Agents auto-optimize based on data

This closes the full loop: **Outcomes → Training → Better Model → Better Agent Decisions → Better Outcomes**

---

**Status**: ✅ Implementation Complete | ⏳ Deployment Pending

**Next Stage**: Agent Intelligence Improvements (Stage 4)
