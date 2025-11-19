"""
Dead Lead Reactivation Crew

Specialized crew for dormant lead reactivation using the DeadLeadReactivationAgent
coordinated with other agents.
"""

from typing import Dict, List, Any
from crewai import Agent, Task, Crew
from ..tools.db_tools import SupabaseDB
from ..tools.linkedin_mcp_tools import LinkedInMCPTool
from ..agents.dead_lead_reactivation_agent import DeadLeadReactivationAgent
from ..agents.researcher_agents import ResearcherAgent
from ..agents.writer_agents import WriterAgent
from ..agents.content_agents import SubjectLineOptimizerAgent, FollowUpAgent
from ..agents.safety_agents import ComplianceAgent, QualityControlAgent, RateLimitAgent
from ..agents.sync_agents import TrackerAgent, SynchronizerAgent
from ..utils.agent_logging import log_agent_execution
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.monitoring import get_monitor


class DeadLeadReactivationCrew:
    """
    Specialized crew for dead lead reactivation.
    
    This crew coordinates:
    - DeadLeadReactivationAgent (monitors triggers)
    - ResearcherAgent (deep research)
    - WriterAgent (message generation)
    - SubjectLineOptimizerAgent (subject line optimization)
    - ComplianceAgent (compliance checks)
    - QualityControlAgent (quality checks)
    - RateLimitAgent (rate limiting)
    - TrackerAgent (tracking)
    - SynchronizerAgent (CRM sync)
    """
    
    def __init__(self):
        self.db = SupabaseDB()
        self.linkedin_tool = LinkedInMCPTool()
        self.communication_bus = get_communication_bus()
        self.monitor = get_monitor()
        
        # Initialize all agents
        self.dead_reactivation_agent = DeadLeadReactivationAgent(self.db, self.linkedin_tool)
        self.researcher = ResearcherAgent(self.db, self.linkedin_tool)
        self.writer = WriterAgent(self.db)
        self.subject_optimizer = SubjectLineOptimizerAgent(self.db)
        self.compliance = ComplianceAgent(self.db)
        self.quality = QualityControlAgent(self.db)
        self.rate_limiter = RateLimitAgent(self.db)
        self.tracker = TrackerAgent(self.db)
        self.synchronizer = SynchronizerAgent(self.db)
    
    @log_agent_execution(agent_name="DeadLeadReactivationCrew")
    def reactivate_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Full reactivation workflow for a single lead.
        
        Workflow:
        1. DeadLeadReactivationAgent monitors for triggers
        2. ResearcherAgent does deep research if trigger found
        3. WriterAgent generates personalized message
        4. SubjectLineOptimizerAgent optimizes subject line
        5. ComplianceAgent checks compliance
        6. QualityControlAgent checks quality
        7. RateLimitAgent checks rate limits
        8. If all pass, message is sent
        9. TrackerAgent tracks delivery
        10. SynchronizerAgent syncs to CRM
        """
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        user_id = lead.get("user_id")
        domain = lead.get("email", "").split("@")[1] if "@" in lead.get("email", "") else ""
        
        # Step 1: Monitor for trigger events
        trigger_events = self.dead_reactivation_agent.monitor_trigger_events(lead_id)
        
        if not trigger_events:
            return {
                "lead_id": lead_id,
                "status": "no_triggers",
                "message": "No trigger events detected. Lead remains dormant."
            }
        
        # Get best trigger
        best_trigger = max(trigger_events, key=lambda x: x.get("relevance_score", 0))
        
        # Step 2: Deep research
        research_result = self.researcher.research_lead(lead_id)
        
        # Step 3: Generate message
        message_result = self.dead_reactivation_agent.craft_trigger_specific_message(lead_id, best_trigger)
        
        # Step 4: Optimize subject line
        subject_variants = self.subject_optimizer.generate_variants(lead, research_result)
        best_subject = subject_variants["variants"][0]["subject"]  # Use first variant
        
        # Step 5: Compliance check
        compliance_result = self.compliance.check_compliance(lead_id, message_result)
        
        if not compliance_result["compliant"]:
            return {
                "lead_id": lead_id,
                "status": "blocked",
                "reason": "compliance_failure",
                "details": compliance_result
            }
        
        # Step 6: Quality check
        quality_result = self.quality.check_quality(lead_id, message_result)
        
        if not quality_result["approved"]:
            return {
                "lead_id": lead_id,
                "status": "blocked",
                "reason": "quality_failure",
                "details": quality_result
            }
        
        # Step 7: Rate limit check
        rate_limit_result = self.rate_limiter.check_rate_limit(user_id, domain)
        
        if not rate_limit_result["can_send"]:
            return {
                "lead_id": lead_id,
                "status": "blocked",
                "reason": "rate_limit_exceeded",
                "details": rate_limit_result
            }
        
        # Step 8: All checks passed - queue for sending
        queue_result = self.dead_reactivation_agent.queue_lead_for_campaign(lead_id, best_trigger)
        
        # Step 9: Track (would happen after sending)
        # Step 10: Sync to CRM (would happen after sending)
        
        return {
            "lead_id": lead_id,
            "status": "queued_for_sending",
            "trigger_event": best_trigger,
            "message": message_result,
            "subject": best_subject,
            "compliance": compliance_result,
            "quality": quality_result,
            "rate_limit": rate_limit_result,
            "queued": queue_result
        }
    
    @log_agent_execution(agent_name="DeadLeadReactivationCrew")
    def monitor_and_reactivate_batch(self, user_id: str, batch_size: int = 50) -> Dict[str, Any]:
        """Monitor all dormant leads and reactivate those with triggers."""
        results = {
            "leads_checked": 0,
            "triggers_detected": 0,
            "leads_queued": 0,
            "leads_blocked": 0,
            "errors": []
        }
        
        # Get dormant leads
        dormant_leads = self.db.get_dormant_leads(user_id, limit=batch_size)
        
        for lead in dormant_leads:
            try:
                results["leads_checked"] += 1
                lead_id = lead["id"]
                
                # Run full reactivation workflow
                reactivation_result = self.reactivate_lead(lead_id)
                
                if reactivation_result.get("status") == "queued_for_sending":
                    results["leads_queued"] += 1
                    results["triggers_detected"] += 1
                elif reactivation_result.get("status") == "blocked":
                    results["leads_blocked"] += 1
                elif reactivation_result.get("status") == "no_triggers":
                    pass  # No action needed
                
            except Exception as e:
                results["errors"].append({
                    "lead_id": lead.get("id"),
                    "error": str(e)
                })
        
        return results

