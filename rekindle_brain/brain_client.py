"""
Rekindle Brain Client

Client for interacting with the Rekindle Brain fine-tuned LLM model.
Handles message generation, action planning, and other brain capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)

class BrainClient:
    """Client for Rekindle Brain API"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.capabilities = [
            "write_message", "plan_actions", "improve_sequence",
            "infer_persona", "generate_content", "optimize_timing"
        ]

    async def call(self, capability: str, task_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Call a specific Brain capability"""
        if capability not in self.capabilities:
            raise ValueError(f"Unknown capability: {capability}")

        logger.info(f"Calling Brain capability: {capability}")

        try:
            # Prepare request
            request_data = self._prepare_request(capability, task_data, context)

            # Make API call
            result = await self._make_api_call(capability, request_data)

            # Format response
            formatted_result = self._format_response(capability, result, task_data)

            logger.info(f"Brain {capability} completed successfully")
            return formatted_result

        except Exception as e:
            logger.error(f"Brain {capability} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "capability": capability,
                "timestamp": datetime.now().isoformat()
            }

    async def _make_api_call(self, capability: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to Brain service"""
        endpoint = f"{self.base_url}/brain/{capability}"

        try:
            async with self.session.post(
                endpoint,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Brain API error {response.status}: {error_text}")

                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Brain API: {e}")
            # Return fallback response for development
            return self._get_fallback_response(capability, request_data)

    def _prepare_request(self, capability: str, task_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Prepare request data for Brain API"""
        base_request = {
            "timestamp": datetime.now().isoformat(),
            "context": context.__dict__ if context else {},
            "task_data": task_data
        }

        if capability == "write_message":
            return {
                **base_request,
                "lead_profile": task_data.get("lead_profile", {}),
                "persona": task_data.get("persona", "professional"),
                "channel": task_data.get("channel", "email"),
                "objective": task_data.get("objective", "book_meeting"),
                "tone": task_data.get("tone", "professional"),
                "constraints": task_data.get("constraints", {})
            }

        elif capability == "plan_actions":
            return {
                **base_request,
                "pipeline_state": task_data.get("pipeline_state", {}),
                "risks": task_data.get("risks", []),
                "time_horizon": task_data.get("time_horizon", "week"),
                "goals": task_data.get("goals", [])
            }

        elif capability == "improve_sequence":
            return {
                **base_request,
                "current_sequence": task_data.get("current_sequence", []),
                "performance_data": task_data.get("performance_data", {}),
                "target_improvement": task_data.get("target_improvement", 0.2)
            }

        elif capability == "infer_persona":
            return {
                **base_request,
                "lead_data": task_data.get("lead_data", {}),
                "interaction_history": task_data.get("interaction_history", []),
                "company_context": task_data.get("company_context", {})
            }

        else:
            return base_request

    def _format_response(self, capability: str, raw_response: Dict[str, Any], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Brain API response for ARE consumption"""
        return {
            "success": True,
            "capability": capability,
            "task_id": task_data.get("id"),
            "brain_output": raw_response,
            "confidence": raw_response.get("confidence", 0.8),
            "processing_time": raw_response.get("processing_time", 0),
            "model_version": raw_response.get("model_version", "unknown"),
            "formatted_response": self._extract_formatted_output(capability, raw_response),
            "timestamp": datetime.now().isoformat()
        }

    def _extract_formatted_output(self, capability: str, response: Dict[str, Any]) -> Any:
        """Extract the main output from Brain response"""
        if capability == "write_message":
            return {
                "subject": response.get("subject", ""),
                "body": response.get("body", ""),
                "call_to_action": response.get("call_to_action", ""),
                "tone": response.get("tone", "professional"),
                "personalization_score": response.get("personalization_score", 0.5)
            }

        elif capability == "plan_actions":
            return {
                "recommended_actions": response.get("actions", []),
                "expected_outcomes": response.get("outcomes", {}),
                "risk_assessment": response.get("risks", {}),
                "timeline": response.get("timeline", {})
            }

        elif capability == "improve_sequence":
            return {
                "improved_sequence": response.get("sequence", []),
                "expected_improvement": response.get("improvement", 0),
                "change_reasons": response.get("reasons", [])
            }

        elif capability == "infer_persona":
            return {
                "persona": response.get("persona", "unknown"),
                "confidence": response.get("confidence", 0.5),
                "traits": response.get("traits", []),
                "communication_style": response.get("communication_style", "professional")
            }

        else:
            return response

    def _get_fallback_response(self, capability: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback response when Brain API is unavailable"""
        logger.warning(f"Using fallback response for {capability}")

        if capability == "write_message":
            return {
                "subject": "Let's discuss how we can help your business grow",
                "body": "Hi there,\n\nI noticed your company is doing great work in the industry. I'd love to learn more about your current challenges and see if we can help.\n\nWould you be open to a quick call?\n\nBest regards,\nSales Team",
                "call_to_action": "Schedule a call",
                "tone": "professional",
                "confidence": 0.6,
                "processing_time": 1.0,
                "model_version": "fallback"
            }

        elif capability == "plan_actions":
            return {
                "actions": [
                    {"type": "send_email", "priority": "high", "reason": "Initial outreach"},
                    {"type": "follow_up", "priority": "medium", "delay_days": 3, "reason": "Nurture lead"}
                ],
                "outcomes": {"meetings_booked": 0.15, "replies": 0.25},
                "risks": {"low": "Standard outreach"},
                "timeline": "1 week",
                "confidence": 0.5,
                "processing_time": 0.5,
                "model_version": "fallback"
            }

        else:
            return {
                "fallback": True,
                "message": f"Fallback response for {capability}",
                "confidence": 0.3,
                "processing_time": 0.1,
                "model_version": "fallback"
            }

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get Brain capabilities"""
        return {
            "capabilities": self.capabilities,
            "base_url": self.base_url,
            "status": "available",  # Would check actual service health
            "supported_features": [
                "message_generation",
                "action_planning",
                "sequence_optimization",
                "persona_inference",
                "content_personalization"
            ],
            "typical_latency": {
                "write_message": "2-5 seconds",
                "plan_actions": "3-8 seconds",
                "improve_sequence": "5-15 seconds",
                "infer_persona": "1-3 seconds"
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check Brain service health"""
        try:
            async with self.session.get(f"{self.base_url}/health", timeout=5) as response:
                if response.status == 200:
                    health_data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time": health_data.get("response_time", 0),
                        "model_loaded": health_data.get("model_loaded", False),
                        "last_updated": health_data.get("last_updated")
                    }
                else:
                    return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    async def close(self):
        """Close the client session"""
        await self.session.close()
        logger.info("Brain client closed")