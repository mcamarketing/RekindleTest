"""
Auto-ICP Crew

Crew for automatic ICP analysis and lead sourcing.
Coordinates ICPAnalyzerAgent, LeadSourcerAgent, and ResearcherAgent.
"""

from typing import Dict, List, Any
from crewai import Agent, Task, Crew
from ..tools.db_tools import SupabaseDB
from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..agents.intelligence_agents import ICPAnalyzerAgent, LeadSourcerAgent
from ..agents.researcher_agents import ResearcherAgent
from ..agents.intelligence_agents import LeadScorerAgent
from ..utils.agent_logging import log_agent_execution


class AutoICPCrew:
    """
    Crew for automatic ICP analysis and lead sourcing.
    
    Workflow:
    1. ICPAnalyzerAgent analyzes closed deals to extract ICP
    2. LeadSourcerAgent finds new leads matching ICP
    3. ResearcherAgent researches new leads
    4. LeadScorerAgent scores new leads
    5. High-scoring leads are queued for campaigns
    """
    
    def __init__(self):
        self.db = SupabaseDB()
        self.linkedin_tool = LinkedInMCPTool()
        
        # Initialize agents
        self.icp_analyzer = ICPAnalyzerAgent(self.db)
        self.lead_sourcer = LeadSourcerAgent(self.db, self.linkedin_tool)
        self.researcher = ResearcherAgent(self.db, self.linkedin_tool)
        self.lead_scorer = LeadScorerAgent(self.db)
    
    @log_agent_execution(agent_name="AutoICPCrew")
    def analyze_and_source_leads(self, user_id: str, min_deals: int = 25, lead_limit: int = 100) -> Dict[str, Any]:
        """
        Complete Auto-ICP workflow.
        
        1. Analyze ICP from closed deals
        2. Source new leads matching ICP
        3. Research and score new leads
        4. Queue high-scoring leads
        """
        # Step 1: Analyze ICP
        icp_result = self.icp_analyzer.analyze_icp(user_id, min_deals)
        
        if icp_result.get("error"):
            return icp_result
        
        icp = icp_result["icp"]
        
        # Step 2: Source new leads
        sourcing_result = self.lead_sourcer.find_leads(icp, limit=lead_limit)
        
        if not sourcing_result.get("leads"):
            return {
                "status": "no_leads_found",
                "icp": icp,
                "sourcing": sourcing_result
            }
        
        # Step 3: Research and score each lead
        processed_leads = []
        for lead_data in sourcing_result["leads"]:
            lead_id = lead_data.get("lead_id")
            
            # Research
            research_result = self.researcher.research_lead(lead_id)
            
            # Score
            scoring_result = self.lead_scorer.score_lead(lead_id, icp)
            
            processed_leads.append({
                "lead_id": lead_id,
                "match_score": lead_data.get("match_score"),
                "revivability_score": scoring_result.get("score"),
                "tier": scoring_result.get("tier"),
                "research": research_result
            })
        
        # Sort by revivability score
        processed_leads.sort(key=lambda x: x["revivability_score"], reverse=True)
        
        # Queue high-scoring leads (score >= 70)
        high_scoring_leads = [l for l in processed_leads if l["revivability_score"] >= 70]
        
        for lead in high_scoring_leads:
            self.db.update_lead(lead["lead_id"], {
                "status": "queued_for_campaign",
                "source": "auto_icp",
                "queued_at": __import__("datetime").datetime.utcnow().isoformat()
            })
        
        return {
            "status": "success",
            "icp": icp,
            "icp_confidence": icp_result.get("confidence"),
            "leads_found": len(sourcing_result["leads"]),
            "leads_processed": len(processed_leads),
            "high_scoring_leads": len(high_scoring_leads),
            "queued_leads": high_scoring_leads
        }






