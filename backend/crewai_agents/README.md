# Rekindle CrewAI Agents System

## 🎯 Overview

Rekindle uses **18 specialized AI agents** working together in **3 crews** to automate dead lead reactivation, campaign execution, and lead sourcing.

---

## 🚀 Quick Start

### Installation

```bash
cd backend/crewai_agents
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
ANTHROPIC_API_KEY=your_anthropic_api_key
REDIS_URL=your_redis_url  # Optional, for caching
```

### Run a Crew

```bash
# Run dead lead reactivation
python -m backend.crewai_agents dead-lead-reactivation <user_id>

# Run full campaign
python -m backend.crewai_agents full-campaign <user_id> <lead_id1> <lead_id2>

# Handle inbound reply
python -m backend.crewai_agents handle-reply <lead_id> "I'm interested"

# Run Auto-ICP sourcing
python -m backend.crewai_agents auto-icp <user_id>

# Run complete daily workflow
python -m backend.crewai_agents daily-workflow <user_id>
```

---

## 📚 Documentation

- **[AGENTS_OVERVIEW.md](./AGENTS_OVERVIEW.md)** - Detailed overview of all 18 agents
- **[CREWS_ARCHITECTURE.md](./CREWS_ARCHITECTURE.md)** - How crews coordinate agents

---

## 🏗️ Architecture

```
OrchestrationService
├── DeadLeadReactivationCrew (9 agents)
│   ├── DeadLeadReactivationAgent
│   ├── ResearcherAgent
│   ├── WriterAgent
│   ├── SubjectLineOptimizerAgent
│   ├── ComplianceAgent
│   ├── QualityControlAgent
│   ├── RateLimitAgent
│   ├── TrackerAgent
│   └── SynchronizerAgent
│
├── FullCampaignCrew (18 agents)
│   ├── All intelligence agents
│   ├── All content agents
│   ├── All safety agents
│   ├── All sync agents
│   ├── All revenue agents
│   └── Specialized agents
│
└── AutoICPCrew (4 agents)
    ├── ICPAnalyzerAgent
    ├── LeadSourcerAgent
    ├── ResearcherAgent
    └── LeadScorerAgent
```

---

## 🔧 Development

### Project Structure

```
backend/crewai_agents/
├── agents/              # All 18 agent implementations
│   ├── researcher_agents.py
│   ├── intelligence_agents.py
│   ├── writer_agents.py
│   ├── content_agents.py
│   ├── dead_lead_reactivation_agent.py
│   ├── sync_agents.py
│   ├── revenue_agents.py
│   ├── safety_agents.py
│   └── launch_agents.py
├── crews/               # Crew implementations
│   ├── dead_lead_reactivation_crew.py
│   ├── full_campaign_crew.py
│   └── auto_icp_crew.py
├── tools/               # Shared tools
│   ├── db_tools.py
│   └── linkedin_mcp_tools.py
├── utils/               # Utilities
│   └── agent_logging.py
├── orchestration_service.py  # Main orchestration
├── main.py              # CLI entry point
└── requirements.txt     # Python dependencies
```

### Adding a New Agent

1. Create agent class in appropriate file (e.g., `agents/content_agents.py`)
2. Implement required methods
3. Add to relevant crew(s) in `crews/`
4. Update `AGENTS_OVERVIEW.md`

### Adding a New Crew

1. Create crew class in `crews/`
2. Initialize required agents
3. Implement workflow methods
4. Add to `OrchestrationService`
5. Update `CREWS_ARCHITECTURE.md`

---

## 🧪 Testing

```bash
# Run all tests (when implemented)
pytest tests/

# Run specific crew test
pytest tests/test_dead_lead_reactivation_crew.py
```

---

## 📊 Monitoring

All agent actions are logged via `agent_logging.py`:

- Execution duration
- Success/failure status
- Input/output data (sanitized)
- Errors and exceptions

Logs are stored in Supabase `agent_logs` table for audit and debugging.

---

## 🔐 Security

- All agents use service role key for database access
- Sensitive data is sanitized in logs
- Rate limiting prevents abuse
- Compliance checks ensure GDPR/CAN-SPAM compliance

---

## 📈 Performance

- **DeadLeadReactivationCrew**: 50 leads/batch
- **FullCampaignCrew**: Parallel processing (configurable)
- **AutoICPCrew**: 100-10,000 leads based on plan

---

## 🆘 Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
2. **Database connection**: Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
3. **API errors**: Check `ANTHROPIC_API_KEY` is valid
4. **Rate limiting**: Check Redis connection if using caching

### Debug Mode

Set `VERBOSE=True` in environment to see detailed agent execution logs.

---

## 📝 License

Proprietary - Rekindle.ai






