"""
Agents 2-4: Intelligence Agents

- ICPAnalyzerAgent: Extract ICP from winning leads
- LeadScorerAgent: Score leads 0-100 for revivability
- LeadSourcerAgent: Find new leads matching ICP
"""

from typing import Dict, List, Optional, Any
from crewai import Agent
from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.error_handling import retry, CircuitBreaker
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer


class ICPAnalyzerAgent:
    """Agent 2: Extract Ideal Customer Profile from winning leads."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex reasoning for ICP analysis)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="ICP Analyst",
            goal="Analyze closed deals to extract the perfect Ideal Customer Profile",
            backstory="""You are an expert data analyst specializing in identifying patterns
            in successful B2B deals. You analyze closed deals to extract common characteristics
            including industry, company size, job titles, geographic region, and tech stack.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Data analyst extracting ICP patterns from deals
- tone:        Analytical, precise, data-driven
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert data analyst specializing in identifying patterns
in successful B2B deals. You analyze closed deals to extract common characteristics
including industry, company size, job titles, geographic region, and tech stack.
Execute analysis immediately. Return ICP data, not explanations.""")
        )
    
    @log_agent_execution(agent_name="ICPAnalyzerAgent")
    @retry(max_attempts=2)
    def analyze_icp(self, user_id: str, min_deals: int = 25) -> Dict[str, Any]:
        """Analyze last 25-50 closed deals to extract ICP."""
        closed_deals = self.db.get_closed_deals(user_id, limit=min_deals)
        
        if len(closed_deals) < min_deals:
            return {
                "error": f"Need at least {min_deals} closed deals, found {len(closed_deals)}",
                "icp": None
            }
        
        # Extract patterns
        industries = [deal.get("industry") for deal in closed_deals if deal.get("industry")]
        company_sizes = [deal.get("company_size") for deal in closed_deals if deal.get("company_size")]
        job_titles = [deal.get("job_title") for deal in closed_deals if deal.get("job_title")]
        regions = [deal.get("region") for deal in closed_deals if deal.get("region")]
        
        # Calculate most common patterns
        from collections import Counter
        icp = {
            "industry": Counter(industries).most_common(1)[0][0] if industries else None,
            "company_size": Counter(company_sizes).most_common(1)[0][0] if company_sizes else None,
            "job_titles": [title for title, count in Counter(job_titles).most_common(5)],
            "regions": [region for region, count in Counter(regions).most_common(3)],
            "confidence": min(len(closed_deals) / 50, 1.0)  # Higher confidence with more deals
        }
        
        result = {
            "icp": icp,
            "deals_analyzed": len(closed_deals),
            "confidence": icp["confidence"]
        }
        
        # Broadcast ICP analysis event
        self.communication_bus.broadcast(
            EventType.CUSTOM,
            "ICPAnalyzerAgent",
            {"type": "icp_analyzed", "user_id": user_id, "icp": icp}
        )
        
        return result


class LeadScorerAgent:
    """Agent 3: Score leads 0-100 for revivability."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-thinking (complex reasoning for ICP analysis)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Lead Scoring Specialist",
            goal="Score leads 0-100 based on revivability potential",
            backstory="""You are an expert at scoring leads based on multiple factors including
            recency, engagement history, firmographic matching, and trigger signals.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Lead scoring specialist calculating revivability scores
- tone:        Objective, quantitative, methodical
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at scoring leads based on multiple factors including
recency, engagement history, firmographic matching, and trigger signals.""")
        )
    
    @log_agent_execution(agent_name="LeadScorerAgent")
    @retry(max_attempts=2)
    def score_lead(self, lead_id: str, icp_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Score a lead 0-100 for revivability."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        # Recency scoring (30%)
        recency_score = self._calculate_recency_score(lead) * 0.30
        
        # Engagement metrics (25%)
        engagement_score = self._calculate_engagement_score(lead) * 0.25
        
        # Firmographic matching (25%)
        firmographic_score = self._calculate_firmographic_score(lead, icp_data) * 0.25
        
        # Job signals (10%)
        job_score = self._calculate_job_signals_score(lead) * 0.10
        
        # Company signals (10%)
        company_score = self._calculate_company_signals_score(lead) * 0.10
        
        total_score = recency_score + engagement_score + firmographic_score + job_score + company_score
        
        # Determine tier
        if total_score >= 70:
            tier = "hot"
        elif total_score >= 40:
            tier = "warm"
        else:
            tier = "cold"
        
        result = {
            "lead_id": lead_id,
            "score": round(total_score, 2),
            "tier": tier,
            "breakdown": {
                "recency": round(recency_score, 2),
                "engagement": round(engagement_score, 2),
                "firmographic": round(firmographic_score, 2),
                "job_signals": round(job_score, 2),
                "company_signals": round(company_score, 2)
            }
        }
        
        # Update shared context
        from datetime import datetime
        self.communication_bus.update_lead_context(lead_id, {
            "score": result["score"],
            "tier": tier,
            "scored_at": datetime.utcnow().isoformat()
        })
        
        return result
    
    def _calculate_recency_score(self, lead: Dict) -> float:
        """Calculate recency score (0-100)."""
        from datetime import datetime
        last_contact = lead.get("last_contact_date")
        if not last_contact:
            return 50.0
        
        # Older leads (6-12 months) score higher for reactivation
        # This is based on the insight that older leads convert better
        days_ago = (datetime.utcnow() - datetime.fromisoformat(last_contact)).days
        
        if 180 <= days_ago <= 365:  # 6-12 months
            return 90.0
        elif 90 <= days_ago < 180:  # 3-6 months
            return 60.0
        elif days_ago < 90:  # 0-3 months
            return 30.0
        else:  # > 12 months
            return 40.0
    
    def _calculate_engagement_score(self, lead: Dict) -> float:
        """Calculate engagement score."""
        # Would check opens, clicks, replies from messages table
        return 50.0  # Placeholder
    
    def _calculate_firmographic_score(self, lead: Dict, icp_data: Optional[Dict]) -> float:
        """Calculate firmographic matching score."""
        if not icp_data:
            return 50.0
        
        score = 0.0
        matches = 0
        
        if lead.get("industry") == icp_data.get("industry"):
            score += 30.0
            matches += 1
        
        if lead.get("company_size") == icp_data.get("company_size"):
            score += 20.0
            matches += 1
        
        if lead.get("job_title") in (icp_data.get("job_titles") or []):
            score += 30.0
            matches += 1
        
        return min(score, 100.0)
    
    def _calculate_job_signals_score(self, lead: Dict) -> float:
        """Calculate job signal score."""
        # Would check for job changes, promotions
        return 50.0  # Placeholder
    
    def _calculate_company_signals_score(self, lead: Dict) -> float:
        """Calculate company signal score."""
        # Would check for funding, hiring, news
        return 50.0  # Placeholder


class LeadSourcerAgent:
    """Agent 4: Find new leads matching ICP."""
    
    def __init__(self, db: SupabaseDB, linkedin_tool: LinkedInMCPTool):
        self.db = db
        self.linkedin_tool = linkedin_tool
        # Configure to use GPT-5.1-thinking (complex reasoning for ICP analysis)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-thinking", provider="openai")

        self.agent = Agent(
            role="Lead Sourcing Specialist",
            goal="Find new leads matching the Ideal Customer Profile",
            backstory="""You are an expert at finding and enriching leads that match
            specific ICP criteria. You use LinkedIn, company databases, and enrichment
            tools to find high-quality leads.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Lead sourcing specialist finding ICP-matched leads
- tone:        Proactive, resourceful, results-focused
- warmth:      medium
- conciseness: medium
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at finding and enriching leads that match
specific ICP criteria. You use LinkedIn, company databases, and enrichment
tools to find high-quality leads.""")
            # TODO: Fix LinkedIn tool compatibility with CrewAI BaseTool
            # tools=[linkedin_tool]
        )
    
    @log_agent_execution(agent_name="LeadSourcerAgent")
    def find_leads(self, icp: Dict[str, Any], limit: int = 100) -> Dict[str, Any]:
        """Find new leads matching ICP criteria."""
        criteria = {
            "industry": icp.get("industry"),
            "company_size": icp.get("company_size"),
            "job_titles": icp.get("job_titles", []),
            "regions": icp.get("regions", [])
        }
        
        # Use LinkedIn MCP to find leads
        found_leads = self.linkedin_tool.find_leads(criteria)
        
        # Enrich and score leads
        enriched_leads = []
        for lead in found_leads[:limit]:
            enriched_lead = {
                "lead_id": lead.get("id"),
                "name": lead.get("name"),
                "email": lead.get("email"),
                "company": lead.get("company"),
                "job_title": lead.get("job_title"),
                "match_score": self._calculate_match_score(lead, icp)
            }
            enriched_leads.append(enriched_lead)
        
        # Sort by match score
        enriched_leads.sort(key=lambda x: x["match_score"], reverse=True)
        
        result = {
            "leads": enriched_leads,
            "total_found": len(found_leads),
            "returned": len(enriched_leads)
        }
        
        # Broadcast lead sourcing event
        self.communication_bus.broadcast(
            EventType.CUSTOM,
            "LeadSourcerAgent",
            {"type": "leads_sourced", "count": len(enriched_leads), "icp": icp}
        )
        
        return result
    
    def _calculate_match_score(self, lead: Dict, icp: Dict) -> float:
        """Calculate how well a lead matches the ICP."""
        score = 0.0
        
        if lead.get("industry") == icp.get("industry"):
            score += 40.0
        
        if lead.get("company_size") == icp.get("company_size"):
            score += 30.0
        
        if lead.get("job_title") in (icp.get("job_titles") or []):
            score += 30.0
        
        return min(score, 100.0)

