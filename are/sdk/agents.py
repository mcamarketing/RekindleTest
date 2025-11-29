"""
ARE SDK Agent Clients

Individual client classes for each ARE agent type, providing
specialized interfaces and methods for agent-specific operations.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .client import AREClient
from .types import (
    AgentType, AgentResponse, Task, Goal, GoalType, Priority,
    AREConfig
)
from .exceptions import AREError, ValidationError

logger = logging.getLogger(__name__)


class BaseAgentClient:
    """Base class for all agent clients"""

    def __init__(self, client: AREClient, agent_type: AgentType):
        self.client = client
        self.agent_type = agent_type

    async def execute(self, task_data: Dict[str, Any], timeout: int = None) -> AgentResponse:
        """Execute a task using this agent"""
        task = Task(
            id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(task_data)) % 10000}",
            description=task_data.get("description", f"Execute {self.agent_type.value} task"),
            agent_type=self.agent_type,
            capabilities=task_data.get("capabilities", []),
            input_data=task_data,
            priority=task_data.get("priority", Priority.MEDIUM),
            estimated_duration=task_data.get("estimated_duration", 300)
        )

        return await self.client.execute_task(task)

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return await self.client.get_agent_status(self.agent_type)

    async def is_available(self) -> bool:
        """Check if agent is available"""
        try:
            status = await self.get_status()
            return status.get("status") == "available"
        except Exception:
            return False


class PlannerAgent(BaseAgentClient):
    """Client for ARE Planner Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.PLANNER)

    async def create_plan(self, goal: Goal) -> Dict[str, Any]:
        """Create execution plan for a goal"""
        response = await self.execute({
            "action": "create_plan",
            "goal": goal.to_dict(),
            "description": f"Create execution plan for goal: {goal.description}"
        })
        return response.result or {}

    async def decompose_goal(self, goal: Goal) -> List[Task]:
        """Break down goal into executable tasks"""
        response = await self.execute({
            "action": "decompose_goal",
            "goal": goal.to_dict(),
            "capabilities": ["goal_analysis", "task_decomposition"],
            "description": f"Decompose goal into tasks: {goal.description}"
        })

        if response.result and "tasks" in response.result:
            return [Task(**task_data) for task_data in response.result["tasks"]]
        return []

    async def assess_risks(self, goal: Goal, tasks: List[Task]) -> Dict[str, Any]:
        """Assess execution risks for a plan"""
        response = await self.execute({
            "action": "assess_risks",
            "goal": goal.to_dict(),
            "tasks": [task.to_dict() for task in tasks],
            "capabilities": ["risk_assessment"],
            "description": f"Assess risks for goal execution: {goal.description}"
        })
        return response.result or {}


class ExecutorAgent(BaseAgentClient):
    """Client for ARE Executor Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.EXECUTOR)

    async def route_task(self, task: Task) -> AgentResponse:
        """Route a task to the appropriate agent"""
        response = await self.execute({
            "action": "route_task",
            "task": task.to_dict(),
            "capabilities": ["task_routing", "agent_coordination"],
            "description": f"Route task to appropriate agent: {task.description}"
        })
        return response

    async def coordinate_execution(self, plan_id: str) -> Dict[str, Any]:
        """Coordinate execution of a complete plan"""
        response = await self.execute({
            "action": "coordinate_execution",
            "plan_id": plan_id,
            "capabilities": ["workflow_orchestration", "progress_tracking"],
            "description": f"Coordinate execution for plan: {plan_id}"
        })
        return response.result or {}

    async def get_execution_status(self, plan_id: str) -> Dict[str, Any]:
        """Get execution status for a plan"""
        response = await self.execute({
            "action": "get_execution_status",
            "plan_id": plan_id,
            "capabilities": ["status_monitoring"],
            "description": f"Get execution status for plan: {plan_id}"
        })
        return response.result or {}


class CriticAgent(BaseAgentClient):
    """Client for ARE Critic Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.CRITIC)

    async def evaluate_performance(self, agent_responses: List[AgentResponse]) -> Dict[str, Any]:
        """Evaluate performance of agent executions"""
        response = await self.execute({
            "action": "evaluate_performance",
            "responses": [r.to_dict() for r in agent_responses],
            "capabilities": ["performance_analysis", "quality_assessment"],
            "description": "Evaluate agent execution performance and quality"
        })
        return response.result or {}

    async def generate_insights(self, execution_data: Dict[str, Any]) -> List[str]:
        """Generate insights from execution data"""
        response = await self.execute({
            "action": "generate_insights",
            "execution_data": execution_data,
            "capabilities": ["pattern_recognition", "insight_generation"],
            "description": "Generate actionable insights from execution data"
        })

        if response.result and "insights" in response.result:
            return response.result["insights"]
        return []

    async def assess_outcomes(self, goal: Goal, results: List[AgentResponse]) -> Dict[str, Any]:
        """Assess whether goal outcomes were achieved"""
        response = await self.execute({
            "action": "assess_outcomes",
            "goal": goal.to_dict(),
            "results": [r.to_dict() for r in results],
            "capabilities": ["outcome_evaluation", "goal_tracking"],
            "description": f"Assess goal achievement: {goal.description}"
        })
        return response.result or {}


class GuardrailAgent(BaseAgentClient):
    """Client for ARE Guardrail Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.GUARDRAIL)

    async def validate_content(self, content: str, context: str = "general") -> Dict[str, Any]:
        """Validate content for compliance and safety"""
        response = await self.execute({
            "action": "validate_content",
            "content": content,
            "context": context,
            "capabilities": ["content_filtering", "compliance_checking"],
            "description": f"Validate content for compliance: {context}"
        })
        return response.result or {}

    async def check_permissions(self, action: str, resource: str, user_id: str) -> bool:
        """Check if user has permission for action"""
        response = await self.execute({
            "action": "check_permissions",
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "capabilities": ["authorization", "access_control"],
            "description": f"Check permissions for {action} on {resource}"
        })
        return response.result.get("allowed", False) if response.result else False

    async def rate_limit_check(self, user_id: str, action: str) -> Dict[str, Any]:
        """Check rate limits for user action"""
        response = await self.execute({
            "action": "rate_limit_check",
            "user_id": user_id,
            "action": action,
            "capabilities": ["rate_limiting", "usage_monitoring"],
            "description": f"Check rate limits for {action}"
        })
        return response.result or {}


class RagServiceAgent(BaseAgentClient):
    """Client for ARE RAG Service Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.RAG_SERVICE)

    async def retrieve_context(self, query: str, context_type: str = "general") -> Dict[str, Any]:
        """Retrieve relevant context for a query"""
        response = await self.execute({
            "action": "retrieve_context",
            "query": query,
            "context_type": context_type,
            "capabilities": ["context_retrieval", "semantic_search"],
            "description": f"Retrieve context for query: {query[:50]}..."
        })
        return response.result or {}

    async def store_memory(self, key: str, data: Dict[str, Any], tags: List[str] = None) -> bool:
        """Store data in long-term memory"""
        response = await self.execute({
            "action": "store_memory",
            "key": key,
            "data": data,
            "tags": tags or [],
            "capabilities": ["memory_storage", "data_persistence"],
            "description": f"Store memory with key: {key}"
        })
        return response.success

    async def search_memory(self, query: str, tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search long-term memory"""
        response = await self.execute({
            "action": "search_memory",
            "query": query,
            "tags": tags or [],
            "limit": limit,
            "capabilities": ["memory_search", "pattern_matching"],
            "description": f"Search memory for: {query[:50]}..."
        })

        if response.result and "results" in response.result:
            return response.result["results"]
        return []

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory storage statistics"""
        response = await self.execute({
            "action": "get_memory_stats",
            "capabilities": ["memory_monitoring"],
            "description": "Get memory storage statistics"
        })
        return response.result or {}


class SocialListeningAgent(BaseAgentClient):
    """Client for ARE Social Listening Agent"""

    def __init__(self, client: AREClient):
        super().__init__(client, AgentType.SOCIAL_LISTENING)

    async def collect_intelligence(self, sources: List[str] = None, topics: List[str] = None) -> Dict[str, Any]:
        """Collect market intelligence from social sources"""
        response = await self.execute({
            "action": "collect_intelligence",
            "sources": sources or ["reddit", "forums"],
            "topics": topics or [],
            "capabilities": ["sentiment_analysis", "topic_modeling"],
            "description": "Collect market intelligence from social platforms"
        })
        return response.result or {}

    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        response = await self.execute({
            "action": "analyze_sentiment",
            "content": content,
            "capabilities": ["sentiment_analysis", "emotion_detection"],
            "description": f"Analyze sentiment of content: {content[:50]}..."
        })
        return response.result or {}

    async def extract_insights(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract actionable insights from social posts"""
        response = await self.execute({
            "action": "extract_insights",
            "posts": posts,
            "capabilities": ["insight_extraction", "pain_point_analysis"],
            "description": "Extract actionable insights from social data"
        })
        return response.result or {}

    async def get_intelligence_summary(self, time_period: str = "last_24_hours") -> Dict[str, Any]:
        """Get summary of collected intelligence"""
        response = await self.execute({
            "action": "get_intelligence_summary",
            "time_period": time_period,
            "capabilities": ["intelligence_aggregation"],
            "description": f"Get intelligence summary for {time_period}"
        })
        return response.result or {}


# Factory function to create agent clients
def create_agent_client(client: AREClient, agent_type: AgentType) -> BaseAgentClient:
    """Factory function to create appropriate agent client"""
    agent_clients = {
        AgentType.PLANNER: PlannerAgent,
        AgentType.EXECUTOR: ExecutorAgent,
        AgentType.CRITIC: CriticAgent,
        AgentType.GUARDRAIL: GuardrailAgent,
        AgentType.RAG_SERVICE: RagServiceAgent,
        AgentType.SOCIAL_LISTENING: SocialListeningAgent,
    }

    client_class = agent_clients.get(agent_type)
    if not client_class:
        raise AREError(f"No client available for agent type: {agent_type.value}")

    return client_class(client)