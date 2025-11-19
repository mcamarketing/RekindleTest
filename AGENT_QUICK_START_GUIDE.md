# 🚀 Rekindle Agent System - Quick Start Guide

**Get your 18-agent system running in 10 minutes**

---

## ⚡ Prerequisites

1. **Database Migration**
   ```bash
   cd supabase
   supabase db push
   ```

2. **Verify Migration**
   ```bash
   supabase db execute -f migrations/verify_agent_tables.sql
   ```
   Should show 7 tables with 0 rows each.

3. **Environment Variables** (see `.env.example`)
   ```bash
   cp .env.example .env
   # Fill in your API keys
   ```

---

## 🎯 Usage Examples

### **Example 1: Research a Lead**

```python
from tools.db_tools import SupabaseDB
from agents.researcher_agents import ResearcherAgent

# Initialize
db = SupabaseDB()
researcher = ResearcherAgent(db=db)

# Research a lead
result = researcher.research_lead(lead_id="lead-uuid-here")

# Output:
# {
#   "lead": {...},
#   "signals": {
#     "profile": {"headline": "VP Marketing", ...},
#     "company_news": [...],
#     "job_postings": [...],
#     "job_changes": [...],
#     "pain_points": ["Hiring for Growth Marketing", "Recent promotion to CMO"]
#   }
# }
```

---

### **Example 2: Auto-ICP from Closed Deals**

```python
from agents.intelligence_agents import ICPAnalyzerAgent, LeadSourcerAgent

# Analyze closed deals to extract ICP
icp_agent = ICPAnalyzerAgent(db=db)
icp_result = icp_agent.analyze_icp(user_id="user-uuid", min_deals=25)

# Output:
# {
#   "icp": {
#     "industry": ["SaaS", "B2B Software"],
#     "job_titles": ["VP Marketing", "CMO"],
#     "company_size": "50-500",
#     "geography": ["US", "UK"]
#   },
#   "confidence_score": 0.85,
#   "deals_analyzed": 30
# }

# Find new leads matching ICP
sourcer = LeadSourcerAgent(db=db)
new_leads = sourcer.find_leads(icp=icp_result["icp"], limit=50)
```

---

### **Example 3: Score Leads**

```python
from agents.intelligence_agents import LeadScorerAgent

scorer = LeadScorerAgent(db=db)

# Score single lead
score = scorer.score_lead(lead_id="lead-uuid", icp=icp_result["icp"])

# Output:
# {
#   "score": 85,
#   "tier": "hot",
#   "breakdown": {
#     "recency": 25,
#     "engagement": 20,
#     "firmographics": 22,
#     "job_signals": 8,
#     "company_signals": 10
#   },
#   "recommendation": "High priority - reach out within 24h"
# }

# Score multiple leads
lead_ids = ["uuid1", "uuid2", "uuid3"]
scored_leads = scorer.score_leads_bulk(lead_ids, icp=icp)
# Returns leads sorted by score (hot leads first)
```

---

### **Example 4: Generate A/B Test Subject Lines**

```python
from agents.content_agents import SubjectLineOptimizerAgent

optimizer = SubjectLineOptimizerAgent(db=db)

# Generate variants
variants = optimizer.generate_variants(
    base_subject="Quick question about your marketing stack",
    lead_context={
        "company": "Acme Inc",
        "pain_points": ["Low email open rates"]
    },
    num_variants=5
)

# Output:
# [
#   {"variant": "Quick question about your marketing stack", "style": "original", "variant_id": "A"},
#   {"variant": "How is Acme Inc handling email open rates?", "style": "question", "variant_id": "B"},
#   {"variant": "[Acme Inc] 3 ways to boost open rates", "style": "urgency", "variant_id": "C"},
#   ...
# ]

# Track performance
optimizer.track_performance(campaign_id="camp-uuid", variant_id="B", opened=True)

# Get winner
winner = optimizer.get_winning_variant(campaign_id="camp-uuid")
```

---

### **Example 5: Handle Inbound Reply**

```python
from agents.sync_agents import TrackerAgent
from agents.content_agents import FollowUpAgent, ObjectionHandlerAgent
from agents.revenue_agents import MeetingBookerAgent, BillingAgent

# Step 1: Classify reply
tracker = TrackerAgent()
classification = tracker.classify("This looks interesting. Can we chat next week?")

# Output:
# {
#   "intent": "MEETING_REQUEST",
#   "sentiment": "Positive",
#   "summary": "This looks interesting. Can we chat next week?"
# }

# Step 2: Handle based on intent
if classification["intent"] == "MEETING_REQUEST":
    # Book meeting
    booker = MeetingBookerAgent(db=db)
    booking = booker.handle_meeting_request(
        user_id="user-uuid",
        lead_email="lead@example.com",
        lead_name="John Doe",
        reply_content=classification["summary"]
    )
    # Returns booking link

elif classification["intent"] == "NOT_INTERESTED":
    # Handle objection
    objection_handler = ObjectionHandlerAgent(db=db)
    response = objection_handler.handle_objection(
        reply_content="Not interested, too expensive",
        lead_name="John Doe"
    )
    # Returns smart objection response

else:
    # Generate follow-up
    follow_up = FollowUpAgent(db=db)
    response = follow_up.generate_follow_up(
        lead_name="John Doe",
        original_message="...",
        reply_content=classification["summary"],
        intent=classification["intent"],
        sentiment=classification["sentiment"]
    )
    # Returns contextual follow-up
```

---

### **Example 6: Launch Campaign with Safety Checks**

```python
from agents.launch_agents import OrchestratorAgent

orchestrator = OrchestratorAgent(db=db)

# Launch campaign (with full safety checks)
result = orchestrator.enqueue_campaign_messages(
    campaign_id="camp-uuid",
    user_id="user-uuid"
)

# Output:
# {
#   "enqueued": 45,
#   "blocked": 5,        # Compliance/quality issues
#   "rate_limited": 10,  # Hit daily limit
#   "errors": 0,
#   "details": [...]
# }

# Single message (for testing)
single_result = orchestrator.enqueue_first_message(
    lead_id="lead-uuid",
    user_id="user-uuid"
)

# Output:
# {
#   "status": "enqueued",
#   "message_id": "msg-uuid",
#   "scheduled_time": "2025-01-03T12:00:00Z",
#   "safety_checks": {
#     "compliance": {"status": "pass"},
#     "quality": {"status": "pass", "score": 85},
#     "rate_limit": {"status": "pass", "remaining": 45}
#   }
# }
```

---

### **Example 7: Manual Safety Checks**

```python
from agents.safety_agents import ComplianceAgent, QualityControlAgent, RateLimitAgent

# Compliance check
compliance = ComplianceAgent(db=db)
can_send = compliance.check_can_send(
    lead_id="lead-uuid",
    email="lead@example.com",
    user_id="user-uuid",
    message_content="Message with unsubscribe link..."
)

# Output:
# {
#   "can_send": True,
#   "checks": {
#     "suppression_list": "pass",
#     "blocked_domain": "pass",
#     "has_unsubscribe_link": "pass",
#     "has_physical_address": "pass"
#   }
# }

# Quality check
quality = QualityControlAgent()
quality_result = quality.check_quality(
    message_content="Your message here",
    subject="Subject line"
)

# Output:
# {
#   "quality_score": 85,
#   "spam_score": 15,
#   "can_send": True,
#   "should_review": False,
#   "issues": [],
#   "warnings": []
# }

# Rate limit check
rate_limit = RateLimitAgent(db=db)
can_send_today = rate_limit.check_can_send_today(user_id="user-uuid")

# Output:
# {
#   "can_send": True,
#   "daily_limit": 100,
#   "sent_today": 45,
#   "remaining": 55
# }
```

---

### **Example 8: Using the Logging Decorator**

```python
from utils.agent_logging import log_agent_execution

class MyCustomAgent:
    def __init__(self, db):
        self.db = db

    @log_agent_execution
    def execute(self, lead_id, user_id, **kwargs):
        """All executions automatically logged to agent_executions table"""

        # Do agent work here
        result = {
            "status": "success",
            "data": "..."
        }

        return result

# Usage
agent = MyCustomAgent(db=db)
result = agent.execute(lead_id="uuid", user_id="uuid")

# Execution automatically logged with:
# - Agent name (MyCustomAgent)
# - Duration
# - Input (lead_id, user_id)
# - Output (result)
# - Success/failure
# - Stack trace if error
```

---

### **Example 9: Monitor Agent Performance**

```sql
-- Get agent success rates (last 7 days)
SELECT
    agent_name,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE status = 'success') as successful,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / COUNT(*), 2) as success_rate_pct,
    AVG(duration_ms) as avg_duration_ms
FROM agent_executions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY agent_name
ORDER BY total_executions DESC;

-- Get slowest executions
SELECT
    agent_name,
    duration_ms,
    error_message,
    created_at
FROM agent_executions
WHERE duration_ms > 5000  -- Slower than 5 seconds
ORDER BY duration_ms DESC
LIMIT 20;

-- Get recent failures
SELECT
    agent_name,
    error_message,
    created_at
FROM agent_executions
WHERE status = 'failure'
ORDER BY created_at DESC
LIMIT 20;
```

---

### **Example 10: Full End-to-End Flow**

```python
from tools.db_tools import SupabaseDB
from agents.researcher_agents import ResearcherAgent
from agents.intelligence_agents import LeadScorerAgent
from agents.writer_agents import WriterAgent
from agents.launch_agents import OrchestratorAgent

# Setup
db = SupabaseDB()
researcher = ResearcherAgent(db=db)
scorer = LeadScorerAgent(db=db)
orchestrator = OrchestratorAgent(db=db)

# 1. Research lead
research = researcher.research_lead(lead_id="lead-uuid")

# 2. Score lead
score = scorer.score_lead(lead_id="lead-uuid")

# 3. If hot lead, generate and send messages
if score["tier"] == "hot":
    # 4. Messages generated by WriterAgent (separate process)
    # ...

    # 5. Launch with safety checks
    result = orchestrator.enqueue_first_message(
        lead_id="lead-uuid",
        user_id="user-uuid"
    )

    if result["status"] == "enqueued":
        print(f"✅ Message enqueued: {result['message_id']}")
    elif result["status"] == "blocked":
        print(f"⚠️ Blocked: {result['reason']}")
    elif result["status"] == "rate_limited":
        print(f"⏰ Rate limited, retry tomorrow")
```

---

## 🔍 Monitoring & Debugging

### **Check Agent Health**
```python
# See REKINDLE_COMPLETE_BUILD_SUMMARY.md for helpful queries
# Or use: supabase/helpful_agent_queries.sql
```

### **Debug Failed Message**
```sql
-- Get full execution chain for a message
SELECT * FROM agent_executions
WHERE lead_id = 'your-lead-uuid'
ORDER BY created_at DESC;

-- Check why message was blocked
SELECT status, metadata
FROM messages
WHERE id = 'your-message-uuid';
```

### **Monitor Revenue**
```sql
-- Get monthly revenue
SELECT
    DATE_TRUNC('month', created_at) as month,
    SUM(amount) / 100.0 as total_gbp,
    COUNT(*) as successful_charges
FROM billing_events
WHERE status = 'succeeded'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;
```

---

## 📚 Agent Reference

| Agent | Purpose | Key Methods |
|-------|---------|-------------|
| ResearcherAgent | LinkedIn research | `research_lead()` |
| ICPAnalyzerAgent | Extract ICP | `analyze_icp()` |
| LeadScorerAgent | Score leads | `score_lead()`, `score_leads_bulk()` |
| LeadSourcerAgent | Find leads | `find_leads()`, `enrich_lead()` |
| EngagementAnalyzerAgent | Engagement tracking | `analyze_engagement()`, `predict_conversion()` |
| SubjectLineOptimizerAgent | A/B testing | `generate_variants()`, `get_winning_variant()` |
| FollowUpAgent | Smart replies | `generate_follow_up()` |
| ObjectionHandlerAgent | Objection handling | `handle_objection()` |
| OrchestratorAgent | Campaign orchestration | `enqueue_first_message()`, `enqueue_campaign_messages()` |
| TrackerAgent | Reply classification | `classify()` |
| MeetingBookerAgent | Meeting booking | `handle_meeting_request()`, `create_meeting()` |
| BillingAgent | Revenue | `charge_for_meeting()` |
| SynchronizerAgent | CRM sync | `handle_reply()`, `create_deal_on_meeting_booked()` |
| ComplianceAgent | Legal compliance | `check_can_send()`, `process_unsubscribe()` |
| QualityControlAgent | Spam detection | `check_quality()`, `calculate_spam_score()` |
| RateLimitAgent | Send limits | `check_can_send_today()`, `get_daily_limit()` |

---

## 🚨 Common Issues

### **"Message blocked by ComplianceAgent"**
- **Cause:** Email on suppression list or missing unsubscribe link
- **Fix:** Check `compliance_result["checks"]` for specific issue

### **"Rate limited"**
- **Cause:** User in warm-up period (Days 1-21)
- **Fix:** Wait until tomorrow, limits increase daily

### **"Spam score too high"**
- **Cause:** Message contains spam trigger words
- **Fix:** Rewrite message, check `quality_result["warnings"]`

### **"No LinkedIn data"**
- **Cause:** MCP server not configured
- **Fix:** Set `LINKEDIN_MCP_URL` environment variable

---

## ✅ Next Steps

1. **Run database migration** (see Prerequisites)
2. **Test one agent** (Example 1)
3. **Test full flow** (Example 10)
4. **Monitor in production** (Example 9)
5. **Check helpful_agent_queries.sql** for more monitoring

---

**Need help?** Check `REKINDLE_COMPLETE_BUILD_SUMMARY.md` for full documentation.

**Ready to scale!** 🚀
