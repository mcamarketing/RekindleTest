"""
Orchestration Service

Main service that coordinates all crews and agents.
This is the entry point for the entire agent system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .crews.dead_lead_reactivation_crew import DeadLeadReactivationCrew
from .crews.full_campaign_crew import FullCampaignCrew
from .crews.auto_icp_crew import AutoICPCrew
from .tools.db_tools import SupabaseDB
from .utils.agent_logging import log_agent_execution
from .utils.monitoring import get_monitor
from .utils.agent_communication import get_communication_bus
from .agents.master_intelligence_agent import MasterIntelligenceAgent
import logging

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    Main orchestration service that coordinates all crews.
    
    This service:
    - Runs dead lead reactivation crew 24/7
    - Orchestrates full campaigns
    - Handles replies and meetings
    - Manages Auto-ICP sourcing
    - Coordinates all 18 agents through crews
    """
    
    def __init__(self):
        self.db = SupabaseDB()
        self.monitor = get_monitor()
        self.communication_bus = get_communication_bus()
        
        # Master Intelligence Agent - The Director
        self.master_intelligence = MasterIntelligenceAgent(self.db)
        
        self.dead_reactivation_crew = DeadLeadReactivationCrew()
        self.full_campaign_crew = FullCampaignCrew()
        self.auto_icp_crew = AutoICPCrew()
    
    @log_agent_execution(agent_name="OrchestrationService")
    def run_dead_lead_reactivation(self, user_id: str, batch_size: int = 50) -> Dict[str, Any]:
        """
        Run dead lead reactivation for a user.
        
        Uses DeadLeadReactivationCrew which coordinates:
        - DeadLeadReactivationAgent (monitors triggers)
        - ResearcherAgent (research)
        - WriterAgent (message generation)
        - SubjectLineOptimizerAgent (subject optimization)
        - ComplianceAgent (compliance)
        - QualityControlAgent (quality)
        - RateLimitAgent (rate limiting)
        - TrackerAgent (tracking)
        - SynchronizerAgent (CRM sync)
        """
        return self.dead_reactivation_crew.monitor_and_reactivate_batch(user_id, batch_size)
    
    @log_agent_execution(agent_name="OrchestrationService")
    def run_full_campaign(self, user_id: str, lead_ids: List[str]) -> Dict[str, Any]:
        """
        Run full campaign for multiple leads.
        
        Uses FullCampaignCrew which coordinates all 18 agents:
        - Research → Scoring → Writing → Optimization
        - Safety checks (Compliance, Quality, Rate Limit)
        - Sending → Tracking → Engagement Analysis
        - Reply handling → Meeting booking → Billing
        """
        results = {
            "leads_processed": 0,
            "campaigns_started": 0,
            "errors": []
        }
        
        for lead_id in lead_ids:
            try:
                campaign_result = self.full_campaign_crew.run_campaign_for_lead(lead_id)
                results["leads_processed"] += 1
                
                if campaign_result.get("status") == "campaign_started":
                    results["campaigns_started"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "lead_id": lead_id,
                    "error": str(e)
                })
        
        return results
    
    @log_agent_execution(agent_name="OrchestrationService")
    def handle_inbound_reply(self, lead_id: str, reply_text: str) -> Dict[str, Any]:
        """
        Handle an inbound reply.
        
        Uses FullCampaignCrew which coordinates:
        - TrackerAgent (classify reply)
        - MeetingBookerAgent (if meeting request)
        - ObjectionHandlerAgent (if objection)
        - FollowUpAgent (if question)
        - BillingAgent (if meeting booked)
        - SynchronizerAgent (sync to CRM)
        """
        return self.full_campaign_crew.handle_reply(lead_id, reply_text)
    
    @log_agent_execution(agent_name="OrchestrationService")
    def run_auto_icp_sourcing(self, user_id: str, min_deals: int = 25, lead_limit: int = 100) -> Dict[str, Any]:
        """
        Run Auto-ICP analysis and lead sourcing.
        
        Uses AutoICPCrew which coordinates:
        - ICPAnalyzerAgent (extract ICP)
        - LeadSourcerAgent (find leads)
        - ResearcherAgent (research leads)
        - LeadScorerAgent (score leads)
        """
        return self.auto_icp_crew.analyze_and_source_leads(user_id, min_deals, lead_limit)
    
    @log_agent_execution(agent_name="OrchestrationService")
    def run_daily_workflow(self, user_id: str) -> Dict[str, Any]:
        """
        Run complete daily workflow for a user.
        
        This coordinates all crews:
        1. Dead lead reactivation (monitor dormant leads)
        2. Auto-ICP sourcing (if 25+ closed deals)
        3. Campaign execution (for queued leads)
        4. Engagement analysis (optimize campaigns)
        """
        daily_results = {
            "dead_lead_reactivation": None,
            "auto_icp_sourcing": None,
            "campaign_execution": None,
            "engagement_analysis": None
        }
        
        # Step 1: Dead lead reactivation
        reactivation_result = self.run_dead_lead_reactivation(user_id, batch_size=50)
        daily_results["dead_lead_reactivation"] = reactivation_result
        
        # Step 2: Auto-ICP sourcing (if user has 25+ closed deals)
        # Check if user qualifies
        closed_deals = self.db.get_closed_deals(user_id, limit=25)
        if len(closed_deals) >= 25:
            icp_result = self.run_auto_icp_sourcing(user_id)
            daily_results["auto_icp_sourcing"] = icp_result
        
        # Step 3: Campaign execution (for queued leads)
        # Get queued leads
        queued_leads = []  # Would query leads table for status="queued_for_campaign"
        if queued_leads:
            lead_ids = [lead["id"] for lead in queued_leads]
            campaign_result = self.run_full_campaign(user_id, lead_ids)
            daily_results["campaign_execution"] = campaign_result
        
        # Step 4: Engagement analysis
        engagement_result = self.full_campaign_crew.analyze_and_optimize(user_id)
        daily_results["engagement_analysis"] = engagement_result
        
        return daily_results
    
    @log_agent_execution(agent_name="OrchestrationService")
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        return self.monitor.get_health_status()
    
    @log_agent_execution(agent_name="OrchestrationService")
    def get_agent_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for agents."""
        if agent_name:
            return self.monitor.get_agent_stats(agent_name)
        return {
            "all_agents": {
                name: self.monitor.get_agent_stats(name)
                for name in ["ResearcherAgent", "WriterAgent", "ComplianceAgent", 
                            "QualityControlAgent", "RateLimitAgent", "DeadLeadReactivationAgent"]
            }
        }
    
    @log_agent_execution(agent_name="OrchestrationService")
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        alerts = self.monitor.get_recent_alerts(limit=limit)
        return [{
            "level": alert.level.value,
            "agent_name": alert.agent_name,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "metadata": alert.metadata
        } for alert in alerts]
    
    @log_agent_execution(agent_name="OrchestrationService")
    def get_master_intelligence(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Get aggregated intelligence from Master Intelligence Agent."""
        return self.master_intelligence.aggregate_cross_client_intelligence(time_period_days)
    
    @log_agent_execution(agent_name="OrchestrationService")
    def get_optimization_plan(self) -> Dict[str, Any]:
        """Get system-wide optimization plan from Master Intelligence."""
        return self.master_intelligence.get_system_optimization_plan()
    
    @log_agent_execution(agent_name="OrchestrationService")
    def learn_from_campaign_outcome(
        self,
        category: str,
        content: str,
        performance_metrics: Dict[str, float],
        context: Dict[str, Any],
        success: bool
    ):
        """Learn from a campaign outcome and store in RAG."""
        self.master_intelligence.learn_from_outcome(
            category=category,
            content=content,
            performance_metrics=performance_metrics,
            context=context,
            success=success
        )

