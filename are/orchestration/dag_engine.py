"""
ARE DAG Engine - Executable Task Graph Orchestrator

Executes the ARE hierarchical orchestration graph, managing task dependencies,
parallel execution, error handling, and the continuous learning loop.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import redis.asyncio as redis

from ..agents.planner_agent import PlannerAgent
from ..agents.executor_agent import ExecutorAgent
from ..agents.critic_agent import CriticAgent
from ..agents.guardrail_agent import GuardrailAgent
from ..agents.rag_service import RagServiceAgent

logger = logging.getLogger(__name__)

@dataclass
class TaskNode:
    """Represents a node in the ARE orchestration graph"""
    id: str
    type: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0

@dataclass
class TaskEdge:
    """Represents an edge (dependency) in the ARE graph"""
    from_node: str
    to_node: str
    condition: Optional[str] = None
    data_flow: Optional[str] = None

@dataclass
class ExecutionContext:
    """Context for graph execution"""
    execution_id: str
    user_goal: Dict[str, Any]
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    edges: List[TaskEdge] = field(default_factory=list)
    data_store: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    status: str = "running"

class DAGEngine:
    """ARE DAG Execution Engine"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.session = aiohttp.ClientSession()
        self.graph_definition = None

        # Initialize ARE agents
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.critic = CriticAgent()
        self.guardrail = GuardrailAgent()
        self.rag_service = RagServiceAgent()

    async def load_graph(self, graph_path: str = "are/orchestration/task_graph.json"):
        """Load the ARE orchestration graph definition"""
        try:
            with open(graph_path, 'r') as f:
                self.graph_definition = json.load(f)
            logger.info(f"Loaded ARE graph with {len(self.graph_definition['are_graph']['nodes'])} nodes")
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            raise

    async def execute_goal(self, user_goal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a user goal through the ARE orchestration graph"""
        execution_id = f"are_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(user_goal)) % 10000}"

        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            user_goal=user_goal
        )

        # Initialize nodes from graph definition
        for node_def in self.graph_definition["are_graph"]["nodes"]:
            node = TaskNode(**node_def)
            context.nodes[node.id] = node

        # Initialize edges
        for edge_def in self.graph_definition["are_graph"]["edges"]:
            edge = TaskEdge(**edge_def)
            context.edges.append(edge)

        logger.info(f"Starting ARE execution {execution_id} for goal: {user_goal.get('description', 'Unknown')}")

        try:
            # Execute the graph
            result = await self._execute_graph(context)

            # Store execution result
            await self._store_execution_result(context, result)

            logger.info(f"ARE execution {execution_id} completed successfully")
            return result

        except Exception as e:
            logger.error(f"ARE execution {execution_id} failed: {e}")
            context.status = "failed"
            await self._store_execution_result(context, {"error": str(e)})
            raise

    async def _execute_graph(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute the ARE orchestration graph"""
        # Start with input node
        input_node = context.nodes["input"]
        input_node.status = "completed"
        input_node.result = context.user_goal
        input_node.completed_at = datetime.now()

        # Store input data
        context.data_store["user_goal"] = context.user_goal

        # Execute graph in topological order with parallel processing
        while True:
            # Find ready nodes (all dependencies satisfied)
            ready_nodes = self._get_ready_nodes(context)

            if not ready_nodes:
                # Check if execution is complete
                if self._is_execution_complete(context):
                    break
                else:
                    # Wait for running nodes to complete
                    await asyncio.sleep(1)
                    continue

            # Execute ready nodes in parallel
            tasks = []
            for node_id in ready_nodes:
                task = asyncio.create_task(self._execute_node(node_id, context))
                tasks.append(task)

            # Wait for all parallel tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

        # Collect final results
        return self._collect_execution_results(context)

    def _get_ready_nodes(self, context: ExecutionContext) -> List[str]:
        """Get nodes that are ready to execute (all dependencies satisfied)"""
        ready_nodes = []

        for node_id, node in context.nodes.items():
            if node.status != "pending":
                continue

            # Check if all incoming edges are satisfied
            dependencies_satisfied = True
            for edge in context.edges:
                if edge.to_node == node_id:
                    from_node = context.nodes.get(edge.from_node)
                    if not from_node or from_node.status != "completed":
                        dependencies_satisfied = False
                        break

            if dependencies_satisfied:
                ready_nodes.append(node_id)

        return ready_nodes

    async def _execute_node(self, node_id: str, context: ExecutionContext) -> None:
        """Execute a single node in the graph"""
        node = context.nodes[node_id]
        node.status = "running"
        node.started_at = datetime.now()

        logger.info(f"Executing node {node_id} ({node.type})")

        try:
            # Get input data from dependencies
            input_data = self._collect_node_inputs(node_id, context)

            # Execute the node based on its type
            result = await self._execute_node_by_type(node, input_data, context)

            # Store result
            node.result = result
            node.status = "completed"
            node.completed_at = datetime.now()

            # Store output data for dependent nodes
            if node.outputs:
                for output in node.outputs:
                    context.data_store[output] = result

            logger.info(f"Node {node_id} completed successfully")

        except Exception as e:
            logger.error(f"Node {node_id} execution failed: {e}")

            # Handle retry logic
            if self._should_retry(node):
                node.retry_count += 1
                node.status = "pending"
                await asyncio.sleep(node.retry_policy.get("backoff_seconds", 30))
            else:
                node.status = "failed"
                node.error = str(e)
                node.completed_at = datetime.now()

    async def _execute_node_by_type(self, node: TaskNode, input_data: Dict[str, Any], context: ExecutionContext) -> Any:
        """Execute a node based on its type"""
        if node.type == "user_goal":
            return input_data

        elif node.type == "ARE.PlannerAgent":
            return await self.planner.run(input_data, context)

        elif node.type == "ARE.RagServiceAgent":
            return await self.rag_service.run(input_data, context)

        elif node.type == "ARE.ExecutorAgent":
            return await self.executor.run(input_data, context)

        elif node.type == "ARE.CriticAgent":
            return await self.critic.run(input_data, context)

        elif node.type == "ARE.GuardrailAgent":
            return await self.guardrail.run(input_data, context)

        elif node.type == "CrewAI.AgentCluster":
            return await self._execute_crewai_cluster(input_data, context)

        elif node.type == "REX.Cluster":
            return await self._execute_rex_cluster(input_data, context)

        elif node.type == "Autonomous.Services":
            return await self._execute_services_cluster(input_data, context)

        elif node.type == "Rekindle.Brain":
            return await self._execute_brain(input_data, context)

        else:
            raise ValueError(f"Unknown node type: {node.type}")

    async def _execute_crewai_cluster(self, input_data: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute CrewAI agent cluster"""
        # Route to appropriate CrewAI wrapper based on task type
        task_assignments = input_data.get("task_assignments", [])

        results = {}
        for task in task_assignments:
            agent_type = task.get("agent_type")
            if agent_type:
                result = await self._call_crewai_agent(agent_type, task, context)
                results[agent_type] = result

        return {"crew_results": results}

    async def _execute_rex_cluster(self, input_data: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute REX system cluster"""
        # Route to appropriate REX wrapper
        task_assignments = input_data.get("task_assignments", [])

        results = {}
        for task in task_assignments:
            component = task.get("component", "decision")
            result = await self._call_rex_component(component, task, context)
            results[component] = result

        return {"rex_results": results}

    async def _execute_services_cluster(self, input_data: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute Autonomous Services cluster"""
        # Route to appropriate service wrapper
        task_assignments = input_data.get("task_assignments", [])

        results = {}
        for task in task_assignments:
            service = task.get("service")
            if service:
                result = await self._call_autonomous_service(service, task, context)
                results[service] = result

        return {"service_results": results}

    async def _execute_brain(self, input_data: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute Rekindle Brain"""
        # Call Brain API
        task_assignments = input_data.get("task_assignments", [])

        results = {}
        for task in task_assignments:
            capability = task.get("capability", "generate")
            result = await self._call_brain_api(capability, task, context)
            results[capability] = result

        return {"brain_results": results}

    async def _call_crewai_agent(self, agent_type: str, task: Dict[str, Any], context: ExecutionContext) -> Any:
        """Call a CrewAI agent wrapper"""
        # Import and call the appropriate wrapper
        try:
            module_name = f"are.integrations.crewai_wrappers.{agent_type.lower()}_wrapper"
            module = __import__(module_name, fromlist=[f"{agent_type}Wrapper"])
            wrapper_class = getattr(module, f"{agent_type}Wrapper")
            wrapper = wrapper_class()
            return await wrapper.run(task, context)
        except Exception as e:
            logger.error(f"Failed to call CrewAI agent {agent_type}: {e}")
            return {"error": str(e)}

    async def _call_rex_component(self, component: str, task: Dict[str, Any], context: ExecutionContext) -> Any:
        """Call a REX component wrapper"""
        try:
            module_name = f"are.integrations.rex_wrappers.rex_{component.lower()}"
            module = __import__(module_name, fromlist=[f"Rex{component.title()}Agent"])
            wrapper_class = getattr(module, f"Rex{component.title()}Agent")
            wrapper = wrapper_class()
            return await wrapper.run(task, context)
        except Exception as e:
            logger.error(f"Failed to call REX component {component}: {e}")
            return {"error": str(e)}

    async def _call_autonomous_service(self, service: str, task: Dict[str, Any], context: ExecutionContext) -> Any:
        """Call an Autonomous Service wrapper"""
        try:
            module_name = f"are.integrations.services_wrappers.{service.lower()}"
            module = __import__(module_name, fromlist=[f"{service}Agent"])
            wrapper_class = getattr(module, f"{service}Agent")
            wrapper = wrapper_class()
            return await wrapper.run(task, context)
        except Exception as e:
            logger.error(f"Failed to call service {service}: {e}")
            return {"error": str(e)}

    async def _call_brain_api(self, capability: str, task: Dict[str, Any], context: ExecutionContext) -> Any:
        """Call Rekindle Brain API"""
        try:
            from rekindle_brain.brain_client import BrainClient
            client = BrainClient()
            return await client.call(capability, task, context)
        except Exception as e:
            logger.error(f"Failed to call Brain API for {capability}: {e}")
            return {"error": str(e)}

    def _collect_node_inputs(self, node_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Collect input data for a node from its dependencies"""
        input_data = {}

        # Find incoming edges
        for edge in context.edges:
            if edge.to_node == node_id:
                from_node = context.nodes.get(edge.from_node)
                if from_node and from_node.result:
                    if edge.data_flow:
                        input_data[edge.data_flow] = from_node.result
                    else:
                        input_data[from_node.id] = from_node.result

        return input_data

    def _is_execution_complete(self, context: ExecutionContext) -> bool:
        """Check if graph execution is complete"""
        return all(node.status in ["completed", "failed"] for node in context.nodes.values())

    def _collect_execution_results(self, context: ExecutionContext) -> Dict[str, Any]:
        """Collect final execution results"""
        results = {
            "execution_id": context.execution_id,
            "status": context.status,
            "start_time": context.start_time.isoformat(),
            "duration_seconds": (datetime.now() - context.start_time).total_seconds(),
            "node_results": {}
        }

        for node_id, node in context.nodes.items():
            results["node_results"][node_id] = {
                "status": node.status,
                "result": node.result,
                "error": node.error,
                "execution_time": (node.completed_at - node.started_at).total_seconds() if node.completed_at and node.started_at else None
            }

        return results

    def _should_retry(self, node: TaskNode) -> bool:
        """Check if a failed node should be retried"""
        max_attempts = node.retry_policy.get("max_attempts", 3)
        return node.retry_count < max_attempts

    async def _store_execution_result(self, context: ExecutionContext, result: Dict[str, Any]):
        """Store execution result in Redis for monitoring and analysis"""
        key = f"are:execution:{context.execution_id}"
        await self.redis.setex(key, 86400, json.dumps(result))  # 24 hour TTL

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status from Redis"""
        key = f"are:execution:{execution_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def shutdown(self):
        """Gracefully shutdown the DAG engine"""
        await self.session.close()
        await self.redis.close()
        logger.info("ARE DAG Engine shut down")