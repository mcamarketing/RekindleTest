"""
Agent 15: OrchestratorAgent - Manage Full Workflow

Coordinates all agents to execute complete campaigns.
"""

from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew
from ..tools.db_tools import SupabaseDB
from .researcher_agents import ResearcherAgent
from .writer_agents import WriterAgent
from .dead_lead_reactivation_agent import DeadLeadReactivationAgent
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer


class OrchestratorAgent:
    """Agent 15: Manage full campaign workflow."""
    
    def __init__(self, db: SupabaseDB, researcher_agent: ResearcherAgent, writer_agent: WriterAgent):
        self.db = db
        self.researcher_agent = researcher_agent
        self.writer_agent = writer_agent
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex orchestration)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Campaign Orchestrator",
            goal="Coordinate all agents to execute complete lead reactivation campaigns",
            backstory="""You are the master coordinator of all agents. You ensure research happens first,
            then message generation, then safety checks (compliance, quality, rate limiting), and finally
            message sending. You handle errors, retries, and campaign state management.""",
            verbose=True,
            allow_delegation=True,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Campaign orchestrator coordinating all agents
- tone:        Organized, methodical, execution-focused
- warmth:      low
- conciseness: high
- energy:      neutral
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are the master coordinator of all agents. You ensure research happens first,
then message generation, then safety checks (compliance, quality, rate limiting), and finally
message sending. You handle errors, retries, and campaign state management.""")
        )
    
    @log_agent_execution(agent_name="OrchestratorAgent")
    @retry(max_attempts=2)
    def orchestrate_campaign(self, user_id: str, lead_ids: List[str]) -> Dict[str, Any]:
        """Orchestrate a full campaign for multiple leads."""
        results = {
            "leads_processed": 0,
            "messages_generated": 0,
            "errors": []
        }
        
        for lead_id in lead_ids:
            try:
                # Step 1: Research
                research_result = self.researcher_agent.research_lead(lead_id)
                
                # Step 2: Generate messages
                sequence_result = self.writer_agent.generate_sequence(
                    lead_id,
                    research_result
                )
                
                results["leads_processed"] += 1
                results["messages_generated"] += len(sequence_result.get("sequence", []))
                
            except Exception as e:
                results["errors"].append({
                    "lead_id": lead_id,
                    "error": str(e)
                })
        
        return results
    
    @log_agent_execution(agent_name="OrchestratorAgent")
    @retry(max_attempts=2)
    def orchestrate_dead_lead_reactivation(self, user_id: str) -> Dict[str, Any]:
        """Orchestrate dead lead reactivation using the specialized agent."""
        dead_reactivation_agent = DeadLeadReactivationAgent(
            self.db,
            self.researcher_agent.linkedin_tool
        )
        
        # Monitor all dormant leads
        result = dead_reactivation_agent.monitor_all_dormant_leads(user_id)
        
        return result

