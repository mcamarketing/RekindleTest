# CrewAI Agents - Quick Reference

## 🚀 CLI Commands

```bash
# Dead lead reactivation
python -m backend.crewai_agents dead-lead-reactivation <user_id>

# Full campaign
python -m backend.crewai_agents full-campaign <user_id> <lead_id1> <lead_id2>

# Handle reply
python -m backend.crewai_agents handle-reply <lead_id> "reply text"

# Auto-ICP sourcing
python -m backend.crewai_agents auto-icp <user_id>

# Daily workflow (runs all crews)
python -m backend.crewai_agents daily-workflow <user_id>
```

---

## 🎯 The 3 Crews

| Crew | Agents | Purpose |
|------|--------|---------|
| **DeadLeadReactivationCrew** | 9 | Monitor dormant leads, reactivate when triggers fire |
| **FullCampaignCrew** | 18 | Execute complete campaigns from research to revenue |
| **AutoICPCrew** | 4 | Analyze ICP, source new leads matching it |

---

## 👥 The 18 Agents

### Intelligence (4)
- **ICPAnalyzerAgent** - Extracts ICP from closed deals
- **LeadScorerAgent** - Scores lead revivability
- **LeadSourcerAgent** - Finds new leads matching ICP
- **ResearcherAgent** - Deep lead intelligence

### Content (5)
- **WriterAgent** - Generates personalized sequences
- **SubjectLineOptimizerAgent** - Optimizes subject lines
- **FollowUpAgent** - Generates intelligent follow-ups
- **ObjectionHandlerAgent** - Handles objections
- **EngagementAnalyzerAgent** - Analyzes engagement

### Specialized (1)
- **DeadLeadReactivationAgent** - Monitors 50+ signals for triggers

### Safety (3)
- **ComplianceAgent** - GDPR/CAN-SPAM compliance
- **QualityControlAgent** - Message quality checks
- **RateLimitAgent** - Rate limiting

### Sync (2)
- **TrackerAgent** - Tracks delivery and engagement
- **SynchronizerAgent** - Syncs to CRM

### Revenue (2)
- **MeetingBookerAgent** - Books meetings automatically
- **BillingAgent** - Charges ACV-based fees

### Orchestration (1)
- **OrchestratorAgent** - Coordinates workflows (legacy)

---

## 🔄 Workflow Summary

### Dead Lead Reactivation
```
Dormant Lead → Monitor Triggers → Research → Generate → 
Optimize → Safety Checks → Send → Track → Sync CRM
```

### Full Campaign
```
Lead → Score → Research → Generate Sequence → Optimize → 
Safety Checks → Send → Track → Analyze → Handle Replies → 
Book Meetings → Bill → Sync CRM
```

### Auto-ICP
```
25+ Closed Deals → Analyze ICP → Source Leads → 
Research → Score → Queue High-Scoring Leads
```

---

## 🔐 Safety Checks (All Crews)

Every message must pass:
1. ✅ **ComplianceAgent** - GDPR/CAN-SPAM compliance
2. ✅ **QualityControlAgent** - Message quality
3. ✅ **RateLimitAgent** - Rate limiting

**No message is sent without all 3 checks passing.**

---

## 📊 Python API

```python
from backend.crewai_agents.orchestration_service import OrchestrationService

service = OrchestrationService()

# Dead lead reactivation
result = service.run_dead_lead_reactivation(user_id="user_123")

# Full campaign
result = service.run_full_campaign(
    user_id="user_123",
    lead_ids=["lead_1", "lead_2"]
)

# Handle reply
result = service.handle_inbound_reply(
    lead_id="lead_1",
    reply_text="I'm interested"
)

# Auto-ICP
result = service.run_auto_icp_sourcing(user_id="user_123")

# Daily workflow
result = service.run_daily_workflow(user_id="user_123")
```

---

## 📚 Full Documentation

- **[AGENTS_OVERVIEW.md](./AGENTS_OVERVIEW.md)** - Detailed agent descriptions
- **[CREWS_ARCHITECTURE.md](./CREWS_ARCHITECTURE.md)** - How crews work
- **[CREWS_VISUAL.md](./CREWS_VISUAL.md)** - Visual diagrams
- **[README.md](./README.md)** - Installation and setup






