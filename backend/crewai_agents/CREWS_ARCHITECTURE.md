# CrewAI Crews Architecture

## Overview

Rekindle uses **3 specialized crews** that coordinate all **18 agents** to work together as a unified system. Each crew handles a specific workflow, and all crews are orchestrated by the `OrchestrationService`.

---

## 🎯 The 3 Crews

### 1. **DeadLeadReactivationCrew** (9 Agents)
**Purpose:** Monitor dormant leads 24/7 and reactivate them when trigger events occur.

**Agents Working Together:**
1. **DeadLeadReactivationAgent** - Monitors 50+ signals per lead for trigger events
2. **ResearcherAgent** - Deep research when trigger detected
3. **WriterAgent** - Generates personalized trigger-specific message
4. **SubjectLineOptimizerAgent** - Optimizes subject line for maximum open rate
5. **ComplianceAgent** - GDPR/CAN-SPAM compliance check
6. **QualityControlAgent** - Message quality validation
7. **RateLimitAgent** - Domain/account rate limiting
8. **TrackerAgent** - Tracks message delivery and engagement
9. **SynchronizerAgent** - Syncs to CRM after sending

**Workflow:**
```
Dormant Lead → Monitor Triggers → Research → Generate Message → 
Optimize Subject → Compliance Check → Quality Check → Rate Limit Check → 
Queue for Sending → Track → Sync to CRM
```

**When It Runs:**
- Continuously monitors all dormant leads
- Runs in batches (50 leads at a time)
- Triggered by external events (funding, hiring, job changes, etc.)

---

### 2. **FullCampaignCrew** (All 18 Agents)
**Purpose:** Execute complete campaigns from research to revenue.

**Agents Working Together:**
1. **LeadScorerAgent** - Scores lead revivability
2. **ResearcherAgent** - Deep lead intelligence
3. **WriterAgent** - Generates multi-channel sequence
4. **SubjectLineOptimizerAgent** - Optimizes all subject lines
5. **ComplianceAgent** - Compliance validation
6. **QualityControlAgent** - Quality assurance
7. **RateLimitAgent** - Rate limiting
8. **TrackerAgent** - Tracks delivery and engagement
9. **EngagementAnalyzerAgent** - Analyzes engagement patterns
10. **FollowUpAgent** - Generates intelligent follow-ups
11. **ObjectionHandlerAgent** - Handles objections automatically
12. **MeetingBookerAgent** - Books meetings from replies
13. **BillingAgent** - Charges ACV-based performance fees
14. **SynchronizerAgent** - Syncs everything to CRM
15. **ICPAnalyzerAgent** - (Used for optimization)
16. **LeadSourcerAgent** - (Used for new lead sourcing)
17. **DeadLeadReactivationAgent** - (Can trigger reactivation)
18. **OrchestratorAgent** - (Coordinates the workflow)

**Workflow:**
```
Lead → Score → Research → Generate Sequence → Optimize Subjects → 
Safety Checks (Compliance/Quality/Rate Limit) → Send → Track → 
Analyze Engagement → Handle Replies → Book Meetings → Bill → Sync CRM
```

**When It Runs:**
- For new leads imported by user
- For leads queued by Auto-ICP crew
- For leads manually triggered by user

---

### 3. **AutoICPCrew** (4 Agents)
**Purpose:** Automatically analyze closed deals to extract ICP, then source new leads matching that ICP.

**Agents Working Together:**
1. **ICPAnalyzerAgent** - Analyzes 25+ closed deals to extract ICP patterns
2. **LeadSourcerAgent** - Finds new leads matching the ICP
3. **ResearcherAgent** - Researches new leads
4. **LeadScorerAgent** - Scores new leads for revivability

**Workflow:**
```
25+ Closed Deals → Analyze ICP → Source Matching Leads → 
Research Leads → Score Leads → Queue High-Scoring Leads for Campaign
```

**When It Runs:**
- Automatically when user has 25+ closed deals
- Can be manually triggered
- Runs daily for qualifying users

---

## 🎼 OrchestrationService

The `OrchestrationService` is the **master coordinator** that runs all crews.

### Main Methods:

1. **`run_dead_lead_reactivation(user_id)`**
   - Runs DeadLeadReactivationCrew
   - Monitors dormant leads and reactivates those with triggers

2. **`run_full_campaign(user_id, lead_ids)`**
   - Runs FullCampaignCrew
   - Executes complete campaigns for specified leads

3. **`handle_inbound_reply(lead_id, reply_text)`**
   - Uses FullCampaignCrew to handle replies
   - Routes to MeetingBookerAgent, ObjectionHandlerAgent, or FollowUpAgent

4. **`run_auto_icp_sourcing(user_id)`**
   - Runs AutoICPCrew
   - Analyzes ICP and sources new leads

5. **`run_daily_workflow(user_id)`**
   - **Runs all crews in sequence:**
     1. Dead lead reactivation
     2. Auto-ICP sourcing (if qualified)
     3. Campaign execution (for queued leads)
     4. Engagement analysis

---

## 🔄 How All 18 Agents Work Together

### Agent Roles by Category:

#### **Intelligence Agents (4)**
- **ICPAnalyzerAgent** - Extracts ICP from closed deals
- **LeadScorerAgent** - Scores lead revivability
- **LeadSourcerAgent** - Finds new leads matching ICP
- **ResearcherAgent** - Deep lead intelligence

#### **Content Agents (5)**
- **WriterAgent** - Generates personalized sequences
- **SubjectLineOptimizerAgent** - Optimizes subject lines
- **FollowUpAgent** - Generates intelligent follow-ups
- **ObjectionHandlerAgent** - Handles objections
- **EngagementAnalyzerAgent** - Analyzes engagement

#### **Specialized Agents (1)**
- **DeadLeadReactivationAgent** - Monitors 50+ signals for trigger events

#### **Safety Agents (3)**
- **ComplianceAgent** - GDPR/CAN-SPAM compliance
- **QualityControlAgent** - Message quality checks
- **RateLimitAgent** - Rate limiting

#### **Sync Agents (2)**
- **TrackerAgent** - Tracks delivery and engagement
- **SynchronizerAgent** - Syncs to CRM

#### **Revenue Agents (2)**
- **MeetingBookerAgent** - Books meetings automatically
- **BillingAgent** - Charges ACV-based fees

#### **Orchestration Agent (1)**
- **OrchestratorAgent** - Coordinates workflows (legacy, now handled by crews)

---

## 📊 Complete Workflow Example

### Scenario: User imports 1,000 dormant leads

1. **Initial Processing (FullCampaignCrew)**
   - LeadScorerAgent scores all 1,000 leads
   - High-scoring leads (score ≥ 70) queued for campaign
   - Low-scoring leads marked as "dormant"

2. **Campaign Execution (FullCampaignCrew)**
   - ResearcherAgent researches each queued lead
   - WriterAgent generates personalized sequence
   - SubjectLineOptimizerAgent optimizes subject lines
   - Safety checks (Compliance, Quality, Rate Limit)
   - Messages sent

3. **Ongoing Monitoring (DeadLeadReactivationCrew)**
   - DeadLeadReactivationAgent monitors dormant leads 24/7
   - When trigger detected (e.g., funding round):
     - ResearcherAgent does deep research
     - WriterAgent crafts trigger-specific message
     - Safety checks pass
     - Message sent
     - TrackerAgent tracks delivery
     - SynchronizerAgent syncs to CRM

4. **Reply Handling (FullCampaignCrew)**
   - Lead replies to email
   - TrackerAgent classifies reply
   - If meeting request → MeetingBookerAgent books meeting
   - If objection → ObjectionHandlerAgent handles it
   - If question → FollowUpAgent generates answer
   - BillingAgent charges performance fee (if meeting booked)
   - SynchronizerAgent syncs to CRM

5. **Auto-ICP Sourcing (AutoICPCrew)**
   - After 25 meetings booked and closed:
   - ICPAnalyzerAgent extracts ICP
   - LeadSourcerAgent finds 500 new leads matching ICP
   - ResearcherAgent researches new leads
   - LeadScorerAgent scores new leads
   - High-scoring leads queued for campaign

6. **Engagement Analysis (FullCampaignCrew)**
   - EngagementAnalyzerAgent analyzes all leads
   - Identifies hot/warm/cold segments
   - Recommends next actions
   - Optimizes future campaigns

---

## 🚀 Usage Examples

### CLI Usage:

```bash
# Run dead lead reactivation
python -m backend.crewai_agents dead-lead-reactivation <user_id>

# Run full campaign
python -m backend.crewai_agents full-campaign <user_id> <lead_id1> <lead_id2>

# Handle inbound reply
python -m backend.crewai_agents handle-reply <lead_id> "I'm interested, let's talk"

# Run Auto-ICP sourcing
python -m backend.crewai_agents auto-icp <user_id>

# Run complete daily workflow
python -m backend.crewai_agents daily-workflow <user_id>
```

### Python API Usage:

```python
from backend.crewai_agents.orchestration_service import OrchestrationService

service = OrchestrationService()

# Run dead lead reactivation
result = service.run_dead_lead_reactivation(user_id="user_123")

# Run full campaign
result = service.run_full_campaign(
    user_id="user_123",
    lead_ids=["lead_1", "lead_2", "lead_3"]
)

# Handle reply
result = service.handle_inbound_reply(
    lead_id="lead_1",
    reply_text="I'm interested, let's schedule a call"
)

# Run Auto-ICP
result = service.run_auto_icp_sourcing(user_id="user_123")

# Run daily workflow (runs all crews)
result = service.run_daily_workflow(user_id="user_123")
```

---

## 🔐 Safety & Compliance

All crews include **mandatory safety checks**:

1. **ComplianceAgent** - Ensures GDPR/CAN-SPAM compliance
   - Checks suppression lists
   - Validates consent
   - Verifies opt-out handling

2. **QualityControlAgent** - Ensures message quality
   - Checks for spam triggers
   - Validates personalization
   - Ensures brand voice consistency

3. **RateLimitAgent** - Prevents domain reputation damage
   - Limits sends per domain
   - Throttles based on account tier
   - Prevents spam folder placement

**No message is sent without all 3 checks passing.**

---

## 📈 Performance & Scalability

- **DeadLeadReactivationCrew**: Processes 50 leads per batch
- **FullCampaignCrew**: Processes leads in parallel (configurable)
- **AutoICPCrew**: Sources 100-10,000 leads based on plan tier

All crews are designed to:
- Scale horizontally
- Handle errors gracefully
- Log all actions for audit
- Sync to CRM in real-time

---

## 🎯 Summary

**All 18 agents work together through 3 specialized crews:**

1. **DeadLeadReactivationCrew** - Reactivates dormant leads when triggers fire
2. **FullCampaignCrew** - Executes complete campaigns from research to revenue
3. **AutoICPCrew** - Automatically sources new leads matching your ICP

**The OrchestrationService coordinates all crews** and provides a single entry point for the entire agent system.

**Result:** A fully automated, intelligent, compliant, and scalable lead reactivation system that works 24/7.






