# Stage 2: Outcome Tracking Implementation

**Date**: 2025-01-23
**Status**: ✅ Complete
**Branch**: `feat/rex-special-forces`
**Part of**: Flywheel Architecture - Data Capture Infrastructure

---

## Overview

Stage 2 implements the **data capture infrastructure** for the Proprietary LLM Brain Loop. This is the foundation that enables Rex to learn from every message → outcome chain and continuously improve through GPT-4 fine-tuning.

### Core Concept

```
Message Sent (with agent decisions)
     ↓
Outcome Labels Table (captures everything)
     ↓
Webhooks Update Outcomes (delivery, opens, clicks, replies, deals)
     ↓
Sentiment Analysis (classifies replies)
     ↓
Training Dataset (ready for GPT-4 fine-tuning)
     ↓
Improved LLM Brain → Better Agent Decisions
```

---

## What Was Implemented

### 1. Database Schema: `outcome_labels` Table

**File**: `supabase/migrations/20251123000000_create_outcome_labels.sql`

**Purpose**: Central table that captures every message → outcome chain for LLM training.

**Key Fields**:

| Category | Fields | Purpose |
|----------|--------|---------|
| **Message** | `subject_line`, `message_body`, `channel` | What we sent |
| **Agent Decisions** | `framework`, `tone`, `agent_decisions` (JSON) | What the AI decided |
| **Delivery** | `delivered`, `bounced`, `bounce_reason` | Did it arrive? |
| **Engagement** | `opened`, `clicked`, `open_count`, `click_count` | Did they engage? |
| **Reply** | `replied`, `reply_text`, `reply_sentiment_score` | What did they say? |
| **Sentiment** | `sentiment_label`, `objection_type`, `interest_signal` | How interested are they? |
| **Meeting** | `meeting_booked`, `meeting_completed`, `meeting_no_show` | Did we get a meeting? |
| **Revenue** | `deal_closed`, `deal_value`, `time_to_close_days` | Did we close revenue? |
| **Context** | `lead_industry`, `lead_role`, `company_size`, `icp_score` | Who are they? |
| **Training** | `training_label`, `training_weight`, `included_in_training` | Ready for LLM? |

**Indexes**:
- Organization, campaign, lead lookups
- Training data queries
- Time-series analysis
- Deal closed tracking

**Row-Level Security (RLS)**:
- Users only see their organization's outcomes
- Service role can insert/update (for webhooks)

**View**: `training_ready_outcomes`
- Pre-filtered view of outcomes ready for export to data warehouse
- Used by ETL pipeline for GPT-4 training

---

### 2. Outcome Tracker

**File**: `backend/rex/outcome_tracker.py`

**Purpose**: Python API for tracking message outcomes throughout their lifecycle.

**Key Methods**:

```python
tracker = OutcomeTracker(supabase)

# When message is sent
outcome_id = await tracker.track_message_sent(
    organization_id=org_id,
    campaign_id=campaign_id,
    lead_id=lead_id,
    channel='email',
    message_body=message,
    agent_decisions={
        'PersonalizerAgent': {'framework': 'PAS', 'tone': 'professional'},
        'CopywriterAgent': {'subject': 'Transform your sales', 'hooks': ['curiosity']}
    },
    lead_context={'industry': 'SaaS', 'role': 'VP Sales'}
)

# When webhooks fire
await tracker.track_delivery(outcome_id, delivered=True)
await tracker.track_opened(outcome_id)
await tracker.track_clicked(outcome_id)
await tracker.track_reply(outcome_id, reply_text="Interested!", sentiment_score=0.8)
await tracker.track_meeting_booked(outcome_id)
await tracker.track_deal_closed(outcome_id, deal_value=15000)
```

**Training Labels**:
- `positive_example`: High engagement, meeting booked, or deal closed (weight: 3.0-10.0)
- `negative_example`: Bounced, unsubscribed, or negative reply (weight: 0.5-2.0)
- `neutral`: Delivered but no strong signal (weight: 1.0)

**Weight System**:
- Closed deals: 10.0 (highest priority for learning)
- Completed meetings: 7.0
- Booked meetings: 5.0
- Interested replies: 3.0
- Objections: 2.0 (learn from failures)
- Neutral replies: 1.0
- Bounces: 0.5

---

### 3. Webhooks for Real-Time Updates

#### SendGrid Webhook

**File**: `backend/rex/webhooks/sendgrid_webhook.py`

**Endpoint**: `POST /webhooks/sendgrid`

**Purpose**: Capture email delivery events in real-time.

**Events Tracked**:
- `delivered`: Email successfully delivered
- `bounce` / `dropped`: Email bounced (hard/soft)
- `open`: Email opened (tracks count)
- `click`: Link clicked (tracks count)
- `spamreport`: Marked as spam
- `unsubscribe`: Unsubscribed

**Setup**:
1. SendGrid Dashboard → Settings → Mail Settings → Event Webhook
2. Set HTTP POST URL: `https://your-api.com/webhooks/sendgrid`
3. Enable events: delivered, bounce, open, click, spam_report
4. (Optional) Configure webhook signature verification with `SENDGRID_WEBHOOK_SECRET`

**Custom Args**:
When sending emails via SendGrid, include:
```python
sendgrid.send(
    to=lead.email,
    subject=subject,
    body=message,
    custom_args={
        'outcome_id': str(outcome_id),  # Links event to outcome_labels row
        'campaign_id': str(campaign_id)
    }
)
```

**Security**:
- HMAC SHA256 signature verification (if `SENDGRID_WEBHOOK_SECRET` set)
- Validates `X-Twilio-Email-Event-Webhook-Signature` header

#### CRM Webhook

**File**: `backend/rex/webhooks/crm_webhook.py`

**Endpoints**:
- `POST /webhooks/crm/deals` - Deal/opportunity events
- `POST /webhooks/crm/meetings` - Meeting completion events

**Purpose**: Capture revenue outcomes from CRM systems.

**Events Tracked**:
- `opportunity.created`: New deal created
- `deal.closed_won`: Deal closed successfully
- `deal.closed_lost`: Deal lost
- `meeting.completed`: Meeting/demo completed
- `meeting.no_show`: Meeting no-show

**Supported CRMs** (auto-detects format):
- HubSpot
- Salesforce
- Pipedrive
- Generic JSON format

**Example Payload** (generic format):
```json
{
  "event": "deal.closed_won",
  "deal_id": "123",
  "deal_value": 15000,
  "closed_at": "2025-01-23T10:00:00Z",
  "contact_email": "lead@example.com",
  "outcome_id": "uuid"
}
```

**Setup**:
1. Configure webhook in your CRM
2. Point to: `https://your-api.com/webhooks/crm/deals`
3. (Optional) Set `CRM_WEBHOOK_SECRET` for signature verification
4. Pass `outcome_id` when creating CRM deal (for linking)

**Auto-Linking**:
If `outcome_id` not provided, webhook attempts to find outcome by:
1. Lead ID (if provided)
2. Contact email (lookup through leads table)

---

### 4. Sentiment Analysis

**File**: `backend/rex/sentiment_analyzer.py`

**Purpose**: Classify lead replies using GPT-4 for nuanced B2B sales understanding.

**Analysis Output**:
```python
analyzer = SentimentAnalyzer(openai_api_key)

result = await analyzer.analyze_reply(
    reply_text="Love this! Let's schedule a call next week.",
    original_message=our_message,
    context={'industry': 'SaaS', 'role': 'VP Sales'}
)

# Returns:
{
    "sentiment_score": 0.85,  # -1.0 (negative) to 1.0 (positive)
    "sentiment_label": "positive",  # positive | neutral | negative
    "interest_signal": True,  # Is lead interested?
    "interest_level": "high",  # high | medium | low | none
    "objection_detected": False,  # Did they object?
    "objection_type": "none",  # price | timing | authority | competitor | not_interested | no_need
    "reasoning": "Lead expresses enthusiasm ('Love this!') and proactively suggests scheduling a call, indicating high interest."
}
```

**Classification Guidelines**:

**Sentiment Ranges**:
- **Positive (0.5 to 1.0)**: Enthusiastic, interested, asking questions
- **Neutral (-0.2 to 0.5)**: Polite acknowledgment, non-committal
- **Negative (-1.0 to -0.2)**: Rejection, annoyance, unsubscribe

**Interest Levels**:
- **High**: "Let's schedule", "Tell me more", asks specific questions
- **Medium**: "Maybe", "Keep me posted", asks vague questions
- **Low**: Minimal engagement, very short reply
- **None**: No interest signal

**Objection Types**:
- **Price**: Mentions cost, budget, expensive
- **Timing**: "Not right now", "Maybe next quarter"
- **Authority**: "Need to check with my boss"
- **Competitor**: "We're using X already"
- **Not Interested**: Direct rejection, unsubscribe
- **No Need**: "We don't need this"

**Fallback**: If GPT-4 fails, uses rule-based classification with keyword matching.

**Batch Processing**: `analyze_batch()` method for processing historical replies.

---

### 5. Agent-Outcome Integration

**File**: `backend/rex/agent_outcome_integration.py`

**Purpose**: Bridge between Rex agents and outcome tracking system.

**Usage in Agent Workflows**:

```python
from backend.rex.agent_outcome_integration import AgentOutcomeIntegration

# Initialize
integration = AgentOutcomeIntegration(supabase, openai_api_key)

# STEP 1: When PersonalizerAgent + CopywriterAgent create message
agent_decisions = {
    'PersonalizerAgent': {
        'framework': 'PAS',  # Problem-Agitate-Solution
        'tone': 'professional',
        'personalization_applied': ['first_name', 'company', 'pain_point']
    },
    'CopywriterAgent': {
        'subject_line': 'Transform your sales process',
        'hooks_used': ['curiosity', 'social_proof'],
        'cta': 'book_meeting'
    },
    'DeliverabilityAgent': {
        'domain_selected': 'team@rekindle.io',
        'send_time': '2025-01-23T14:30:00Z',
        'warmup_score': 0.85
    }
}

outcome_id = await integration.track_agent_message(
    organization_id=org_id,
    campaign_id=campaign_id,
    lead_id=lead_id,
    channel='email',
    message_body=personalized_message,
    agent_decisions=agent_decisions,
    subject_line=subject,
    lead_context={'industry': 'SaaS', 'role': 'VP Sales', 'icp_score': 0.85}
)

# Store outcome_id with sent message for later tracking
# (e.g., pass as custom_arg to SendGrid, or store in sent_messages table)

# STEP 2: When reply comes in (via webhook or manual entry)
analysis = await integration.process_reply(
    outcome_id=outcome_id,
    reply_text="Interested! Can we schedule a call?",
    replied_at=datetime.now()
)
# Automatically runs sentiment analysis and updates outcome

# STEP 3: Agents learn from outcomes
performance = await integration.get_agent_performance(campaign_id)
# Returns: Which frameworks, tones, strategies are working best

winning_strategies = await integration.get_winning_strategies(
    organization_id=org_id,
    metric='reply_rate',  # or 'meeting_rate', 'close_rate'
    min_samples=10
)
# Returns: Top 10 strategies sorted by performance
# Agents use this to adapt and improve
```

**Learning Methods**:

1. **`get_agent_performance(campaign_id, agent_name)`**
   - Returns performance breakdown by framework, tone, strategy
   - Shows: delivery rate, open rate, reply rate, meeting rate, close rate, avg deal value
   - Used by agents to understand what's working in this campaign

2. **`get_winning_strategies(organization_id, metric, min_samples)`**
   - Returns top strategies across all campaigns for this organization
   - Filters by minimum sample size (statistical significance)
   - Sorted by chosen metric (reply_rate, meeting_rate, close_rate)
   - Used by agents to learn cross-campaign patterns

**Example Performance Output**:
```python
{
    'campaign_id': 'uuid',
    'agent_name': 'PersonalizerAgent',
    'total_outcomes': 500,
    'strategy_performance': {
        'PAS_professional': {
            'framework': 'PAS',
            'tone': 'professional',
            'total_sent': 200,
            'delivery_rate': 0.95,
            'open_rate': 0.35,
            'reply_rate': 0.12,  # 12% reply rate
            'meeting_rate': 0.05,  # 5% booked meeting
            'close_rate': 0.02,  # 2% closed deal
            'avg_deal_value': 15000
        },
        'AIDA_casual': {
            'framework': 'AIDA',
            'tone': 'casual',
            'total_sent': 150,
            'reply_rate': 0.08,  # Only 8% reply rate (worse)
            ...
        }
    }
}
```

---

## Integration Points

### How Agents Use This System

#### PersonalizerAgent
```python
# Before sending message
winning = await integration.get_winning_strategies(org_id, metric='reply_rate')

# Choose framework/tone from winning strategies
best_strategy = winning[0]  # Top performer
framework = best_strategy['framework']  # e.g., 'PAS'
tone = best_strategy['tone']  # e.g., 'professional'

# Personalize message using winning strategy
message = personalize(lead, framework=framework, tone=tone)

# Track decision
outcome_id = await integration.track_agent_message(
    ...,
    agent_decisions={'PersonalizerAgent': {'framework': framework, 'tone': tone}}
)
```

#### CopywriterAgent
```python
# Analyze which hooks/CTAs work best
performance = await integration.get_agent_performance(campaign_id, 'CopywriterAgent')

# Adapt based on what's working
if performance['strategy_performance']['curiosity_book_meeting']['reply_rate'] > 0.15:
    # Use curiosity hook with book_meeting CTA
    pass
```

#### ICPIntelligenceAgent
```python
# Learn which ICP profiles convert best
outcomes = await tracker.get_training_ready_outcomes(org_id)

high_converting_icps = [
    o for o in outcomes
    if o['deal_closed'] and o['icp_score'] > 0.8
]

# Update ICP model based on patterns in high_converting_icps
```

---

## Environment Variables

Add to `.env` and deployment platforms:

```bash
# Webhook Security (Optional but Recommended)
SENDGRID_WEBHOOK_SECRET=<generate with: openssl rand -hex 32>
CRM_WEBHOOK_SECRET=<generate with: openssl rand -hex 32>

# OpenAI (Required for Sentiment Analysis)
OPENAI_API_KEY=sk-proj-...

# Supabase (Already configured)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

---

## Testing Webhooks Locally

### SendGrid Webhook
```bash
# 1. Expose local server with ngrok
ngrok http 8081

# 2. Configure SendGrid webhook to: https://your-ngrok-url.ngrok.io/webhooks/sendgrid

# 3. Send test email
curl -X POST http://localhost:8081/webhooks/sendgrid \
  -H "Content-Type: application/json" \
  -d '[
    {
      "email": "test@example.com",
      "event": "delivered",
      "timestamp": 1706000000,
      "sg_message_id": "test123",
      "outcome_id": "your-outcome-uuid"
    }
  ]'
```

### CRM Webhook
```bash
curl -X POST http://localhost:8081/webhooks/crm/deals \
  -H "Content-Type: application/json" \
  -d '{
    "event": "deal.closed_won",
    "deal_id": "123",
    "deal_value": 15000,
    "closed_at": "2025-01-23T10:00:00Z",
    "outcome_id": "your-outcome-uuid"
  }'
```

---

## Database Migration

To apply the `outcome_labels` schema:

```bash
# Via Supabase CLI
cd supabase/migrations
supabase db push

# OR manually via Supabase SQL Editor
# Copy/paste contents of 20251123000000_create_outcome_labels.sql
```

**Verify Migration**:
```sql
-- Check table exists
SELECT * FROM outcome_labels LIMIT 1;

-- Check view exists
SELECT * FROM training_ready_outcomes LIMIT 1;

-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE tablename = 'outcome_labels';
-- Should show rowsecurity = true
```

---

## Next Steps (Stage 3: LLM Training Pipeline)

Stage 2 captures the data. Stage 3 will:

1. **Data Warehouse ETL**
   - Export `training_ready_outcomes` to data warehouse (Snowflake/BigQuery)
   - Transform into GPT-4 fine-tuning format (JSONL)
   - Schedule daily/weekly exports

2. **GPT-4 Fine-Tuning Pipeline**
   - Format outcomes as training examples:
     ```json
     {
       "messages": [
         {"role": "system", "content": "You are a B2B sales expert..."},
         {"role": "user", "content": "Context: SaaS, VP Sales, ICP 0.85\nTask: Write personalized message"},
         {"role": "assistant", "content": "Subject: Transform...\nBody: Hi {{first_name}}, ..."}
       ]
     }
     ```
   - Upload to OpenAI fine-tuning API
   - Train model weekly
   - Deploy new model version
   - A/B test against current model

3. **Model Versioning**
   - Track model versions in database
   - Compare performance (v1 vs v2 vs v3)
   - Rollback if new model underperforms

4. **Continuous Learning**
   - Every week: Export new outcomes → Retrain model → Deploy
   - Flywheel accelerates: More data → Better model → Better results → More users → More data

---

## Success Metrics

Track these to measure flywheel progress:

| Metric | Week 1 | Month 3 | Month 6 | Target |
|--------|--------|---------|---------|--------|
| **Outcome labels captured** | 100 | 5,000 | 25,000 | 100,000+/year |
| **Training-ready examples** | 20 | 1,000 | 5,000 | 20,000+ |
| **Reply sentiment accuracy** | 85% | 90% | 95% | 95%+ |
| **Webhook uptime** | 99% | 99.9% | 99.9% | 99.9% |
| **Deal attribution** | 50% | 75% | 90% | 95%+ |

---

## Files Created

```
supabase/migrations/
  20251123000000_create_outcome_labels.sql  (Database schema)

backend/rex/
  outcome_tracker.py                        (Core tracking API)
  sentiment_analyzer.py                     (GPT-4 reply classification)
  agent_outcome_integration.py              (Agent integration layer)

  webhooks/
    __init__.py                             (Webhook exports)
    sendgrid_webhook.py                     (Email events)
    crm_webhook.py                          (Deal/meeting events)

backend/rex/
  app.py                                    (Updated: Register webhook routers)

docs/architecture/
  STAGE_2_OUTCOME_TRACKING.md               (This file)
```

---

## Status

- [x] Database schema created
- [x] Outcome tracker implemented
- [x] Webhooks implemented (SendGrid, CRM)
- [x] Sentiment analysis implemented
- [x] Agent integration layer created
- [x] Webhooks registered in FastAPI app
- [x] Documentation written
- [ ] Database migration applied (requires Supabase access)
- [ ] Webhooks configured in SendGrid (requires SendGrid account)
- [ ] Webhooks configured in CRM (requires CRM account)
- [ ] End-to-end testing

**Ready for**: Deployment and webhook configuration

**Next Stage**: LLM Training Pipeline (GPT-4 fine-tuning)
