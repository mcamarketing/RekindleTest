"""
Agent Integration Module

Handles communication between Rekindle Brain and ARE agents:
- Planner: Routes goal decomposition to Brain or CrewAI agents
- Critic: Labels successful/failed patterns for training signals
- Social Listener: Ingests social data and converts to embeddings
- Guardrail: Validates prompt security and compliance
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import BrainConfig

logger = logging.getLogger(__name__)

class AgentIntegrator:
    """Manages integration between Rekindle Brain and ARE agents"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.agent_endpoints = config.agent_integration["are_endpoints"]
        self.communication_config = config.agent_integration["communication_protocol"]
        self.session: Optional[aiohttp.ClientSession] = None
        self.agent_health: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize agent integration"""
        logger.info("Initializing AgentIntegrator")

        # Create HTTP session for agent communication
        timeout = aiohttp.ClientTimeout(total=self.communication_config["timeout_seconds"])
        self.session = aiohttp.ClientSession(timeout=timeout)

        # Test agent connections
        await self._test_agent_connections()

        logger.info("AgentIntegrator initialized")

    async def gather_insights(self, business_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather insights from ARE agents for business query processing

        Args:
            business_query: Business query being processed

        Returns:
            Dictionary containing insights from all agents
        """
        logger.info("Gathering insights from ARE agents")

        insights = {
            "social_insights": [],
            "critic_evaluation": {},
            "planner_suggestions": [],
            "guardrail_validation": {},
            "agent_responses": {}
        }

        # Gather insights concurrently
        tasks = [
            self._get_social_insights(business_query),
            self._get_critic_evaluation(business_query),
            self._get_planner_suggestions(business_query),
            self._get_guardrail_validation(business_query)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            agent_name = ["social", "critic", "planner", "guardrail"][i]

            if isinstance(result, Exception):
                logger.warning(f"Failed to get insights from {agent_name}: {result}")
                insights["agent_responses"][agent_name] = {"error": str(result)}
            else:
                insights["agent_responses"][agent_name] = {"success": True}
                self._integrate_agent_result(insights, agent_name, result)

        logger.info(f"Gathered insights from {len([r for r in results if not isinstance(r, Exception)])} agents")

        return insights

    async def _get_social_insights(self, business_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get social intelligence insights from Social Listener agent"""
        try:
            endpoint = self.agent_endpoints["social_listener"]

            payload = {
                "query": business_query.get("goal", ""),
                "task_type": business_query.get("task_type", "general"),
                "timeframe": "recent",  # Could be configurable
                "topics": business_query.get("social_intel", [])
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            # Extract social insights
            insights = []
            if "insights" in response:
                for insight in response["insights"]:
                    insights.append({
                        "topic": insight.get("topic", "general"),
                        "summary": insight.get("summary", ""),
                        "sentiment": insight.get("sentiment", "neutral"),
                        "confidence": insight.get("confidence", 0.5),
                        "source": "social_listener"
                    })

            return insights

        except Exception as e:
            logger.error(f"Failed to get social insights: {e}")
            return []

    async def _get_critic_evaluation(self, business_query: Dict[str, Any]) -> Dict[str, Any]:
        """Get evaluation from Critic agent"""
        try:
            endpoint = self.agent_endpoints["critic"]

            payload = {
                "evaluate_type": "business_strategy",
                "content": business_query.get("goal", ""),
                "context": business_query.get("context", {}),
                "constraints": business_query.get("constraints", {})
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            # Extract critic evaluation
            evaluation = {
                "success_rate": response.get("success_rate", 0.5),
                "top_patterns": response.get("top_patterns", []),
                "failure_patterns": response.get("failure_patterns", []),
                "improvement_suggestions": response.get("improvement_suggestions", []),
                "confidence_score": response.get("confidence_score", 0.5)
            }

            return evaluation

        except Exception as e:
            logger.error(f"Failed to get critic evaluation: {e}")
            return {}

    async def _get_planner_suggestions(self, business_query: Dict[str, Any]) -> List[str]:
        """Get planning suggestions from Planner agent"""
        try:
            endpoint = self.agent_endpoints["planner"]

            payload = {
                "goal": business_query.get("goal", ""),
                "task_type": business_query.get("task_type", "general"),
                "current_context": business_query.get("context", {}),
                "request_type": "brain_integration"
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            # Extract planner suggestions
            suggestions = response.get("suggestions", [])
            if isinstance(suggestions, list):
                return suggestions
            else:
                return [str(suggestions)]

        except Exception as e:
            logger.error(f"Failed to get planner suggestions: {e}")
            return []

    async def _get_guardrail_validation(self, business_query: Dict[str, Any]) -> Dict[str, Any]:
        """Get validation from Guardrail agent"""
        try:
            endpoint = self.agent_endpoints["guardrail"]

            payload = {
                "content": business_query.get("goal", ""),
                "content_type": "business_query",
                "context": "brain_processing",
                "check_types": ["compliance", "safety", "privacy"]
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            # Extract guardrail validation
            validation = {
                "approved": response.get("approved", True),
                "issues": response.get("issues", []),
                "recommendations": response.get("recommendations", []),
                "risk_level": response.get("risk_level", "low")
            }

            return validation

        except Exception as e:
            logger.error(f"Failed to get guardrail validation: {e}")
            return {"approved": True, "issues": [], "risk_level": "unknown"}

    async def get_critic_evaluation(self, success_patterns: List[Dict[str, Any]],
                                  failure_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get comprehensive critic evaluation for training signals"""
        try:
            endpoint = self.agent_endpoints["critic"]

            payload = {
                "evaluate_type": "training_signal_generation",
                "success_patterns": success_patterns,
                "failure_patterns": failure_patterns,
                "analysis_type": "pattern_recognition"
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            return response

        except Exception as e:
            logger.error(f"Failed to get critic evaluation for training: {e}")
            return {}

    async def notify_social_update(self, processed_data: List[Dict[str, Any]]):
        """Notify agents of social intelligence updates"""
        logger.info(f"Notifying agents of social data update: {len(processed_data)} items")

        # Notify relevant agents (could be expanded)
        notifications = [
            self._notify_agent("critic", "social_intelligence_updated", {
                "new_insights": len(processed_data),
                "topics": list(set(item.get("metadata", {}).get("topics", []) for item in processed_data))
            }),
            self._notify_agent("planner", "social_intelligence_updated", {
                "update_type": "market_intelligence",
                "freshness": "real_time"
            })
        ]

        await asyncio.gather(*notifications, return_exceptions=True)

    async def _notify_agent(self, agent_name: str, notification_type: str, data: Dict[str, Any]):
        """Send notification to specific agent"""
        try:
            endpoint = self.agent_endpoints.get(agent_name)
            if not endpoint:
                return

            payload = {
                "notification_type": notification_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

            await self._call_agent_endpoint(endpoint, payload, method="POST")

        except Exception as e:
            logger.warning(f"Failed to notify {agent_name}: {e}")

    async def _call_agent_endpoint(self, endpoint: str, payload: Dict[str, Any],
                                 method: str = "POST") -> Dict[str, Any]:
        """Call ARE agent endpoint"""
        if not self.session:
            raise RuntimeError("AgentIntegrator not initialized")

        try:
            headers = {"Content-Type": "application/json"}

            if method.upper() == "POST":
                async with self.session.post(endpoint, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                async with self.session.get(endpoint, params=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Agent endpoint call failed: {endpoint} - {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Agent endpoint timeout: {endpoint}")
            raise

    def _integrate_agent_result(self, insights: Dict[str, Any], agent_name: str, result):
        """Integrate agent result into insights dictionary"""
        if agent_name == "social":
            insights["social_insights"] = result
        elif agent_name == "critic":
            insights["critic_evaluation"] = result
        elif agent_name == "planner":
            insights["planner_suggestions"] = result
        elif agent_name == "guardrail":
            insights["guardrail_validation"] = result

    async def _test_agent_connections(self):
        """Test connectivity to all ARE agent endpoints"""
        logger.info("Testing ARE agent connections")

        for agent_name, endpoint in self.agent_endpoints.items():
            try:
                # Simple health check
                payload = {"action": "health_check"}
                response = await self._call_agent_endpoint(endpoint, payload)

                self.agent_health[agent_name] = {
                    "status": "healthy",
                    "last_check": datetime.now().isoformat(),
                    "response_time": response.get("response_time", 0)
                }

                logger.info(f"✓ {agent_name} agent connection healthy")

            except Exception as e:
                self.agent_health[agent_name] = {
                    "status": "unhealthy",
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }

                logger.warning(f"✗ {agent_name} agent connection failed: {e}")

    async def get_agent_health(self) -> Dict[str, Any]:
        """Get health status of all ARE agents"""
        # Update health checks periodically
        if any((datetime.now() - datetime.fromisoformat(h["last_check"])).total_seconds() > 300  # 5 minutes
               for h in self.agent_health.values() if "last_check" in h):
            await self._test_agent_connections()

        return self.agent_health.copy()

    async def route_to_brain_or_agents(self, goal: Dict[str, Any]) -> str:
        """
        Decide whether to route goal to Brain or CrewAI agents

        Returns:
            "brain" or "crewai"
        """
        try:
            # Get planner recommendation
            endpoint = self.agent_endpoints["planner"]

            payload = {
                "goal": goal,
                "routing_decision": True,
                "available_options": ["brain", "crewai"]
            }

            response = await self._call_agent_endpoint(endpoint, payload)

            routing = response.get("recommended_routing", "brain")

            logger.info(f"Planner recommended routing to: {routing}")

            return routing

        except Exception as e:
            logger.warning(f"Failed to get routing decision, defaulting to brain: {e}")
            return "brain"

    async def submit_training_signal(self, signal: Dict[str, Any]):
        """Submit training signal to relevant agents"""
        logger.info("Submitting training signal to agents")

        # Submit to critic for evaluation
        try:
            endpoint = self.agent_endpoints["critic"]

            payload = {
                "signal_type": "training_feedback",
                "signal_data": signal,
                "source": "brain"
            }

            await self._call_agent_endpoint(endpoint, payload)

        except Exception as e:
            logger.warning(f"Failed to submit training signal to critic: {e}")

    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all connected agents"""
        capabilities = {}

        for agent_name in self.agent_endpoints.keys():
            try:
                endpoint = self.agent_endpoints[agent_name]

                payload = {"action": "get_capabilities"}
                response = await self._call_agent_endpoint(endpoint, payload)

                capabilities[agent_name] = response.get("capabilities", [])

            except Exception as e:
                logger.warning(f"Failed to get capabilities for {agent_name}: {e}")
                capabilities[agent_name] = []

        return capabilities

    async def shutdown(self):
        """Shutdown agent integration"""
        logger.info("Shutting down AgentIntegrator")

        if self.session:
            await self.session.close()
            self.session = None

        self.agent_health.clear()

        logger.info("AgentIntegrator shutdown complete")