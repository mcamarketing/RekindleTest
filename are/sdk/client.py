"""
ARE SDK Client

Main client class for interacting with the ARE (Autonomous Revenue Engine) system.
Provides high-level methods for goal processing, agent execution, and system monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import json

from .types import (
    AREConfig, Goal, Task, ExecutionPlan, AgentResponse,
    AgentType, AREEvent, AgentMetrics, GoalType, Priority
)
from .exceptions import (
    AREError, AgentUnavailableError, ValidationError, TimeoutError,
    NetworkError, AuthenticationError
)
from .communication import HTTPClient, WebSocketClient

logger = logging.getLogger(__name__)


class AREClient:
    """
    Main client for ARE SDK

    Provides a unified interface to all ARE agents and services.
    Handles communication, error handling, and response processing.
    """

    def __init__(self, config: AREConfig = None):
        self.config = config or AREConfig()
        self.http_client = HTTPClient(self.config)
        self.ws_client = None

        if self.config.websocket_url:
            self.ws_client = WebSocketClient(self.config)

        self._event_handlers: Dict[str, List[Callable]] = {}
        self._metrics: Dict[AgentType, AgentMetrics] = {}

        # Initialize metrics for all agent types
        for agent_type in AgentType:
            self._metrics[agent_type] = AgentMetrics(agent_type)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Establish connection to ARE system"""
        try:
            # Test HTTP connection
            await self.http_client.connect()

            # Connect WebSocket if configured
            if self.ws_client:
                await self.ws_client.connect()
                self.ws_client.on_event(self._handle_event)

            logger.info("ARE SDK client connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect ARE client: {e}")
            raise NetworkError(self.config.base_url, "CONNECT", str(e))

    async def disconnect(self):
        """Disconnect from ARE system"""
        try:
            if self.ws_client:
                await self.ws_client.disconnect()

            await self.http_client.disconnect()
            logger.info("ARE SDK client disconnected")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def process_goal(self, goal: Goal) -> ExecutionPlan:
        """
        Process a business goal through the ARE system

        Args:
            goal: The goal to process

        Returns:
            ExecutionPlan: Complete plan with tasks and dependencies

        Raises:
            ValidationError: If goal is invalid
            TimeoutError: If processing times out
            AREError: For other processing errors
        """
        try:
            # Validate goal
            self._validate_goal(goal)

            # Send to ARE planner
            response = await self.http_client.post(
                "/goals/process",
                goal.to_dict(),
                timeout=self.config.timeout
            )

            # Parse response
            plan_data = response.get("plan", {})
            plan = ExecutionPlan(
                plan_id=plan_data["plan_id"],
                goal=goal,
                tasks=[Task(**task_data) for task_data in plan_data.get("tasks", [])],
                dependencies=plan_data.get("dependencies", []),
                agent_assignments=plan_data.get("agent_assignments", {}),
                risk_assessment=plan_data.get("risk_assessment", {}),
                estimated_completion=datetime.fromisoformat(plan_data["estimated_completion"]),
                created_at=datetime.fromisoformat(plan_data["created_at"])
            )

            logger.info(f"Goal processed successfully: {plan.plan_id}")
            return plan

        except Exception as e:
            logger.error(f"Goal processing failed: {e}")
            self._update_metrics(goal, success=False)
            raise self._handle_error(e, "goal_processing")

    async def execute_task(self, task: Task) -> AgentResponse:
        """
        Execute a single task using the appropriate agent

        Args:
            task: The task to execute

        Returns:
            AgentResponse: Agent execution result

        Raises:
            AgentUnavailableError: If required agent is unavailable
            TimeoutError: If execution times out
            AREError: For other execution errors
        """
        try:
            # Validate task
            self._validate_task(task)

            # Route to appropriate agent
            agent_endpoint = f"/agents/{task.agent_type.value}/execute"

            response = await self.http_client.post(
                agent_endpoint,
                task.to_dict(),
                timeout=task.estimated_duration or self.config.timeout
            )

            # Parse response
            agent_response = AgentResponse(
                agent_type=task.agent_type,
                task_id=task.id,
                success=response.get("success", False),
                result=response.get("result"),
                error=response.get("error"),
                execution_time=response.get("execution_time"),
                confidence_score=response.get("confidence_score"),
                metadata=response.get("metadata", {})
            )

            # Update metrics
            self._update_metrics(task, agent_response.success)

            logger.info(f"Task executed: {task.id} - {agent_response.success}")
            return agent_response

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            self._update_metrics(task, success=False)
            raise self._handle_error(e, "task_execution")

    async def get_agent_status(self, agent_type: AgentType) -> Dict[str, Any]:
        """
        Get status and health of a specific agent

        Args:
            agent_type: Type of agent to check

        Returns:
            Dict with agent status information
        """
        try:
            response = await self.http_client.get(f"/agents/{agent_type.value}/status")
            return response

        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            raise self._handle_error(e, "status_check")

    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get overall system metrics and health status

        Returns:
            Dict with system-wide metrics
        """
        try:
            response = await self.http_client.get("/metrics")
            return response

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            raise self._handle_error(e, "metrics_retrieval")

    async def stream_events(self, event_types: List[str] = None) -> None:
        """
        Start streaming ARE events

        Args:
            event_types: List of event types to listen for (None for all)
        """
        if not self.ws_client:
            raise AREError("WebSocket client not configured for streaming")

        await self.ws_client.subscribe(event_types or [])

    def on_event(self, event_type: str, callback: Callable):
        """
        Register event handler

        Args:
            event_type: Type of event to handle
            callback: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(callback)

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task

        Args:
            task_id: ID of task to cancel

        Returns:
            bool: True if cancelled successfully
        """
        try:
            response = await self.http_client.post(f"/tasks/{task_id}/cancel", {})
            return response.get("cancelled", False)

        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            raise self._handle_error(e, "task_cancellation")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a specific task

        Args:
            task_id: ID of task to check

        Returns:
            Dict with task status information
        """
        try:
            response = await self.http_client.get(f"/tasks/{task_id}/status")
            return response

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise self._handle_error(e, "status_check")

    def _validate_goal(self, goal: Goal):
        """Validate goal parameters"""
        if not goal.description:
            raise ValidationError("description", goal.description, "Goal description is required")

        if not isinstance(goal.goal_type, GoalType):
            raise ValidationError("goal_type", goal.goal_type, "Invalid goal type")

        if goal.priority not in Priority:
            raise ValidationError("priority", goal.priority, "Invalid priority level")

    def _validate_task(self, task: Task):
        """Validate task parameters"""
        if not task.id:
            raise ValidationError("id", task.id, "Task ID is required")

        if not task.description:
            raise ValidationError("description", task.description, "Task description is required")

        if not isinstance(task.agent_type, AgentType):
            raise ValidationError("agent_type", task.agent_type, "Invalid agent type")

        if not task.capabilities:
            raise ValidationError("capabilities", task.capabilities, "Task must specify required capabilities")

    def _update_metrics(self, request: Union[Goal, Task], success: bool):
        """Update internal metrics"""
        if isinstance(request, Task):
            agent_type = request.agent_type
        else:  # Goal
            agent_type = AgentType.PLANNER  # Goals go through planner

        metrics = self._metrics[agent_type]
        metrics.requests_total += 1
        metrics.last_request_at = datetime.now()

        if success:
            metrics.requests_successful += 1
        else:
            metrics.requests_failed += 1

        # Update error rate
        if metrics.requests_total > 0:
            metrics.error_rate = metrics.requests_failed / metrics.requests_total

    def _handle_event(self, event: AREEvent):
        """Handle incoming events from WebSocket"""
        # Call registered handlers
        handlers = self._event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                asyncio.create_task(handler(event))
            except Exception as e:
                logger.error(f"Event handler error: {e}")

    def _handle_error(self, error: Exception, context: str) -> AREError:
        """Convert exceptions to ARE-specific errors"""
        if isinstance(error, AREError):
            return error

        # Network errors
        if "connection" in str(error).lower() or "timeout" in str(error).lower():
            return TimeoutError(context, self.config.timeout, str(error))

        # Default to generic ARE error
        return AREError(f"{context} failed: {str(error)}", details={"original_error": str(error)})

    def get_metrics(self) -> Dict[AgentType, AgentMetrics]:
        """Get current metrics for all agents"""
        return self._metrics.copy()

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on ARE system"""
        try:
            response = await self.http_client.get("/health")
            return {
                "status": "healthy" if response.get("status") == "ok" else "unhealthy",
                "details": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }