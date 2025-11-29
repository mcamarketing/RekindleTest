"""
ARE REX State Agent Wrapper

Manages state machine execution and real-time state transitions
for the REX (Real-time Execution) system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class State(Enum):
    """REX execution states"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    COMPLETING = "completing"
    ERROR = "error"
    TERMINATED = "terminated"

class Transition(Enum):
    """State transitions"""
    START = "start"
    COMPLETE = "complete"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCEL = "cancel"
    RESET = "reset"

@dataclass
class StateContext:
    """Context for state execution"""
    state_id: str
    current_state: State
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class StateTransition:
    """Represents a state transition"""
    from_state: State
    to_state: State
    transition: Transition
    timestamp: datetime
    reason: str
    context: Dict[str, Any] = field(default_factory=dict)

class RexStateAgent:
    """ARE REX State Agent - Manages state machine execution"""

    def __init__(self):
        self.active_states: Dict[str, StateContext] = {}
        self.state_history: Dict[str, List[StateTransition]] = {}
        self.transition_handlers: Dict[State, Dict[Transition, callable]] = {}
        self.timeout_handlers: Dict[str, asyncio.Task] = {}

        # Initialize transition handlers
        self._setup_transition_handlers()

    def _setup_transition_handlers(self):
        """Setup state transition handlers"""
        # IDLE -> INITIALIZING
        self.transition_handlers[State.IDLE] = {
            Transition.START: self._handle_start
        }

        # INITIALIZING -> EXECUTING
        self.transition_handlers[State.INITIALIZING] = {
            Transition.COMPLETE: self._handle_initialization_complete,
            Transition.ERROR: self._handle_error
        }

        # EXECUTING -> MONITORING
        self.transition_handlers[State.EXECUTING] = {
            Transition.COMPLETE: self._handle_execution_complete,
            Transition.ERROR: self._handle_error,
            Transition.TIMEOUT: self._handle_timeout
        }

        # MONITORING -> COMPLETING
        self.transition_handlers[State.MONITORING] = {
            Transition.COMPLETE: self._handle_monitoring_complete,
            Transition.ERROR: self._handle_error
        }

        # COMPLETING -> IDLE
        self.transition_handlers[State.COMPLETING] = {
            Transition.COMPLETE: self._handle_completion_finalized
        }

        # ERROR -> IDLE (recovery)
        self.transition_handlers[State.ERROR] = {
            Transition.RESET: self._handle_reset
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'execute')
        state_id = input_data.get('state_id', f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        logger.info(f"REX State Agent executing action: {action} for state: {state_id}")

        try:
            if action == 'initialize':
                return await self._initialize_state(state_id, input_data)
            elif action == 'execute':
                return await self._execute_state(state_id, input_data)
            elif action == 'monitor':
                return await self._monitor_state(state_id, input_data)
            elif action == 'complete':
                return await self._complete_state(state_id, input_data)
            elif action == 'cancel':
                return await self._cancel_state(state_id, input_data)
            elif action == 'get_status':
                return self._get_state_status(state_id)
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"State execution failed: {e}")
            await self._transition_state(state_id, Transition.ERROR, str(e))
            raise

    async def _initialize_state(self, state_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new state context"""
        if state_id in self.active_states:
            raise ValueError(f"State {state_id} already exists")

        context = StateContext(
            state_id=state_id,
            current_state=State.IDLE,
            data=input_data.get('initial_data', {}),
            metadata=input_data.get('metadata', {})
        )

        self.active_states[state_id] = context
        self.state_history[state_id] = []

        logger.info(f"Initialized state: {state_id}")

        # Auto-transition to INITIALIZING
        await self._transition_state(state_id, Transition.START, "State initialization")

        return {
            "status": "initialized",
            "state_id": state_id,
            "current_state": context.current_state.value
        }

    async def _execute_state(self, state_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute state logic"""
        if state_id not in self.active_states:
            raise ValueError(f"State {state_id} not found")

        context = self.active_states[state_id]

        # Update context data
        context.data.update(input_data.get('execution_data', {}))
        context.updated_at = datetime.now()

        # Set timeout if specified
        timeout = input_data.get('timeout_seconds')
        if timeout:
            self._setup_timeout(state_id, timeout)

        # Transition to EXECUTING
        await self._transition_state(state_id, Transition.COMPLETE, "Starting execution")

        # Execute state logic (placeholder for actual REX logic)
        execution_result = await self._perform_state_execution(context)

        return {
            "status": "executing",
            "state_id": state_id,
            "execution_result": execution_result,
            "current_state": context.current_state.value
        }

    async def _monitor_state(self, state_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor state execution"""
        if state_id not in self.active_states:
            raise ValueError(f"State {state_id} not found")

        context = self.active_states[state_id]

        # Perform monitoring checks
        monitoring_result = await self._perform_monitoring_checks(context)

        return {
            "status": "monitoring",
            "state_id": state_id,
            "monitoring_result": monitoring_result,
            "current_state": context.current_state.value
        }

    async def _complete_state(self, state_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete state execution"""
        if state_id not in self.active_states:
            raise ValueError(f"State {state_id} not found")

        context = self.active_states[state_id]

        # Finalize execution
        completion_result = await self._finalize_execution(context)

        # Transition to COMPLETING
        await self._transition_state(state_id, Transition.COMPLETE, "Execution completed")

        return {
            "status": "completed",
            "state_id": state_id,
            "completion_result": completion_result,
            "current_state": context.current_state.value
        }

    async def _cancel_state(self, state_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel state execution"""
        if state_id not in self.active_states:
            raise ValueError(f"State {state_id} not found")

        context = self.active_states[state_id]

        # Cancel timeout if active
        if state_id in self.timeout_handlers:
            self.timeout_handlers[state_id].cancel()
            del self.timeout_handlers[state_id]

        # Transition to TERMINATED
        await self._transition_state(state_id, Transition.CANCEL, "Execution cancelled")

        # Cleanup
        del self.active_states[state_id]

        return {
            "status": "cancelled",
            "state_id": state_id
        }

    def _get_state_status(self, state_id: str) -> Dict[str, Any]:
        """Get current state status"""
        if state_id not in self.active_states:
            return {"status": "not_found", "state_id": state_id}

        context = self.active_states[state_id]
        history = self.state_history.get(state_id, [])

        return {
            "status": "active",
            "state_id": state_id,
            "current_state": context.current_state.value,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "data_keys": list(context.data.keys()),
            "transition_count": len(history),
            "last_transition": history[-1].__dict__ if history else None
        }

    async def _transition_state(self, state_id: str, transition: Transition, reason: str):
        """Handle state transition"""
        if state_id not in self.active_states:
            return

        context = self.active_states[state_id]
        from_state = context.current_state

        # Determine target state
        to_state = self._get_target_state(from_state, transition)
        if not to_state:
            logger.warning(f"Invalid transition {transition.value} from {from_state.value}")
            return

        # Create transition record
        transition_record = StateTransition(
            from_state=from_state,
            to_state=to_state,
            transition=transition,
            timestamp=datetime.now(),
            reason=reason
        )

        # Update context
        context.current_state = to_state
        context.updated_at = datetime.now()

        # Record transition
        if state_id not in self.state_history:
            self.state_history[state_id] = []
        self.state_history[state_id].append(transition_record)

        logger.info(f"State {state_id}: {from_state.value} -> {to_state.value} ({transition.value})")

        # Execute transition handler
        handler = self.transition_handlers.get(from_state, {}).get(transition)
        if handler:
            await handler(state_id, transition_record)

    def _get_target_state(self, from_state: State, transition: Transition) -> Optional[State]:
        """Get target state for transition"""
        transitions = {
            (State.IDLE, Transition.START): State.INITIALIZING,
            (State.INITIALIZING, Transition.COMPLETE): State.EXECUTING,
            (State.INITIALIZING, Transition.ERROR): State.ERROR,
            (State.EXECUTING, Transition.COMPLETE): State.MONITORING,
            (State.EXECUTING, Transition.ERROR): State.ERROR,
            (State.EXECUTING, Transition.TIMEOUT): State.ERROR,
            (State.MONITORING, Transition.COMPLETE): State.COMPLETING,
            (State.MONITORING, Transition.ERROR): State.ERROR,
            (State.COMPLETING, Transition.COMPLETE): State.IDLE,
            (State.ERROR, Transition.RESET): State.IDLE,
        }

        return transitions.get((from_state, transition))

    def _setup_timeout(self, state_id: str, timeout_seconds: int):
        """Setup execution timeout"""
        async def timeout_handler():
            await asyncio.sleep(timeout_seconds)
            if state_id in self.active_states:
                logger.warning(f"State {state_id} timed out")
                await self._transition_state(state_id, Transition.TIMEOUT, f"Timeout after {timeout_seconds}s")

        task = asyncio.create_task(timeout_handler())
        self.timeout_handlers[state_id] = task

    # Transition handlers
    async def _handle_start(self, state_id: str, transition: StateTransition):
        """Handle START transition"""
        # Initialize state resources
        pass

    async def _handle_initialization_complete(self, state_id: str, transition: StateTransition):
        """Handle initialization completion"""
        # Setup execution environment
        pass

    async def _handle_execution_complete(self, state_id: str, transition: StateTransition):
        """Handle execution completion"""
        # Begin monitoring phase
        pass

    async def _handle_monitoring_complete(self, state_id: str, transition: StateTransition):
        """Handle monitoring completion"""
        # Prepare for finalization
        pass

    async def _handle_completion_finalized(self, state_id: str, transition: StateTransition):
        """Handle final completion"""
        # Cleanup and reset
        if state_id in self.timeout_handlers:
            self.timeout_handlers[state_id].cancel()
            del self.timeout_handlers[state_id]

    async def _handle_error(self, state_id: str, transition: StateTransition):
        """Handle error transition"""
        # Log error and prepare recovery
        logger.error(f"State {state_id} entered error state: {transition.reason}")

    async def _handle_timeout(self, state_id: str, transition: StateTransition):
        """Handle timeout transition"""
        # Cleanup timed out execution
        pass

    async def _handle_reset(self, state_id: str, transition: StateTransition):
        """Handle reset transition"""
        # Reset state to clean state
        pass

    # Execution methods (placeholders for actual REX logic)
    async def _perform_state_execution(self, context: StateContext) -> Dict[str, Any]:
        """Perform actual state execution logic"""
        # Placeholder - integrate with actual REX execution engine
        await asyncio.sleep(0.1)  # Simulate work

        return {
            "execution_status": "success",
            "processed_data": len(context.data),
            "execution_time": 0.1
        }

    async def _perform_monitoring_checks(self, context: StateContext) -> Dict[str, Any]:
        """Perform monitoring checks"""
        # Placeholder - integrate with actual monitoring systems
        return {
            "health_status": "healthy",
            "performance_metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time": 120
            },
            "active_tasks": 3
        }

    async def _finalize_execution(self, context: StateContext) -> Dict[str, Any]:
        """Finalize state execution"""
        # Placeholder - cleanup and finalization logic
        return {
            "finalization_status": "success",
            "cleanup_completed": True,
            "resources_freed": 5
        }

    async def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of all active states"""
        return {
            "active_states": len(self.active_states),
            "states_by_status": self._count_states_by_status(),
            "total_transitions": sum(len(history) for history in self.state_history.values())
        }

    def _count_states_by_status(self) -> Dict[str, int]:
        """Count states by current status"""
        counts = {}
        for context in self.active_states.values():
            status = context.current_state.value
            counts[status] = counts.get(status, 0) + 1
        return counts