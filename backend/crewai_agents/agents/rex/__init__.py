"""
REX - Primary Orchestrator and User-Facing Command Agent

REX is the main orchestrator that:
- Listens to user commands via chat widget
- Automatically delegates tasks to the correct internal agents
- Executes workflows fully and autonomously
- Uses adaptive reasoning (GPT-5.1-instant for quick, GPT-5.1-thinking for complex)
- Communicates in a confident, intelligent, conversational, yet precise style
"""

from .rex import RexOrchestrator
from .command_parser import CommandParser
from .action_executor import ActionExecutor
from .result_aggregator import ResultAggregator
from .defaults import IntelligentDefaults
from .permissions import PermissionsManager
from .sentience_engine import SentienceEngine
from .response_wrapper import ResponseWrapper

__all__ = [
    "RexOrchestrator",
    "CommandParser",
    "ActionExecutor",
    "ResultAggregator",
    "IntelligentDefaults",
    "PermissionsManager",
    "SentienceEngine",
    "ResponseWrapper"
]

