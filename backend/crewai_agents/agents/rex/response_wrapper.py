"""
Response Wrapper for Action-First Behavior

Wraps all agent responses to ensure they follow action-first protocol.
Removes demo/sales/tutorial language and enforces concise confirmations.
"""

from typing import Dict, Any, Optional
from ..utils.action_first_enforcer import ActionFirstEnforcer
import logging

logger = logging.getLogger(__name__)


class ResponseWrapper:
    """Wraps agent responses to enforce action-first behavior."""
    
    @staticmethod
    def wrap_agent_response(response: Any, agent_name: str) -> str:
        """
        Wrap agent response to ensure action-first compliance.
        
        Args:
            response: Raw response from agent (dict, str, or other)
            agent_name: Name of the agent for logging
        
        Returns:
            Concise, action-first confirmation string
        """
        # Convert response to string if needed
        if isinstance(response, dict):
            # Extract message if available
            message = response.get("message") or response.get("response") or response.get("status")
            if message:
                response_str = str(message)
            else:
                # Generate concise confirmation from status
                status = response.get("status", "completed")
                if status == "success":
                    response_str = f"{agent_name} task completed."
                else:
                    response_str = f"{agent_name} task {status}."
        elif isinstance(response, str):
            response_str = response
        else:
            response_str = str(response)
        
        # Clean response using action-first enforcer
        cleaned = ActionFirstEnforcer.clean_response(response_str)
        
        # Validate compliance
        if not ActionFirstEnforcer.validate_response(cleaned):
            logger.warning(f"Agent {agent_name} response failed validation, cleaned: {cleaned[:100]}")
        
        return cleaned
    
    @staticmethod
    def ensure_confirmation(result: Dict[str, Any], default_message: str) -> str:
        """
        Ensure result has a concise confirmation message.
        
        Args:
            result: Execution result dictionary
            default_message: Default confirmation if none found
        
        Returns:
            Concise confirmation string
        """
        # Check for existing message
        message = result.get("message") or result.get("response") or result.get("confirmation")
        
        if message:
            return ActionFirstEnforcer.clean_response(str(message))
        
        # Generate from status
        status = result.get("status", "completed")
        if status == "success":
            return default_message
        elif status == "error":
            error = result.get("error", "Unknown error")
            return f"Error: {error[:50]}"
        else:
            return f"Task {status}."

