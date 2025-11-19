"""
Agent 1: ResearcherAgent - Deep Lead Intelligence

Fetches LinkedIn profile data, company updates, job postings, and extracts actionable pain points.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from crewai import Agent
from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry, CircuitBreaker
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.validation import validate_lead_data
from ..utils.action_first_enforcer import ActionFirstEnforcer


class ResearcherAgent:
    """Deep lead intelligence using LinkedIn MCP."""
    
    def __init__(self, db: SupabaseDB, linkedin_tool: LinkedInMCPTool):
        self.db = db
        self.linkedin_tool = linkedin_tool
        self.communication_bus = get_communication_bus()
        # Circuit breaker for LinkedIn API calls
        self.linkedin_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        # Configure to use GPT-5.1 (default for research tasks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1", provider="openai")

        self.agent = Agent(
            role="Lead Intelligence Researcher",
            goal="Gather comprehensive intelligence on leads including LinkedIn data, company news, and pain points",
            backstory="""You are an expert researcher specializing in B2B lead intelligence.
            You gather data from LinkedIn, company websites, news sources, and social media
            to identify trigger events, pain points, and buying signals.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Deep intelligence researcher gathering lead data
- tone:        Analytical, thorough, detail-focused
- warmth:      medium
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert researcher specializing in B2B lead intelligence.
You gather data from LinkedIn, company websites, news sources, and social media
to identify trigger events, pain points, and buying signals.
Execute research immediately. Return results, not explanations.""")
            # TODO: Fix LinkedIn tool compatibility with CrewAI BaseTool
            # tools=[linkedin_tool]
        )
    
    @log_agent_execution(agent_name="ResearcherAgent")
    @retry(max_attempts=3, backoff="exponential", circuit_breaker=None)
    def research_lead(self, lead_id: str) -> Dict[str, Any]:
        """Research a lead and extract intelligence."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Validate lead data
        try:
            validated_lead = validate_lead_data(lead)
        except Exception as e:
            return {"error": f"Invalid lead data: {e}"}
        
        email = validated_lead.email
        company = validated_lead.company or ""
        
        # Get LinkedIn profile data (with circuit breaker)
        try:
            profile_data = self.linkedin_circuit_breaker.call(
                self.linkedin_tool.get_profile_data,
                email
            )
        except Exception as e:
            profile_data = {"error": str(e)}
        
        # Get company updates (with circuit breaker)
        try:
            company_updates = self.linkedin_circuit_breaker.call(
                self.linkedin_tool.get_company_updates,
                company
            ) if company else []
        except Exception as e:
            company_updates = []
        
        # Get job postings (pain point signals)
        try:
            job_postings = self.linkedin_circuit_breaker.call(
                self.linkedin_tool.get_job_postings,
                company
            ) if company else []
        except Exception as e:
            job_postings = []
        
        # Extract pain points
        pain_points = self._extract_pain_points(lead, profile_data, company_updates, job_postings)
        
        # Compile revival hooks
        revival_hooks = self._identify_revival_hooks(lead, profile_data, company_updates, job_postings)
        
        research_result = {
            "lead_id": lead_id,
            "current_role": profile_data.get("current_role"),
            "company_news": company_updates,
            "job_postings": job_postings,
            "pain_points": pain_points,
            "revival_hooks": revival_hooks,
            "best_channel": self._determine_best_channel(profile_data, company_updates)
        }
        
        # Broadcast research completion event
        self.communication_bus.broadcast(
            EventType.LEAD_RESEARCHED,
            "ResearcherAgent",
            research_result
        )
        
        # Update shared context
        self.communication_bus.update_lead_context(lead_id, {
            "research": research_result,
            "researched_at": datetime.utcnow().isoformat()
        })
        
        return research_result
    
    def _extract_pain_points(self, lead: Dict, profile_data: Dict, company_updates: List, job_postings: List) -> List[str]:
        """Extract pain points from research data."""
        pain_points = []
        
        # Hiring signals = scaling/onboarding pain
        if job_postings and len(job_postings) >= 5:
            pain_points.append("Scaling issues")
            pain_points.append("Team hiring")
        
        # Job changes = new responsibilities
        if profile_data.get("job_changes"):
            pain_points.append("New role responsibilities")
        
        return pain_points
    
    def _identify_revival_hooks(self, lead: Dict, profile_data: Dict, company_updates: List, job_postings: List) -> List[str]:
        """Identify revival hooks from research."""
        hooks = []
        
        if job_postings and len(job_postings) >= 5:
            hooks.append("New budget available")
            hooks.append("Expanding team")
        
        if profile_data.get("job_changes"):
            hooks.append("New decision-maker")
        
        return hooks
    
    def _determine_best_channel(self, profile_data: Dict, company_updates: List) -> str:
        """Determine best channel for outreach."""
        if profile_data.get("recent_posts"):
            return "LinkedIn + Email"
        return "Email"

