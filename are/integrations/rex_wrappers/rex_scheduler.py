"""
ARE REX Scheduler Agent Wrapper

Manages task scheduling, resource allocation, and execution timing
for the REX (Real-time Execution) system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import heapq
import uuid

logger = logging.getLogger(__name__)

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ScheduleStatus(Enum):
    """Scheduling status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(order=True)
class ScheduledTask:
    """A task scheduled for execution"""
    priority: int  # For heap ordering (negative for max-heap)
    task_id: str = field(compare=False)
    task_name: str = field(compare=False)
    agent_type: str = field(compare=False)
    execution_time: datetime = field(compare=False)
    estimated_duration: int = field(compare=False)  # seconds
    dependencies: List[str] = field(compare=False, default_factory=list)
    resources_required: Dict[str, Any] = field(compare=False, default_factory=dict)
    status: ScheduleStatus = field(compare=False, default=ScheduleStatus.PENDING)
    created_at: datetime = field(compare=False, default_factory=datetime.now)
    started_at: Optional[datetime] = field(compare=False, default=None)
    completed_at: Optional[datetime] = field(compare=False, default=None)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)

    def __post_init__(self):
        # Ensure priority is negative for max-heap behavior
        self.priority = -self.priority

@dataclass
class ResourcePool:
    """Represents a pool of resources"""
    resource_type: str
    total_capacity: int
    available_capacity: int
    allocated_tasks: Dict[str, int] = field(default_factory=dict)  # task_id -> amount

    def allocate(self, task_id: str, amount: int) -> bool:
        """Allocate resources for a task"""
        if self.available_capacity >= amount:
            self.available_capacity -= amount
            self.allocated_tasks[task_id] = amount
            return True
        return False

    def release(self, task_id: str):
        """Release resources allocated to a task"""
        if task_id in self.allocated_tasks:
            amount = self.allocated_tasks[task_id]
            self.available_capacity += amount
            del self.allocated_tasks[task_id]

class RexSchedulerAgent:
    """ARE REX Scheduler Agent - Task scheduling and resource management"""

    def __init__(self):
        self.task_queue: List[ScheduledTask] = []  # Priority queue
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.resource_pools: Dict[str, ResourcePool] = {}

        # Setup default resource pools
        self._setup_resource_pools()

        # Scheduling parameters
        self.max_concurrent_tasks = 5
        self.scheduling_interval = 30  # seconds

        # Background scheduling task
        self.scheduling_task = None
        self.is_running = False

    def _setup_resource_pools(self):
        """Setup default resource pools"""
        self.resource_pools = {
            "cpu": ResourcePool("cpu", 100, 100),  # Percentage
            "memory": ResourcePool("memory", 80, 80),  # Percentage
            "api_calls": ResourcePool("api_calls", 1000, 1000),  # Per hour
            "llm_tokens": ResourcePool("llm_tokens", 100000, 100000),  # Tokens
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'schedule')

        logger.info(f"REX Scheduler Agent executing action: {action}")

        try:
            if action == 'schedule_task':
                return await self._schedule_task(input_data)
            elif action == 'cancel_task':
                return await self._cancel_task(input_data)
            elif action == 'get_schedule':
                return self._get_schedule()
            elif action == 'start_scheduler':
                return await self._start_scheduler()
            elif action == 'stop_scheduler':
                return await self._stop_scheduler()
            elif action == 'get_resource_status':
                return self._get_resource_status()
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Scheduler execution failed: {e}")
            raise

    async def _schedule_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new task"""
        task_id = input_data.get('task_id', str(uuid.uuid4()))
        task_name = input_data.get('task_name', 'Unnamed Task')
        agent_type = input_data.get('agent_type', 'brain')
        priority = Priority[input_data.get('priority', 'MEDIUM').upper()]
        execution_time = input_data.get('execution_time')

        if execution_time and isinstance(execution_time, str):
            execution_time = datetime.fromisoformat(execution_time.replace('Z', '+00:00'))

        estimated_duration = input_data.get('estimated_duration', 300)
        dependencies = input_data.get('dependencies', [])
        resources_required = input_data.get('resources_required', {})

        # Check if dependencies are satisfied
        if not self._check_dependencies(dependencies):
            return {
                "status": "deferred",
                "task_id": task_id,
                "reason": "Dependencies not satisfied"
            }

        task = ScheduledTask(
            task_id=task_id,
            task_name=task_name,
            agent_type=agent_type,
            priority=priority.value,
            execution_time=execution_time or datetime.now(),
            estimated_duration=estimated_duration,
            dependencies=dependencies,
            resources_required=resources_required
        )

        # Add to priority queue
        heapq.heappush(self.task_queue, task)

        logger.info(f"Scheduled task: {task_id} ({task_name}) for {task.execution_time}")

        return {
            "status": "scheduled",
            "task_id": task_id,
            "execution_time": task.execution_time.isoformat(),
            "priority": priority.value
        }

    async def _cancel_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a scheduled or running task"""
        task_id = input_data.get('task_id')

        if not task_id:
            raise ValueError("task_id is required")

        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = ScheduleStatus.CANCELLED
            task.completed_at = datetime.now()
            self._release_task_resources(task)
            del self.active_tasks[task_id]
            self.completed_tasks[task_id] = task

            logger.info(f"Cancelled active task: {task_id}")
            return {"status": "cancelled", "task_id": task_id}

        # Check queue
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.status = ScheduleStatus.CANCELLED
                self.completed_tasks[task_id] = task
                del self.task_queue[i]
                heapq.heapify(self.task_queue)

                logger.info(f"Cancelled queued task: {task_id}")
                return {"status": "cancelled", "task_id": task_id}

        return {"status": "not_found", "task_id": task_id}

    def _get_schedule(self) -> Dict[str, Any]:
        """Get current schedule status"""
        return {
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "next_task": self.task_queue[0].__dict__ if self.task_queue else None,
            "scheduler_running": self.is_running
        }

    async def _start_scheduler(self) -> Dict[str, Any]:
        """Start the background scheduler"""
        if self.is_running:
            return {"status": "already_running"}

        self.is_running = True
        self.scheduling_task = asyncio.create_task(self._scheduling_loop())

        logger.info("Scheduler started")
        return {"status": "started"}

    async def _stop_scheduler(self) -> Dict[str, Any]:
        """Stop the background scheduler"""
        if not self.is_running:
            return {"status": "not_running"}

        self.is_running = False
        if self.scheduling_task:
            self.scheduling_task.cancel()
            try:
                await self.scheduling_task
            except asyncio.CancelledError:
                pass

        logger.info("Scheduler stopped")
        return {"status": "stopped"}

    def _get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        return {
            resource_type: {
                "total": pool.total_capacity,
                "available": pool.available_capacity,
                "utilization": ((pool.total_capacity - pool.available_capacity) / pool.total_capacity) * 100,
                "allocated_tasks": len(pool.allocated_tasks)
            }
            for resource_type, pool in self.resource_pools.items()
        }

    async def _scheduling_loop(self):
        """Background scheduling loop"""
        while self.is_running:
            try:
                await self._process_scheduled_tasks()
                await asyncio.sleep(self.scheduling_interval)
            except Exception as e:
                logger.error(f"Scheduling loop error: {e}")
                await asyncio.sleep(self.scheduling_interval)

    async def _process_scheduled_tasks(self):
        """Process tasks that are ready for execution"""
        now = datetime.now()

        # Process tasks in priority order
        temp_queue = []
        while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
            task = heapq.heappop()

            # Check if task is ready
            if task.execution_time <= now and self._check_dependencies(task.dependencies):
                if self._allocate_resources(task):
                    tasks_to_start.append(task)
                else:
                    # Put back in queue if resources not available
                    temp_queue.append(task)
            else:
                temp_queue.append(task)

        # Restore queue
        for task in temp_queue:
            heapq.heappush(self.task_queue, task)

        # Start ready tasks
        for task in tasks_to_start:
            await self._start_task(task)

    async def _start_task(self, task: ScheduledTask):
        """Start execution of a task"""
        task.status = ScheduleStatus.RUNNING
        task.started_at = datetime.now()

        self.active_tasks[task.task_id] = task

        logger.info(f"Started task: {task.task_id} ({task.task_name})")

        # Simulate task execution (in real implementation, this would trigger actual execution)
        asyncio.create_task(self._monitor_task_completion(task))

    async def _monitor_task_completion(self, task: ScheduledTask):
        """Monitor task completion"""
        try:
            # Wait for estimated duration (in real implementation, monitor actual completion)
            await asyncio.sleep(task.estimated_duration)

            # Mark as completed
            task.status = ScheduleStatus.COMPLETED
            task.completed_at = datetime.now()

            # Release resources
            self._release_task_resources(task)

            # Move to completed
            self.completed_tasks[task.task_id] = task
            del self.active_tasks[task.task_id]

            logger.info(f"Completed task: {task.task_id}")

        except Exception as e:
            logger.error(f"Task monitoring failed for {task.task_id}: {e}")
            task.status = ScheduleStatus.FAILED
            task.completed_at = datetime.now()

            # Handle retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = ScheduleStatus.PENDING
                task.execution_time = datetime.now() + timedelta(seconds=60 * task.retry_count)  # Exponential backoff

                # Put back in queue
                heapq.heappush(self.task_queue, task)
                logger.info(f"Retrying task: {task.task_id} (attempt {task.retry_count})")
            else:
                # Release resources and mark as failed
                self._release_task_resources(task)
                self.completed_tasks[task.task_id] = task
                del self.active_tasks[task.task_id]
                logger.error(f"Task failed permanently: {task.task_id}")

    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_task_id in dependencies:
            if dep_task_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_task_id].status != ScheduleStatus.COMPLETED:
                return False
        return True

    def _allocate_resources(self, task: ScheduledTask) -> bool:
        """Allocate resources for a task"""
        required = task.resources_required

        # Check if all required resources are available
        allocations = {}
        for resource_type, amount in required.items():
            if resource_type not in self.resource_pools:
                logger.warning(f"Unknown resource type: {resource_type}")
                continue

            pool = self.resource_pools[resource_type]
            if not pool.allocate(task.task_id, amount):
                # Allocation failed, release any already allocated
                for rt, amt in allocations.items():
                    self.resource_pools[rt].release(task.task_id)
                return False

            allocations[resource_type] = amount

        return True

    def _release_task_resources(self, task: ScheduledTask):
        """Release resources allocated to a task"""
        for resource_type in task.resources_required.keys():
            if resource_type in self.resource_pools:
                self.resource_pools[resource_type].release(task.task_id)

    async def update_task_priority(self, task_id: str, new_priority: Priority) -> Dict[str, Any]:
        """Update the priority of a scheduled task"""
        # Find task in queue
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.priority = -new_priority.value  # Update priority
                heapq.heapify(self.task_queue)  # Re-heapify

                logger.info(f"Updated priority for task {task_id} to {new_priority.value}")
                return {"status": "updated", "task_id": task_id, "new_priority": new_priority.value}

        return {"status": "not_found", "task_id": task_id}

    async def reschedule_task(self, task_id: str, new_execution_time: datetime) -> Dict[str, Any]:
        """Reschedule a task for a different time"""
        # Find task in queue
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.execution_time = new_execution_time
                heapq.heapify(self.task_queue)  # Re-heapify

                logger.info(f"Rescheduled task {task_id} to {new_execution_time}")
                return {
                    "status": "rescheduled",
                    "task_id": task_id,
                    "new_execution_time": new_execution_time.isoformat()
                }

        return {"status": "not_found", "task_id": task_id}

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        total_tasks = len(self.task_queue) + len(self.active_tasks) + len(self.completed_tasks)

        if not self.completed_tasks:
            avg_completion_time = 0
        else:
            completion_times = [
                (task.completed_at - task.started_at).total_seconds()
                for task in self.completed_tasks.values()
                if task.started_at and task.completed_at
            ]
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        return {
            "total_tasks": total_tasks,
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "average_completion_time": avg_completion_time,
            "scheduler_running": self.is_running,
            "max_concurrent_tasks": self.max_concurrent_tasks
        }