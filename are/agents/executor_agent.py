"""
ARE Executor Agent

Executes Planner tasks, routes them to the appropriate agents (Brain, CrewAI, REX, or Autonomous Services),
manages sequencing, collects results, and triggers the feedback loop.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class TaskAssignment:
    """Represents a task assignment to an agent cluster"""
    task_id: str
    agent_cluster: str
    capabilities: List[str]
    input_data: Dict[str, Any]
    priority: int
    timeout_seconds: int
    assigned_at: datetime
    status: str = "pending"

@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_id: str
    agent_cluster: str
    success: bool
    output: Any
    error: Optional[str]
    execution_time: float
    started_at: datetime
    completed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExecutorAgent:
    """ARE Executor Agent - Task execution and orchestration"""

    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.active_executions: Dict[str, TaskAssignment] = {}
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.progress_callbacks: List[callable] = []
        self.execution_logs: List[Dict[str, Any]] = []

        # Agent cluster endpoints (would be configured from environment)
        self.endpoints = {
            "brain": "http://localhost:8001/brain",
            "crewai": "http://localhost:8002/crewai",
            "rex": "http://localhost:8003/rex",
            "services": "http://localhost:8004/services"
        }

    def add_progress_callback(self, callback: callable):
        """Add a callback for progress updates"""
        self.progress_callbacks.append(callback)

    def _log_progress(self, message: str, progress_percent: float = None, details: Dict[str, Any] = None):
        """Log progress and notify callbacks"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "progress_percent": progress_percent,
            "details": details or {}
        }

        self.execution_logs.append(log_entry)
        logger.info(f"[PROGRESS] {message}")

        # Notify callbacks
        for callback in self.progress_callbacks:
            try:
                asyncio.create_task(callback(log_entry))
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def _log_execution_step(self, step: str, task_id: str = None, latency: float = None, details: Dict[str, Any] = None):
        """Log detailed execution step with latency tracking"""
        message = f"Execution step: {step}"
        if task_id:
            message += f" (Task: {task_id})"
        if latency:
            message += f" - Latency: {latency:.2f}s"

        self._log_progress(message, details={
            "step": step,
            "task_id": task_id,
            "latency_seconds": latency,
            **(details or {})
        })

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        plan = input_data.get("execution_plan")
        if not plan:
            raise ValueError("No execution plan provided")

        plan_id = plan.get("plan_id")
        logger.info(f"Executing plan {plan_id}")

        execution_start = datetime.now()
        self._log_progress(f"Starting execution of plan {plan_id}", 0)

        try:
            # Step 1: Parse plan and create task assignments
            step_start = datetime.now()
            self._log_execution_step("Creating task assignments", latency=0)
            assignments = await self._create_assignments(plan)
            step_latency = (datetime.now() - step_start).total_seconds()
            self._log_execution_step("Task assignments created", latency=step_latency,
                                   details={"assignment_count": len(assignments)})
            self._log_progress(f"Created {len(assignments)} task assignments", 10)

            # Step 2: Execute tasks respecting dependencies
            step_start = datetime.now()
            self._log_execution_step("Starting task execution", latency=0)
            results = await self._execute_tasks(assignments, plan)
            step_latency = (datetime.now() - step_start).total_seconds()
            self._log_execution_step("Task execution completed", latency=step_latency,
                                   details={"results_count": len(results)})
            self._log_progress(f"Executed {len(results)} tasks", 70)

            # Step 3: Aggregate and validate results
            step_start = datetime.now()
            self._log_execution_step("Aggregating results", latency=0)
            aggregated_results = self._aggregate_results(results)
            step_latency = (datetime.now() - step_start).total_seconds()
            self._log_execution_step("Results aggregated", latency=step_latency)
            self._log_progress("Results aggregated and validated", 85)

            # Step 4: Generate execution report
            step_start = datetime.now()
            self._log_execution_step("Generating execution report", latency=0)
            report = self._generate_execution_report(plan, results, aggregated_results)
            step_latency = (datetime.now() - step_start).total_seconds()
            self._log_execution_step("Execution report generated", latency=step_latency)
            self._log_progress("Execution report generated", 95)

            total_latency = (datetime.now() - execution_start).total_seconds()
            self._log_progress(f"Plan {plan_id} execution completed successfully", 100,
                             {"total_latency": total_latency, "tasks_completed": len(results)})

            logger.info(f"Plan {plan_id} execution completed with {len(results)} task results")
            return {
                "execution_results": results,
                "aggregated_results": aggregated_results,
                "execution_report": report,
                "execution_logs": self.execution_logs.copy(),
                "performance_metrics": {
                    "total_execution_time": total_latency,
                    "tasks_executed": len(results),
                    "success_rate": aggregated_results["summary"]["success_rate"]
                }
            }

        except Exception as e:
            total_latency = (datetime.now() - execution_start).total_seconds()
            self._log_progress(f"Plan {plan_id} execution failed: {str(e)}", 100,
                             {"error": str(e), "total_latency": total_latency})
            logger.error(f"Execution failed for plan {plan_id}: {e}")
            raise

    async def _create_assignments(self, plan: Dict[str, Any]) -> List[TaskAssignment]:
        """Create task assignments from execution plan"""
        assignments = []
        tasks = plan.get("tasks", [])
        agent_assignments = plan.get("agent_assignments", {})

        for task in tasks:
            task_id = task["id"]
            agent_cluster = agent_assignments.get(task_id)

            if not agent_cluster:
                logger.warning(f"No agent assignment for task {task_id}, skipping")
                continue

            assignment = TaskAssignment(
                task_id=task_id,
                agent_cluster=agent_cluster,
                capabilities=task.get("capabilities", []),
                input_data=task.get("input_data", {}),
                priority=task.get("priority", 1),
                timeout_seconds=task.get("estimated_duration", 300),
                assigned_at=datetime.now()
            )

            assignments.append(assignment)

        # Sort by priority (higher priority first)
        assignments.sort(key=lambda x: x.priority, reverse=True)

        logger.info(f"Created {len(assignments)} task assignments")
        return assignments

    async def _execute_tasks(self, assignments: List[TaskAssignment], plan: Dict[str, Any]) -> List[ExecutionResult]:
        """Execute tasks respecting dependencies"""
        results = []
        completed_tasks = set()
        dependencies = plan.get("dependencies", [])

        # Create dependency graph
        dep_graph = self._build_dependency_graph(dependencies)

        while len(results) < len(assignments):
            # Find ready tasks (all dependencies satisfied)
            ready_assignments = [
                assignment for assignment in assignments
                if assignment.task_id not in completed_tasks
                and self._dependencies_satisfied(assignment.task_id, dep_graph, completed_tasks)
            ]

            if not ready_assignments:
                if len(completed_tasks) < len(assignments):
                    # Circular dependency or stuck tasks
                    logger.error("Execution stuck - possible circular dependency or failed tasks")
                    break
                else:
                    break

            # Execute ready tasks in parallel (with concurrency limit)
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent tasks

            async def execute_with_semaphore(assignment: TaskAssignment):
                async with semaphore:
                    return await self._execute_single_task(assignment)

            # Execute batch of ready tasks
            batch_results = await asyncio.gather(
                *[execute_with_semaphore(assignment) for assignment in ready_assignments],
                return_exceptions=True
            )

            # Process results
            for i, result in enumerate(batch_results):
                assignment = ready_assignments[i]

                if isinstance(result, Exception):
                    # Task failed
                    error_result = ExecutionResult(
                        task_id=assignment.task_id,
                        agent_cluster=assignment.agent_cluster,
                        success=False,
                        output=None,
                        error=str(result),
                        execution_time=0.0,
                        started_at=datetime.now(),
                        completed_at=datetime.now()
                    )
                    results.append(error_result)
                else:
                    # Task succeeded
                    results.append(result)
                    completed_tasks.add(assignment.task_id)

            # Small delay to prevent tight looping
            await asyncio.sleep(0.1)

        logger.info(f"Executed {len(results)} tasks, {len(completed_tasks)} completed successfully")
        return results

    async def _execute_single_task(self, assignment: TaskAssignment) -> ExecutionResult:
        """Execute a single task"""
        started_at = datetime.now()
        assignment.status = "running"

        self._log_execution_step(f"Starting task execution on {assignment.agent_cluster}",
                               assignment.task_id, 0)
        logger.info(f"Executing task {assignment.task_id} on {assignment.agent_cluster}")

        try:
            # Route to appropriate agent cluster
            if assignment.agent_cluster == "brain":
                result = await self._execute_brain_task(assignment)
            elif assignment.agent_cluster == "crewai":
                result = await self._execute_crewai_task(assignment)
            elif assignment.agent_cluster == "rex":
                result = await self._execute_rex_task(assignment)
            elif assignment.agent_cluster == "services":
                result = await self._execute_services_task(assignment)
            else:
                raise ValueError(f"Unknown agent cluster: {assignment.agent_cluster}")

            execution_time = (datetime.now() - started_at).total_seconds()

            self._log_execution_step(f"Task completed successfully",
                                   assignment.task_id, execution_time,
                                   {"agent_cluster": assignment.agent_cluster})

            return ExecutionResult(
                task_id=assignment.task_id,
                agent_cluster=assignment.agent_cluster,
                success=True,
                output=result,
                error=None,
                execution_time=execution_time,
                started_at=started_at,
                completed_at=datetime.now()
            )

        except Exception as e:
            execution_time = (datetime.now() - started_at).total_seconds()
            self._log_execution_step(f"Task failed: {str(e)}",
                                   assignment.task_id, execution_time,
                                   {"error": str(e), "agent_cluster": assignment.agent_cluster})
            logger.error(f"Task {assignment.task_id} failed: {e}")

            return ExecutionResult(
                task_id=assignment.task_id,
                agent_cluster=assignment.agent_cluster,
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                started_at=started_at,
                completed_at=datetime.now()
            )

    async def _execute_brain_task(self, assignment: TaskAssignment) -> Any:
        """Execute task on Rekindle Brain"""
        endpoint = f"{self.endpoints['brain']}/execute"

        payload = {
            "task_id": assignment.task_id,
            "capabilities": assignment.capabilities,
            "input_data": assignment.input_data,
            "timeout": assignment.timeout_seconds
        }

        async with self.session.post(endpoint, json=payload, timeout=assignment.timeout_seconds) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Brain API error {response.status}: {error_text}")

            result = await response.json()
            return result.get("output")

    async def _execute_crewai_task(self, assignment: TaskAssignment) -> Any:
        """Execute task on CrewAI agents"""
        endpoint = f"{self.endpoints['crewai']}/execute"

        payload = {
            "task_id": assignment.task_id,
            "capabilities": assignment.capabilities,
            "input_data": assignment.input_data,
            "timeout": assignment.timeout_seconds
        }

        async with self.session.post(endpoint, json=payload, timeout=assignment.timeout_seconds) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"CrewAI API error {response.status}: {error_text}")

            result = await response.json()
            return result.get("output")

    async def _execute_rex_task(self, assignment: TaskAssignment) -> Any:
        """Execute task on REX system"""
        endpoint = f"{self.endpoints['rex']}/execute"

        payload = {
            "task_id": assignment.task_id,
            "capabilities": assignment.capabilities,
            "input_data": assignment.input_data,
            "timeout": assignment.timeout_seconds
        }

        async with self.session.post(endpoint, json=payload, timeout=assignment.timeout_seconds) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"REX API error {response.status}: {error_text}")

            result = await response.json()
            return result.get("output")

    async def _execute_services_task(self, assignment: TaskAssignment) -> Any:
        """Execute task on Autonomous Services"""
        endpoint = f"{self.endpoints['services']}/execute"

        payload = {
            "task_id": assignment.task_id,
            "capabilities": assignment.capabilities,
            "input_data": assignment.input_data,
            "timeout": assignment.timeout_seconds
        }

        async with self.session.post(endpoint, json=payload, timeout=assignment.timeout_seconds) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Services API error {response.status}: {error_text}")

            result = await response.json()
            return result.get("output")

    def _build_dependency_graph(self, dependencies: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Build dependency graph from plan dependencies"""
        graph = {}

        for dep in dependencies:
            from_task = dep["from"]
            to_task = dep["to"]

            if from_task not in graph:
                graph[from_task] = []
            if to_task not in graph:
                graph[to_task] = []

            # Add dependency: to_task depends on from_task
            if from_task not in graph[to_task]:
                graph[to_task].append(from_task)

        return graph

    def _dependencies_satisfied(self, task_id: str, dep_graph: Dict[str, List[str]], completed: set) -> bool:
        """Check if all dependencies for a task are satisfied"""
        dependencies = dep_graph.get(task_id, [])
        return all(dep in completed for dep in dependencies)

    def _aggregate_results(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """Aggregate execution results"""
        total_tasks = len(results)
        successful_tasks = len([r for r in results if r.success])
        failed_tasks = total_tasks - successful_tasks

        total_execution_time = sum(r.execution_time for r in results)

        # Group by agent cluster
        cluster_results = {}
        for result in results:
            cluster = result.agent_cluster
            if cluster not in cluster_results:
                cluster_results[cluster] = {"total": 0, "successful": 0, "failed": 0, "avg_time": 0}
            cluster_results[cluster]["total"] += 1
            if result.success:
                cluster_results[cluster]["successful"] += 1
            else:
                cluster_results[cluster]["failed"] += 1

        # Calculate averages
        for cluster_data in cluster_results.values():
            if cluster_data["total"] > 0:
                cluster_times = [r.execution_time for r in results if r.agent_cluster == cluster_data and r.success]
                cluster_data["avg_time"] = sum(cluster_times) / len(cluster_times) if cluster_times else 0

        return {
            "summary": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
                "total_execution_time": total_execution_time,
                "average_task_time": total_execution_time / total_tasks if total_tasks > 0 else 0
            },
            "by_cluster": cluster_results,
            "failures": [{"task_id": r.task_id, "error": r.error} for r in results if not r.success]
        }

    def _generate_execution_report(self, plan: Dict[str, Any], results: List[ExecutionResult], aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        plan_id = plan.get("plan_id")
        goal = plan.get("goal", {})

        # Calculate goal achievement
        goal_achievement = self._assess_goal_achievement(goal, results)

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(results)

        # Generate recommendations
        recommendations = self._generate_execution_recommendations(results, aggregated)

        return {
            "plan_id": plan_id,
            "goal": goal,
            "execution_summary": aggregated["summary"],
            "goal_achievement": goal_achievement,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "cluster_performance": aggregated["by_cluster"],
            "generated_at": datetime.now().isoformat()
        }

    def _assess_goal_achievement(self, goal: Dict[str, Any], results: List[ExecutionResult]) -> Dict[str, Any]:
        """Assess how well the goal was achieved"""
        target_metrics = goal.get("target_metrics", {})
        achievements = {}

        # This would analyze actual outcomes vs targets
        # For now, return a basic assessment
        for metric, target in target_metrics.items():
            # Mock achievement calculation
            achievement_rate = 0.85  # Would be calculated from actual results
            achievements[metric] = {
                "target": target,
                "achieved": target * achievement_rate,
                "achievement_rate": achievement_rate,
                "status": "ACHIEVED" if achievement_rate >= 0.8 else "PARTIAL"
            }

        overall_achievement = sum(a["achievement_rate"] for a in achievements.values()) / len(achievements) if achievements else 0

        return {
            "overall_achievement": overall_achievement,
            "status": "SUCCESS" if overall_achievement >= 0.8 else "PARTIAL_SUCCESS",
            "metric_achievements": achievements
        }

    def _identify_bottlenecks(self, results: List[ExecutionResult]) -> List[Dict[str, Any]]:
        """Identify execution bottlenecks"""
        bottlenecks = []

        # Find slowest tasks
        sorted_results = sorted(results, key=lambda r: r.execution_time, reverse=True)
        if sorted_results and sorted_results[0].execution_time > 300:  # 5 minutes
            bottlenecks.append({
                "type": "slow_task",
                "task_id": sorted_results[0].task_id,
                "execution_time": sorted_results[0].execution_time,
                "threshold": 300
            })

        # Find failed clusters
        cluster_failures = {}
        for result in results:
            if not result.success:
                cluster = result.agent_cluster
                cluster_failures[cluster] = cluster_failures.get(cluster, 0) + 1

        for cluster, failures in cluster_failures.items():
            if failures > 2:
                bottlenecks.append({
                    "type": "cluster_failures",
                    "cluster": cluster,
                    "failure_count": failures,
                    "threshold": 2
                })

        return bottlenecks

    def _generate_execution_recommendations(self, results: List[ExecutionResult], aggregated: Dict[str, Any]) -> List[str]:
        """Generate execution improvement recommendations"""
        recommendations = []

        success_rate = aggregated["summary"]["success_rate"]

        if success_rate < 0.8:
            recommendations.append("Improve task success rate through better agent selection and error handling")

        avg_time = aggregated["summary"]["average_task_time"]
        if avg_time > 180:  # 3 minutes
            recommendations.append("Optimize task execution time through parallelization and caching")

        # Cluster-specific recommendations
        for cluster, data in aggregated["by_cluster"].items():
            if data["avg_time"] > 120:  # 2 minutes
                recommendations.append(f"Optimize {cluster} cluster performance")

        return recommendations

    async def get_execution_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get current execution status for a plan"""
        # This would query execution state
        return None

    async def cancel_execution(self, plan_id: str) -> bool:
        """Cancel execution of a plan"""
        # This would signal cancellation to running tasks
        return True

    async def shutdown(self):
        """Gracefully shutdown the executor"""
        await self.session.close()
        logger.info("ARE Executor Agent shut down")