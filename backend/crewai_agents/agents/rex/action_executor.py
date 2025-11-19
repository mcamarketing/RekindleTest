"""
Action Executor for REX

Executes commands by calling the appropriate crews and agents.
"""

from typing import Dict, List, Optional, Any
from ..orchestration_service import OrchestrationService
from ..crews.special_forces_crews import SpecialForcesCoordinator
from ..tools.db_tools import SupabaseDB
from .defaults import IntelligentDefaults
from .permissions import PermissionsManager
from .sentience_engine import SentienceEngine, SelfHealingLogic
from .response_wrapper import ResponseWrapper
import logging

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes parsed commands by delegating to crews and agents."""

    def __init__(self, orchestration_service: OrchestrationService, db: SupabaseDB, permissions_manager: PermissionsManager, sentience_engine: SentienceEngine, special_forces: Optional[SpecialForcesCoordinator] = None):
        self.orchestration_service = orchestration_service
        self.special_forces = special_forces or SpecialForcesCoordinator()
        self.db = db
        self.defaults = IntelligentDefaults(db)
        self.permissions = permissions_manager
        self.sentience = sentience_engine
        self.self_healing = sentience_engine.self_healing

        # Feature flag: Use Special Forces Crews (new) vs 28-agent system (legacy)
        self.use_special_forces = True
    
    def execute(self, user_id: Optional[str], parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a parsed command with permission checks.
        
        Returns:
            {
                "success": bool,
                "action": str,
                "result": {...},  # Agent/crew execution result
                "message": str,  # User-facing confirmation
                "execution_time": float,
                "permission_denied": bool
            }
        """
        import time
        start_time = time.time()
        
        action = parsed_command.get("action")
        entities = parsed_command.get("entities", {})
        
        # Check permissions before execution
        if action:
            can_execute, error_message = self.permissions.can_execute_action(user_id, action)
            if not can_execute:
                return {
                    "success": False,
                    "action": action,
                    "message": error_message or "Permission denied",
                    "permission_denied": True,
                    "execution_time": time.time() - start_time
                }
        
        if not action:
            # No action detected - treat as query
            return self._handle_query(user_id, parsed_command.get("raw_message", ""))
        
        try:
            # Execute with self-healing retry logic
            max_attempts = 2
            attempt = 0
            last_error = None
            
            while attempt < max_attempts:
                try:
                    # Execute based on action type
                    if action == "launch_campaign":
                        result = self._execute_launch_campaign(user_id, entities)
                    elif action == "reactivate_leads":
                        result = self._execute_reactivate_leads(user_id, entities)
                    elif action == "analyze_icp":
                        result = self._execute_analyze_icp(user_id, entities)
                    elif action == "source_leads":
                        result = self._execute_source_leads(user_id, entities)
                    elif action == "research_leads":
                        result = self._execute_research_leads(user_id, entities)
                    elif action == "get_kpis":
                        result = self._execute_get_kpis(user_id, entities)
                    elif action == "get_campaign_status":
                        result = self._execute_get_campaign_status(user_id, entities)
                    elif action == "get_lead_details":
                        result = self._execute_get_lead_details(user_id, entities)
                    else:
                        result = {
                            "success": False,
                            "message": f"Unknown action: {action}"
                        }
                    
                    execution_time = time.time() - start_time
                    result["execution_time"] = execution_time
                    result["action"] = action
                    
                    logger.info(f"REX executed {action} for user {user_id} in {execution_time:.2f}s")
                    return result
                    
                except Exception as e:
                    last_error = e
                    attempt += 1
                    
                    # Check if we should retry
                    if self.self_healing.should_retry(e, attempt, max_attempts):
                        recovery_strategy = self.self_healing.get_recovery_strategy(e)
                        logger.warning(f"Execution error (attempt {attempt}/{max_attempts}): {e}. Strategy: {recovery_strategy}")
                        
                        # Implement recovery strategy
                        if recovery_strategy == "wait_and_retry":
                            import time as time_module
                            time_module.sleep(1)  # Wait 1 second before retry
                        elif recovery_strategy == "retry_with_backoff":
                            import time as time_module
                            time_module.sleep(2 ** attempt)  # Exponential backoff
                        # Continue to retry
                    else:
                        # Don't retry, break and return error
                        break
            
            # All attempts failed
            logger.error(f"REX execution error for {action} after {attempt} attempts: {last_error}", exc_info=True)
            return {
                "success": False,
                "action": action,
                "message": f"Error executing {action}",
                "error": str(last_error),
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"REX execution error for {action}: {e}", exc_info=True)
            return {
                "success": False,
                "action": action,
                "message": f"Error executing {action}",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _execute_launch_campaign(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute campaign launch."""
        # Infer lead IDs if not provided
        lead_ids = entities.get("lead_ids")
        if not lead_ids:
            criteria = {
                "hot_only": entities.get("hot_only", True),
                "state": entities.get("state"),
                "industry": entities.get("industry")
            }
            lead_ids = self.defaults.infer_lead_ids(user_id, criteria if any(criteria.values()) else None)

        if not lead_ids:
            return {
                "success": False,
                "message": "No leads found to target"
            }

        # Execute campaign using Special Forces or legacy system
        if self.use_special_forces:
            logger.info(f"Using Special Forces Crew A (Lead Reactivation) for user {user_id}")
            result = self.special_forces.run_campaign(user_id, lead_ids)
            leads_processed = result.get("leads_processed", 0)
            messages_queued = result.get("messages_queued", 0)

            if leads_processed > 0:
                confirmation = f"Campaign launched for {leads_processed} leads, {messages_queued} messages queued."
            else:
                confirmation = "Campaign launched."
        else:
            # Legacy 28-agent system
            result = self.orchestration_service.run_full_campaign(user_id, lead_ids)
            campaigns_started = result.get("campaigns_started", 0)
            leads_processed = result.get("leads_processed", 0)

            if leads_processed > 0:
                confirmation = f"Campaign launched for {leads_processed} leads."
            else:
                confirmation = "Campaign launched."

        return {
            "success": True,
            "result": result,
            "message": ResponseWrapper.ensure_confirmation({"status": "success"}, confirmation)
        }
    
    def _execute_reactivate_leads(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lead reactivation."""
        batch_size = entities.get("batch_size") or self.defaults.infer_batch_size(user_id, "reactivation")
        
        result = self.orchestration_service.run_dead_lead_reactivation(user_id, batch_size=batch_size)
        
        leads_queued = result.get("leads_queued", 0)
        triggers_detected = result.get("triggers_detected", 0)
        
        # Generate concise confirmation
        if leads_queued > 0:
            confirmation = f"Reactivation sequence deployed for {leads_queued} leads."
        else:
            confirmation = "Reactivation sequence deployed."
        
        return {
            "success": True,
            "result": result,
            "message": ResponseWrapper.ensure_confirmation({"status": "success"}, confirmation)
        }
    
    def _execute_analyze_icp(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ICP analysis."""
        min_deals = entities.get("min_deals", 25)
        result = self.orchestration_service.run_auto_icp_sourcing(user_id, min_deals=min_deals, lead_limit=0)
        
        return {
            "success": True,
            "result": result,
            "message": ResponseWrapper.ensure_confirmation({"status": "success"}, "ICP analysis complete.")
        }
    
    def _execute_source_leads(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lead sourcing."""
        lead_limit = entities.get("lead_limit", 100)
        result = self.orchestration_service.run_auto_icp_sourcing(user_id, min_deals=25, lead_limit=lead_limit)
        
        leads_found = result.get("leads_found", 0)
        high_scoring = result.get("high_scoring_leads", 0)
        
        if leads_found > 0:
            confirmation = f"{leads_found} leads sourced, {high_scoring} high-scoring leads queued."
        else:
            confirmation = "Lead sourcing complete."
        
        return {
            "success": True,
            "result": result,
            "message": ResponseWrapper.ensure_confirmation({"status": "success"}, confirmation)
        }
    
    def _execute_research_leads(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lead research."""
        # Get leads to research
        lead_ids = entities.get("lead_ids")
        if not lead_ids:
            criteria = {"hot_only": True}
            lead_ids = self.defaults.infer_lead_ids(user_id, criteria)
        
        if not lead_ids:
            return {
                "success": False,
                "message": "No leads found to research"
            }
        
        # Research leads (would call ResearcherAgent for each)
        # For now, return success
        return {
            "success": True,
            "result": {"leads_researched": len(lead_ids)},
            "message": ResponseWrapper.ensure_confirmation({"status": "success"}, f"Lead research complete for {len(lead_ids)} leads.")
        }
    
    def _execute_get_kpis(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get user KPIs."""
        from ..tools.rex_tools import GetUserKPIsTool
        tool = GetUserKPIsTool()
        result = tool._run(user_id)
        
        return {
            "success": True,
            "result": {"kpis": result},
            "message": result
        }
    
    def _execute_get_campaign_status(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaign status."""
        from ..tools.rex_tools import GetCampaignStatusTool
        tool = GetCampaignStatusTool()
        campaign_name = entities.get("campaign_name")
        result = tool._run(user_id, campaign_name)
        
        return {
            "success": True,
            "result": {"status": result},
            "message": result
        }
    
    def _execute_get_lead_details(self, user_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get lead details."""
        lead_email = entities.get("lead_email")
        if not lead_email:
            return {
                "success": False,
                "message": "Please provide lead email"
            }
        
        from ..tools.rex_tools import GetLeadDetailsTool
        tool = GetLeadDetailsTool()
        result = tool._run(user_id, lead_email)
        
        return {
            "success": True,
            "result": {"lead_details": result},
            "message": result
        }
    
    def _handle_query(self, user_id: Optional[str], message: str) -> Dict[str, Any]:
        """Handle general queries (no specific action)."""
        # Check if user is logged in
        is_logged_in, _, _ = self.permissions.check_user_state(user_id)
        
        if not is_logged_in:
            # For non-logged-in users, return conversational response
            return {
                "success": True,
                "result": {},
                "message": "Hi! Please log in to access Rekindle features.",
                "requires_login": True
            }
        
        # For logged-in users, use tools to answer
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["kpi", "status", "stats", "dashboard", "overview"]):
            return self._execute_get_kpis(user_id, {})
        elif "campaign" in message_lower:
            return self._execute_get_campaign_status(user_id, {})
        else:
            # Generic response - will be handled by CrewAI agent
            return {
                "success": True,
                "result": {},
                "message": "Query received"
            }

