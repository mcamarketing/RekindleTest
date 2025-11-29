"""
ARE SDK Types and Data Models

Core type definitions for the ARE SDK, including goals, tasks, responses,
and configuration objects.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentType(Enum):
    """Types of agents available in ARE"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    GUARDRAIL = "guardrail"
    RAG_SERVICE = "rag_service"
    SOCIAL_LISTENING = "social_listening"
    CREWAI = "crewai"
    REX = "rex"
    BRAIN = "brain"


class GoalType(Enum):
    """Types of goals that can be processed"""
    REVIVE_PIPELINE = "REVIVE_PIPELINE"
    INCREASE_MEETINGS = "INCREASE_MEETINGS"
    OPTIMIZE_SEQUENCE = "OPTIMIZE_SEQUENCE"
    BUILD_ICP = "BUILD_ICP"
    GENERAL = "GENERAL"


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AREConfig:
    """Configuration for ARE SDK client"""
    base_url: str = "http://localhost:8000"
    websocket_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    enable_streaming: bool = True
    org_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class Goal:
    """Represents a business goal to be processed by ARE"""
    goal_type: GoalType
    description: str
    target_metrics: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    org_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "goal_type": self.goal_type.value,
            "description": self.description,
            "target_metrics": self.target_metrics,
            "constraints": self.constraints,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority.value,
            "org_id": self.org_id,
            "user_id": self.user_id,
            "metadata": self.metadata
        }


@dataclass
class Task:
    """Represents a single executable task"""
    id: str
    description: str
    agent_type: AgentType
    capabilities: List[str]
    input_data: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    estimated_duration: int = 300  # seconds
    dependencies: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "id": self.id,
            "description": self.description,
            "agent_type": self.agent_type.value,
            "capabilities": self.capabilities,
            "input_data": self.input_data,
            "priority": self.priority.value,
            "estimated_duration": self.estimated_duration,
            "dependencies": self.dependencies,
            "success_criteria": self.success_criteria,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan for a goal"""
    plan_id: str
    goal: Goal
    tasks: List[Task]
    dependencies: List[Dict[str, str]]  # [{"from": "task1", "to": "task2"}]
    agent_assignments: Dict[str, str]  # task_id -> agent_cluster
    risk_assessment: Dict[str, Any]
    estimated_completion: datetime
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "plan_id": self.plan_id,
            "goal": self.goal.to_dict(),
            "tasks": [task.to_dict() for task in self.tasks],
            "dependencies": self.dependencies,
            "agent_assignments": self.agent_assignments,
            "risk_assessment": self.risk_assessment,
            "estimated_completion": self.estimated_completion.isoformat(),
            "created_at": self.created_at.isoformat()
        }


@dataclass
class AgentResponse:
    """Response from an agent execution"""
    agent_type: AgentType
    task_id: Optional[str]
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "agent_type": self.agent_type.value,
            "task_id": self.task_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AREEvent:
    """Event emitted by ARE system"""
    event_type: str
    event_id: str
    source: str  # agent or component name
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event streaming"""
        return {
            "event_type": self.event_type,
            "event_id": self.event_id,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    agent_type: AgentType
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    average_response_time: float = 0.0
    last_request_at: Optional[datetime] = None
    error_rate: float = 0.0
    uptime_percentage: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for monitoring"""
        return {
            "agent_type": self.agent_type.value,
            "requests_total": self.requests_total,
            "requests_successful": self.requests_successful,
            "requests_failed": self.requests_failed,
            "average_response_time": self.average_response_time,
            "last_request_at": self.last_request_at.isoformat() if self.last_request_at else None,
            "error_rate": self.error_rate,
            "uptime_percentage": self.uptime_percentage
        }


# Type aliases for common use cases
AgentRequest = Dict[str, Any]
AgentResult = Dict[str, Any]
ValidationResult = Dict[str, Union[bool, List[str]]]
StreamCallback = callable  # Callback function for streaming responses