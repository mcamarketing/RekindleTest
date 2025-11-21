"""
Agent Communication Bus

Enables agents to communicate, share context, and coordinate.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events agents can broadcast."""
    LEAD_RESEARCHED = "lead_researched"
    MESSAGE_GENERATED = "message_generated"
    MESSAGE_SENT = "message_sent"
    REPLY_RECEIVED = "reply_received"
    MEETING_BOOKED = "meeting_booked"
    TRIGGER_DETECTED = "trigger_detected"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_COMPLETED = "campaign_completed"
    ERROR_OCCURRED = "error_occurred"
    CUSTOM = "custom"


@dataclass
class AgentEvent:
    """Event structure for agent communication."""
    event_type: EventType
    source_agent: str
    target_agent: Optional[str]  # None for broadcast
    data: Dict[str, Any]
    timestamp: datetime
    event_id: str


class AgentCommunicationBus:
    """
    Central communication bus for agents.
    
    Allows:
    - Event broadcasting (pub/sub)
    - Direct agent-to-agent requests
    - Shared context/memory
    - Agent coordination
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[AgentEvent] = []
        self.shared_context: Dict[str, Any] = {}
        self.max_history = 1000  # Keep last 1000 events
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type."""
        self.subscribers[event_type].append(callback)
        logger.debug(f"Agent subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        if callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
    
    def broadcast(self, event_type: EventType, source_agent: str, data: Dict[str, Any]):
        """
        Broadcast an event to all subscribers.
        
        Args:
            event_type: Type of event
            source_agent: Agent broadcasting the event
            data: Event data
        """
        event = AgentEvent(
            event_type=event_type,
            source_agent=source_agent,
            target_agent=None,
            data=data,
            timestamp=datetime.utcnow(),
            event_id=f"{event_type.value}_{datetime.utcnow().timestamp()}"
        )
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        callbacks = self.subscribers.get(event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
        
        logger.debug(f"Event {event_type.value} broadcast by {source_agent}")
    
    def request(
        self,
        from_agent: str,
        to_agent: str,
        request_type: str,
        data: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Direct agent-to-agent request.
        
        Args:
            from_agent: Requesting agent
            to_agent: Target agent
            request_type: Type of request
            data: Request data
            timeout: Request timeout in seconds
        
        Returns:
            Response from target agent or None if timeout
        """
        # In production, this would use a proper request/response mechanism
        # For now, we'll use events with a response callback
        
        request_event = AgentEvent(
            event_type=EventType.CUSTOM,
            source_agent=from_agent,
            target_agent=to_agent,
            data={
                "request_type": request_type,
                "request_data": data,
                "request_id": f"req_{datetime.utcnow().timestamp()}"
            },
            timestamp=datetime.utcnow(),
            event_id=f"request_{datetime.utcnow().timestamp()}"
        )
        
        logger.info(f"Request from {from_agent} to {to_agent}: {request_type}")
        
        # Store request
        self.event_history.append(request_event)
        
        # In production, would wait for response with timeout
        # For now, return None (would be implemented with async/await)
        return None
    
    def get_shared_context(self, key: str) -> Optional[Any]:
        """Get value from shared context."""
        return self.shared_context.get(key)
    
    def set_shared_context(self, key: str, value: Any):
        """Set value in shared context."""
        self.shared_context[key] = value
        logger.debug(f"Shared context updated: {key}")
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        source_agent: Optional[str] = None,
        limit: int = 100
    ) -> List[AgentEvent]:
        """Get event history with optional filters."""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source_agent:
            events = [e for e in events if e.source_agent == source_agent]
        
        return events[-limit:]
    
    def get_lead_context(self, lead_id: str) -> Dict[str, Any]:
        """Get all context for a specific lead."""
        context_key = f"lead_{lead_id}"
        return self.shared_context.get(context_key, {})
    
    def update_lead_context(self, lead_id: str, updates: Dict[str, Any]):
        """Update context for a specific lead."""
        context_key = f"lead_{lead_id}"
        current_context = self.shared_context.get(context_key, {})
        current_context.update(updates)
        self.shared_context[context_key] = current_context


# Global instance
_communication_bus: Optional[AgentCommunicationBus] = None


def get_communication_bus() -> AgentCommunicationBus:
    """Get or create global communication bus instance."""
    global _communication_bus
    if _communication_bus is None:
        _communication_bus = AgentCommunicationBus()
    return _communication_bus








