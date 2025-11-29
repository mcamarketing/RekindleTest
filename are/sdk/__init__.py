"""
ARE SDK - Autonomous Revenue Engine Software Development Kit

This SDK provides programmatic access to all ARE agents and services,
enabling any part of the Rekindle platform to leverage AI capabilities.
"""

from .client import AREClient
from .agents import (
    PlannerAgent,
    ExecutorAgent,
    CriticAgent,
    GuardrailAgent,
    RagServiceAgent,
    SocialListeningAgent
)
from .types import (
    Goal,
    Task,
    ExecutionPlan,
    AgentResponse,
    AREConfig,
    AgentType
)
from .exceptions import (
    AREError,
    AgentUnavailableError,
    ValidationError,
    TimeoutError
)

__version__ = "1.0.0"
__all__ = [
    "AREClient",
    "PlannerAgent", "ExecutorAgent", "CriticAgent",
    "GuardrailAgent", "RagServiceAgent", "SocialListeningAgent",
    "Goal", "Task", "ExecutionPlan", "AgentResponse",
    "AREConfig", "AgentType",
    "AREError", "AgentUnavailableError", "ValidationError", "TimeoutError"
]