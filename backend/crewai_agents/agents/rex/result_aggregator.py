"""
Result Aggregator for REX

Collects outputs from agents/crews and generates concise, confident responses.
"""

from typing import Dict, List, Optional, Any
from .response_wrapper import ResponseWrapper
from ..utils.action_first_enforcer import ActionFirstEnforcer
import logging

logger = logging.getLogger(__name__)


class ResultAggregator:
    """Aggregates execution results into concise user-facing messages."""
    
    def __init__(self):
        """Initialize result aggregator."""
        pass
    
    def aggregate(self, execution_result: Dict[str, Any]) -> str:
        """
        Aggregate execution result into concise user message.
        
        Returns short, confident, actionable confirmation.
        Handles permission denials and login requirements.
        Enforces action-first protocol.
        """
        # Check for permission denial
        if execution_result.get("permission_denied"):
            message = execution_result.get("message", "This feature is not included in your package. Upgrade to access.")
            return ActionFirstEnforcer.clean_response(message)
        
        # Check for login requirement
        if execution_result.get("requires_login"):
            message = execution_result.get("message", "Hi! Please log in to access this feature.")
            return ActionFirstEnforcer.clean_response(message)
        
        if not execution_result.get("success"):
            error_msg = execution_result.get("message", "Error occurred")
            return f"Error: {error_msg[:50]}"
        
        action = execution_result.get("action")
        result = execution_result.get("result", {})
        message = execution_result.get("message", "")
        
        # Return the pre-formatted message from executor (already cleaned)
        if message:
            # Ensure it's action-first compliant
            cleaned = ActionFirstEnforcer.clean_response(message)
            if ActionFirstEnforcer.validate_response(cleaned):
                return cleaned
            # If validation fails, use fallback
            message = ""
        
        # Fallback: generate concise message based on action
        action_messages = {
            "launch_campaign": "Campaign launched.",
            "reactivate_leads": "Reactivation sequence deployed.",
            "analyze_icp": "ICP analysis complete.",
            "source_leads": "Lead sourcing complete.",
            "research_leads": "Lead research complete.",
            "get_kpis": result.get("kpis", "KPIs retrieved.") if isinstance(result.get("kpis"), str) else "KPIs retrieved.",
            "get_campaign_status": result.get("status", "Campaign status retrieved.") if isinstance(result.get("status"), str) else "Campaign status retrieved.",
            "get_lead_details": result.get("lead_details", "Lead details retrieved.") if isinstance(result.get("lead_details"), str) else "Lead details retrieved."
        }
        
        default_message = action_messages.get(action, "Task completed.")
        return ActionFirstEnforcer.clean_response(default_message)
    
    def format_error(self, error: Exception, action: Optional[str] = None) -> str:
        """Format error into concise message."""
        error_msg = str(error)
        
        # Don't expose internal errors
        if "database" in error_msg.lower() or "connection" in error_msg.lower():
            return "System error. Please try again."
        
        return f"Error: {error_msg[:100]}"

