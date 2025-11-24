# Deployment Guide - Outcome Tracking & LLM Training Pipeline

## 🚀 Quick Start (30 Minutes to Live)

This guide walks you through deploying the complete outcome tracking system and running your first training cycle.

---

## Phase 1: Deploy Outcome Tracking System (10 min)

### Step 1: Apply Database Migrations

```bash
# Navigate to project root
cd c:\Users\Hello\OneDrive\Documents\REKINDLE

# Apply outcome tracking migration
npx supabase db push supabase/migrations/20251123000000_create_outcome_labels.sql

# Apply model registry migration
npx supabase db push supabase/migrations/20251123000001_create_model_registry.sql

# Verify tables created
npx supabase db list
```

**Expected Output:**
```
✓ outcome_labels (created)
✓ model_registry (created)
✓ training_ready_outcomes (view created)
✓ active_models (view created)
✓ model_leaderboard (view created)
```

### Step 2: Configure Webhook Endpoints

**SendGrid Webhook:**
```bash
# URL to provide to SendGrid
https://your-domain.com/webhooks/sendgrid

# Events to track:
- delivered
- open
- click
- bounce
- spam_report
```

**CRM Webhook (HubSpot/Salesforce/Pipedrive):**
```bash
# URL to provide to CRM
https://your-domain.com/webhooks/crm

# Events to track:
- deal.created
- deal.updated
- deal.closed
- meeting.booked
```

### Step 3: Start Backend Services

```bash
# Terminal 1: Start Python API (port 8000)
cd backend
python -m uvicorn api_server:app --reload --port 8000

# Terminal 2: Start Node Scheduler (port 3002)
cd backend/node_scheduler_worker
npm run dev

# Terminal 3: Start Frontend (port 5173)
npm run dev
```

### Step 4: Verify Webhook Endpoints

```bash
# Test SendGrid webhook
curl -X POST http://localhost:8000/webhooks/sendgrid \
  -H "Content-Type: application/json" \
  -d '[{"event":"delivered","email":"test@example.com"}]'

# Expected response: {"status":"processed","events":1}

# Test CRM webhook
curl -X POST http://localhost:8000/webhooks/crm \
  -H "Content-Type: application/json" \
  -d '{"deal_id":"123","status":"closed","amount":15000}'

# Expected response: {"status":"processed"}
```

---

## Phase 2: Collect Baseline Data (2-7 days)

### Minimum Requirements:
- **50+ outcomes** (absolute minimum)
- **100-250 outcomes** (recommended for first training)
- **Quality threshold:** 0.6+ (replies, meetings, or deals)

### Track Your Progress:

```sql
-- Check outcome collection progress
SELECT
  COUNT(*) as total_outcomes,
  COUNT(*) FILTER (WHERE quality_score >= 0.6) as training_ready,
  COUNT(*) FILTER (WHERE replied = true) as replies,
  COUNT(*) FILTER (WHERE meeting_booked = true) as meetings,
  COUNT(*) FILTER (WHERE deal_closed = true) as deals,
  AVG(quality_score) as avg_quality
FROM outcome_labels
WHERE created_at >= NOW() - INTERVAL '7 days';
```

**Example Output:**
```
total_outcomes | training_ready | replies | meetings | deals | avg_quality
---------------|----------------|---------|----------|-------|------------
     142       |       89       |   23    |    12    |   4   |   0.68
```

### What to Track:

1. **Message Sent:**
   ```python
   from backend.rex.outcome_tracker import OutcomeTracker

   tracker = OutcomeTracker(supabase_client)

   outcome_id = await tracker.track_message_sent(
       organization_id="org_123",
       campaign_id="camp_456",
       lead_id="lead_789",
       channel="email",
       message_body="Hey {{first_name}}, saw your recent post about...",
       agent_decisions={
           "framework": "PAS",
           "tone": "consultative",
           "personalization_score": 0.85
       },
       subject_line="Quick question about your sales process"
   )
   ```

2. **Reply Received:**
   ```python
   from backend.rex.sentiment_analyzer import SentimentAnalyzer

   analyzer = SentimentAnalyzer()

   # Analyze reply
   sentiment = await analyzer.analyze_reply(
       reply_text="Thanks for reaching out! I'm interested...",
       original_message=original_message
   )

   # Track reply
   await tracker.track_reply(
       outcome_id=outcome_id,
       reply_text=reply_text,
       sentiment_score=sentiment["sentiment_score"],
       sentiment_label=sentiment["sentiment_label"],
       interest_signal=sentiment["interest_signal"]
   )
   ```

3. **Meeting Booked:**
   ```python
   await tracker.track_meeting_booked(
       outcome_id=outcome_id,
       meeting_time=datetime.now() + timedelta(days=3)
   )
   ```

4. **Deal Closed:**
   ```python
   await tracker.track_deal_closed(
       outcome_id=outcome_id,
       deal_value=15000
   )
   ```

---

## Phase 3: Run First Training Cycle (2 hours)

### Step 1: Export Training Data

```bash
cd backend/rex/training_pipeline

python -c "
from data_formatter import DataFormatter
from supabase import create_client
import os

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

formatter = DataFormatter(supabase)

# Export to JSONL
count = await formatter.export_to_jsonl(
    output_path='./training_data/rekindle_v1_0_0.jsonl',
    organization_id=None,  # All orgs
    min_quality_score=0.6,
    limit=1000
)

print(f'Exported {count} training examples')
"
```

**Expected Output:**
```
✓ Fetched 142 outcomes
✓ Filtered to 89 training-ready examples
✓ Generated 89 training examples
✓ Exported to ./training_data/rekindle_v1_0_0.jsonl
```

### Step 2: Start Training Job

```bash
python -c "
from training_orchestrator import TrainingOrchestrator
from model_trainer import ModelTrainer
from model_registry import ModelRegistry

# Initialize components
trainer = ModelTrainer(openai_client)
registry = ModelRegistry(supabase_client)
orchestrator = TrainingOrchestrator(trainer, registry, formatter)

# Run complete training cycle
result = await orchestrator.run_training_cycle(
    model_version='v1.0.0',
    min_quality_score=0.6,
    deploy_immediately=False  # Manual deployment for first cycle
)

print(f'Training job started: {result[\"job_id\"]}')
print(f'Model version: {result[\"model_version\"]}')
print(f'Training examples: {result[\"training_stats\"][\"total_examples\"]}')
"
```

**Expected Output:**
```
✓ Training data: 89 examples
✓ Quality score avg: 0.68
✓ Uploaded training file: file-abc123
✓ Created fine-tuning job: ftjob-xyz789
✓ Model version: v1.0.0
✓ Status: Training started (ETA: 30-60 minutes)
```

### Step 3: Monitor Training Progress

```bash
# Check training status
python -c "
result = await trainer.get_fine_tuning_status(job_id='ftjob-xyz789')
print(f'Status: {result[\"status\"]}')
print(f'Trained tokens: {result[\"trained_tokens\"]}')
print(f'Model ID: {result[\"fine_tuned_model\"]}')
"
```

**Training Timeline:**
- Upload: 1-2 minutes
- Training: 30-60 minutes (depends on data size)
- Validation: 5 minutes
- Total: ~45-70 minutes

---

## Phase 4: Deploy Model with A/B Test (5 min)

### Step 1: Register Trained Model

```python
from model_registry import ModelRegistry

registry = ModelRegistry(supabase_client)

# Register new model
model_id = await registry.register_model(
    model_id="ft:gpt-4o-mini-2024-07-18:rekindle:v1-0-0:xyz789",
    model_version="v1.0.0",
    training_stats={
        "total_examples": 89,
        "avg_quality_score": 0.68,
        "training_duration_mins": 45
    }
)

print(f"Registered model: {model_id}")
```

### Step 2: Deploy with A/B Test (10% Traffic)

```python
# Set baseline model (current GPT-4)
await registry.set_baseline_model(
    model_id="baseline",
    model_version="gpt-4o-mini"
)

# Deploy new model to 10% of traffic
await registry.deploy_model(
    model_id=model_id,
    traffic_percentage=10.0,
    ab_test_group="variant_a"
)

print("Model deployed to 10% of traffic")
```

### Step 3: Route Requests Through A/B Test

```python
# In your message generation code
from model_registry import ModelRegistry

registry = ModelRegistry(supabase_client)

# Get model for this request (automatically A/B tested)
selected_model = await registry.get_model_for_request(
    organization_id="org_123",
    campaign_id="camp_456"
)

# Use selected model
response = await openai_client.chat.completions.create(
    model=selected_model["model_id"],
    messages=[...],
    temperature=0.7
)
```

---

## Phase 5: Monitor Performance (Ongoing)

### Real-Time Dashboard Queries

**Model Performance Comparison:**
```sql
SELECT
  model_version,
  total_messages_sent,
  reply_rate,
  close_rate,
  reply_rate_vs_baseline,
  close_rate_vs_baseline,
  deployed_at
FROM model_leaderboard
ORDER BY deployed_at DESC
LIMIT 5;
```

**Recent Outcomes:**
```sql
SELECT
  channel,
  framework,
  tone,
  replied,
  reply_sentiment_score,
  meeting_booked,
  deal_closed,
  quality_score,
  created_at
FROM outcome_labels
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY quality_score DESC
LIMIT 20;
```

**Cost Tracking (with LLM Provider Abstraction):**
```python
from llm_providers.model_router import ModelRouter

router = ModelRouter(providers={...})

# Get performance report
report = router.get_performance_report()

for model_id, metrics in report.items():
    print(f"{model_id}:")
    print(f"  Avg cost: ${metrics['avg_cost']:.4f}")
    print(f"  Avg latency: {metrics['avg_latency_ms']:.0f}ms")
    print(f"  Success rate: {metrics['success_rate']:.2%}")
    print(f"  Total requests: {metrics['total_requests']}")
```

### Decision Criteria (1 Week)

After 1 week with 10% traffic, analyze results:

**Promote Variant if:**
- Reply rate improvement: +10% or more
- Close rate improvement: +5% or more
- No increase in negative sentiment
- Cost per meeting: Equal or lower

**Example:**
```
Baseline (GPT-4o-mini):
- Reply rate: 12.3%
- Close rate: 3.1%
- Cost per message: $0.002

Variant (Fine-tuned v1.0.0):
- Reply rate: 15.2% (+23.6% ✓)
- Close rate: 3.8% (+22.6% ✓)
- Cost per message: $0.003 (+50%, but still profitable)

DECISION: Promote variant to 100% traffic
```

**Promote Model:**
```python
await registry.promote_model(
    model_id=model_id,
    traffic_percentage=100.0
)

# Mark previous model as deprecated
await registry.deprecate_model(previous_model_id)
```

---

## Phase 6: Continuous Improvement (Weekly)

### Weekly Training Cycle

```bash
# Automate with cron job (every Monday at 2 AM)
0 2 * * 1 cd /path/to/project && python backend/rex/training_pipeline/training_orchestrator.py run_training_cycle --auto-deploy --traffic=10

# Or manual:
python training_orchestrator.py run_training_cycle \
    --min-quality-score 0.6 \
    --model-version v1.1.0 \
    --deploy-immediately \
    --ab-test-traffic 10
```

### Flywheel Metrics (Track Weekly)

```sql
-- Flywheel velocity
WITH weekly_metrics AS (
  SELECT
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as outcomes,
    COUNT(*) FILTER (WHERE quality_score >= 0.6) as training_examples,
    AVG(reply_sentiment_score) as avg_sentiment
  FROM outcome_labels
  WHERE created_at >= NOW() - INTERVAL '12 weeks'
  GROUP BY week
)
SELECT
  week,
  outcomes,
  training_examples,
  avg_sentiment,
  LAG(avg_sentiment) OVER (ORDER BY week) as prev_sentiment,
  (avg_sentiment - LAG(avg_sentiment) OVER (ORDER BY week)) as sentiment_delta
FROM weekly_metrics
ORDER BY week DESC;
```

**Expected Flywheel Progress:**
```
Week 1:  89 examples, 0.68 sentiment
Week 2:  142 examples, 0.71 sentiment (+4.4%)
Week 3:  234 examples, 0.74 sentiment (+4.2%)
Week 4:  387 examples, 0.78 sentiment (+5.4%)
...
Week 12: 2,450 examples, 0.89 sentiment (+2.1%)
```

### Model Generation Strategy

**Version Naming:**
- Major: Breaking changes to training format
- Minor: New training data batch
- Patch: Bug fixes only

**Example Timeline:**
```
v1.0.0 - Week 1:  89 examples (baseline)
v1.1.0 - Week 2:  +53 examples (total: 142)
v1.2.0 - Week 3:  +92 examples (total: 234)
v1.3.0 - Week 4:  +153 examples (total: 387)
v2.0.0 - Month 2: New training format with multi-channel
```

---

## Troubleshooting

### Issue: Not enough training data
**Solution:** Lower `min_quality_score` to 0.5 temporarily, or wait for more outcomes

### Issue: Training job failed
**Solution:** Check OpenAI dashboard for error details, verify JSONL format

### Issue: Model worse than baseline
**Solution:**
1. Check training data quality
2. Verify sentiment analysis accuracy
3. Ensure enough positive examples (not just negative)

### Issue: Webhook not receiving events
**Solution:**
1. Verify webhook URL is publicly accessible
2. Check SendGrid/CRM webhook configuration
3. Test with `curl` or Postman
4. Check API logs for errors

---

## Security Checklist

- ✅ Supabase RLS policies enabled (multi-tenant isolation)
- ✅ API keys in environment variables (never committed)
- ✅ Webhook endpoints have signature verification
- ✅ Rate limiting enabled (100 req/min per org)
- ✅ Training data excludes PII by default
- ✅ Model artifacts stored securely (OpenAI managed)

---

## Cost Estimation

### Training Costs (GPT-4o-mini):
- **Upload:** Free
- **Training:** $0.003/1K tokens × training data
  - 89 examples × ~500 tokens avg = 44,500 tokens
  - Cost: $0.003 × 44.5 = **$0.13**
- **Inference:** $0.00015/1K input, $0.0006/1K output
  - 1,000 messages × 1K tokens = $0.75/day
  - **$22.50/month** for 1,000 messages/day

### Alternative (Llama-3.1-70B via Together AI):
- **Training:** $0.0009/1K tokens = **$0.04** (70% cheaper)
- **Inference:** $0.0009/1K tokens = **$27/month**
- **Break-even:** Similar cost, but full ownership

### Hybrid Approach (Recommended):
- GPT-4o for complex: 20% traffic = $4.50/month
- Llama-3.1-70B for simple: 80% traffic = $21.60/month
- **Total: $26.10/month** (vs $22.50 all-GPT-4)
- **Benefit:** No vendor lock-in, can scale to local deployment

---

## Success Metrics

### Week 1 (Baseline):
- ✅ Outcome tracking live
- ✅ 100+ outcomes captured
- ✅ First model trained and deployed
- ✅ A/B test running (10% traffic)

### Month 1 (Flywheel Spinning):
- ✅ 500+ outcomes captured
- ✅ 3-4 model iterations deployed
- ✅ 15%+ reply rate achieved
- ✅ Cost per meeting < $350

### Month 3 (Flywheel Accelerating):
- ✅ 2,000+ outcomes captured
- ✅ 10+ model iterations
- ✅ 20%+ reply rate (2.5x industry avg)
- ✅ Cost per meeting < $250
- ✅ 3-5 pilot customers contributing data

### Year 1 (Competitive Moat):
- ✅ 50,000+ outcomes (6-month lead on competitors)
- ✅ 25%+ reply rate (3x industry avg)
- ✅ 50+ customers in flywheel
- ✅ Proprietary model outperforms GPT-4

---

## Next Steps

1. **Apply migrations:** `npx supabase db push`
2. **Configure webhooks:** SendGrid + CRM
3. **Start collecting data:** Run campaigns
4. **Monitor progress:** Check outcome_labels daily
5. **First training cycle:** When 100+ outcomes collected
6. **Deploy with A/B test:** 10% traffic
7. **Monitor for 1 week:** Compare metrics
8. **Promote or iterate:** Based on results
9. **Repeat weekly:** Continuous improvement

**The flywheel is ready. Deploy, measure, iterate, expand, and let it run! 🚀**
