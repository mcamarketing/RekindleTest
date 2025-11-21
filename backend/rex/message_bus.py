"""
REX Message Bus
Redis Pub/Sub for inter-agent communication and event broadcasting
"""

import json
import logging
import uuid
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Message structure for Rex message bus"""
    id: str
    type: str  # e.g., 'mission.assigned', 'mission.completed', 'error.escalation'
    timestamp: str
    sender: str  # 'rex' | crew_name | agent_name
    recipient: str  # 'rex' | crew_name | agent_name | 'broadcast'

    # Payload
    mission_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    # Tracking
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class MessageBus:
    """
    Redis Pub/Sub message bus for Rex system.
    Handles routing, correlation, and dead letter queue.
    """

    # Channel patterns
    CHANNELS = {
        'missions': 'rex:missions',  # Mission lifecycle events
        'agents': 'rex:agents:{crew}',  # Agent-specific messages
        'errors': 'rex:errors',  # Error escalations
        'analytics': 'rex:analytics',  # Analytics events
        'system': 'rex:system',  # System-wide broadcasts
        'deadletter': 'rex:deadletter',  # Failed message processing
    }

    # Message type categories
    MESSAGE_TYPES = {
        # Rex → Agent
        'mission.assigned': 'missions',
        'mission.cancelled': 'missions',
        'resource.allocated': 'missions',

        # Agent → Rex
        'mission.started': 'missions',
        'mission.progress': 'missions',
        'mission.completed': 'missions',
        'mission.failed': 'missions',

        # System
        'resource.exhausted': 'system',
        'error.escalation': 'errors',
        'domain.rotation_needed': 'system',

        # Analytics
        'analytics.snapshot': 'analytics',
        'analytics.anomaly': 'analytics',
    }

    def __init__(self, redis):
        self.redis = redis
        self.pubsub = redis.pubsub()

        # Message handlers
        self.handlers: Dict[str, List[Callable]] = {}

        # Correlation tracking
        self.pending_replies: Dict[str, asyncio.Future] = {}

        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'deadletter_count': 0
        }

    async def start(self):
        """Start message bus listener"""
        logger.info("Starting Rex message bus...")

        # Subscribe to all channels
        await self.pubsub.subscribe(
            self.CHANNELS['missions'],
            self.CHANNELS['errors'],
            self.CHANNELS['analytics'],
            self.CHANNELS['system']
        )

        # Start listener loop
        asyncio.create_task(self._listener_loop())

        logger.info("Message bus started")

    async def stop(self):
        """Stop message bus"""
        logger.info("Stopping message bus...")
        await self.pubsub.unsubscribe()
        await self.pubsub.close()
        logger.info("Message bus stopped")

    async def _listener_loop(self):
        """Listen for incoming messages"""
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)

                if message and message['type'] == 'message':
                    await self._process_message(message['data'])

                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning

            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, raw_data: bytes):
        """Process incoming message"""
        try:
            # Deserialize message
            message = Message.from_json(raw_data.decode('utf-8'))
            self.stats['messages_received'] += 1

            logger.debug(
                f"Received message: {message.type} from {message.sender} "
                f"(mission: {message.mission_id})"
            )

            # Handle replies
            if message.reply_to and message.reply_to in self.pending_replies:
                future = self.pending_replies.pop(message.reply_to)
                future.set_result(message)
                return

            # Route to handlers
            handlers = self.handlers.get(message.type, [])
            if not handlers:
                logger.warning(f"No handler registered for message type: {message.type}")
                return

            # Execute all registered handlers
            for handler in handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Handler failed for message {message.id}: {e}")
                    await self._send_to_deadletter(message, str(e))

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats['messages_failed'] += 1

    async def publish(
        self,
        message_type: str,
        sender: str,
        recipient: str = 'broadcast',
        mission_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> str:
        """
        Publish message to appropriate channel.
        Returns message ID.
        """
        try:
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                type=message_type,
                timestamp=datetime.utcnow().isoformat(),
                sender=sender,
                recipient=recipient,
                mission_id=mission_id,
                data=data or {},
                correlation_id=correlation_id,
                reply_to=reply_to
            )

            # Determine channel
            channel = self._get_channel(message_type, recipient)

            # Publish to Redis
            await self.redis.publish(channel, message.to_json())

            self.stats['messages_sent'] += 1

            logger.debug(
                f"Published message: {message_type} to {channel} "
                f"(id: {message.id}, mission: {mission_id})"
            )

            return message.id

        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            self.stats['messages_failed'] += 1
            raise

    async def publish_and_wait(
        self,
        message_type: str,
        sender: str,
        recipient: str,
        mission_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> Optional[Message]:
        """
        Publish message and wait for reply.
        Returns reply message or None if timeout.
        """
        try:
            # Create correlation ID
            correlation_id = str(uuid.uuid4())

            # Create future for reply
            reply_future = asyncio.Future()
            self.pending_replies[correlation_id] = reply_future

            # Publish message
            message_id = await self.publish(
                message_type=message_type,
                sender=sender,
                recipient=recipient,
                mission_id=mission_id,
                data=data,
                correlation_id=correlation_id
            )

            logger.debug(f"Waiting for reply to message {message_id}...")

            # Wait for reply with timeout
            try:
                reply = await asyncio.wait_for(reply_future, timeout=timeout)
                logger.debug(f"Received reply to message {message_id}")
                return reply
            except asyncio.TimeoutError:
                logger.warning(f"Reply timeout for message {message_id}")
                self.pending_replies.pop(correlation_id, None)
                return None

        except Exception as e:
            logger.error(f"Error in publish_and_wait: {e}")
            return None

    async def reply(
        self,
        original_message: Message,
        sender: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Reply to a message"""
        if not original_message.correlation_id:
            logger.warning("Cannot reply to message without correlation_id")
            return

        await self.publish(
            message_type=f"{original_message.type}.reply",
            sender=sender,
            recipient=original_message.sender,
            mission_id=original_message.mission_id,
            data=data,
            reply_to=original_message.correlation_id
        )

    def _get_channel(self, message_type: str, recipient: str) -> str:
        """Determine Redis channel for message type"""
        # Check if it's an agent-specific message
        if recipient.startswith('crew_') or recipient in [
            'dead_lead_crew', 'campaign_crew', 'auto_icp_crew',
            'domain_health_monitor', 'special_forces_coordinator'
        ]:
            return self.CHANNELS['agents'].format(crew=recipient)

        # Use message type category
        category = self.MESSAGE_TYPES.get(message_type, 'system')
        channel_key = category if category in self.CHANNELS else 'system'
        return self.CHANNELS[channel_key]

    async def _send_to_deadletter(self, message: Message, error: str):
        """Send failed message to dead letter queue"""
        try:
            deadletter_data = {
                'message': asdict(message),
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }

            await self.redis.publish(
                self.CHANNELS['deadletter'],
                json.dumps(deadletter_data)
            )

            # Store in Redis list for later inspection
            await self.redis.lpush(
                'rex:deadletter:messages',
                json.dumps(deadletter_data)
            )

            # Keep only last 1000 messages
            await self.redis.ltrim('rex:deadletter:messages', 0, 999)

            self.stats['deadletter_count'] += 1

            logger.error(
                f"Message sent to dead letter queue: {message.id} "
                f"(error: {error})"
            )

        except Exception as e:
            logger.error(f"Error sending to dead letter queue: {e}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register handler for message type"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []

        self.handlers[message_type].append(handler)

        logger.info(f"Handler registered for message type: {message_type}")

    def unregister_handler(self, message_type: str, handler: Callable):
        """Unregister handler for message type"""
        if message_type in self.handlers:
            self.handlers[message_type].remove(handler)

            if not self.handlers[message_type]:
                del self.handlers[message_type]

            logger.info(f"Handler unregistered for message type: {message_type}")

    async def broadcast(
        self,
        message_type: str,
        sender: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Broadcast message to all subscribers"""
        await self.publish(
            message_type=message_type,
            sender=sender,
            recipient='broadcast',
            data=data
        )

    async def get_deadletter_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve messages from dead letter queue"""
        try:
            messages_json = await self.redis.lrange(
                'rex:deadletter:messages',
                0,
                limit - 1
            )

            return [json.loads(msg) for msg in messages_json]

        except Exception as e:
            logger.error(f"Error retrieving dead letter messages: {e}")
            return []

    async def clear_deadletter(self):
        """Clear dead letter queue"""
        try:
            await self.redis.delete('rex:deadletter:messages')
            self.stats['deadletter_count'] = 0
            logger.info("Dead letter queue cleared")
        except Exception as e:
            logger.error(f"Error clearing dead letter queue: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            **self.stats,
            'pending_replies': len(self.pending_replies),
            'registered_handlers': sum(len(handlers) for handlers in self.handlers.values()),
            'handler_types': len(self.handlers)
        }


# ============================================================================
# MESSAGE BUS UTILITIES
# ============================================================================

class MessageBuilder:
    """Utility class for building common messages"""

    @staticmethod
    def mission_assigned(
        mission_id: str,
        crew_name: str,
        mission_data: Dict[str, Any],
        resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build mission assigned message"""
        return {
            'message_type': 'mission.assigned',
            'sender': 'rex',
            'recipient': crew_name,
            'mission_id': mission_id,
            'data': {
                'mission': mission_data,
                'resources': resources,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def mission_progress(
        mission_id: str,
        agent_name: str,
        progress: float,
        status: str
    ) -> Dict[str, Any]:
        """Build mission progress message"""
        return {
            'message_type': 'mission.progress',
            'sender': agent_name,
            'recipient': 'rex',
            'mission_id': mission_id,
            'data': {
                'progress': progress,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def mission_completed(
        mission_id: str,
        crew_name: str,
        outcome: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build mission completed message"""
        return {
            'message_type': 'mission.completed',
            'sender': crew_name,
            'recipient': 'rex',
            'mission_id': mission_id,
            'data': {
                'outcome': outcome,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def mission_failed(
        mission_id: str,
        crew_name: str,
        error: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build mission failed message"""
        return {
            'message_type': 'mission.failed',
            'sender': crew_name,
            'recipient': 'rex',
            'mission_id': mission_id,
            'data': {
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def error_escalation(
        mission_id: str,
        source: str,
        error: Dict[str, Any],
        severity: str = 'high'
    ) -> Dict[str, Any]:
        """Build error escalation message"""
        return {
            'message_type': 'error.escalation',
            'sender': source,
            'recipient': 'rex',
            'mission_id': mission_id,
            'data': {
                'error': error,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def domain_rotation_needed(
        domain: str,
        reputation: float,
        reason: str
    ) -> Dict[str, Any]:
        """Build domain rotation message"""
        return {
            'message_type': 'domain.rotation_needed',
            'sender': 'domain_health_monitor',
            'recipient': 'rex',
            'data': {
                'domain': domain,
                'reputation': reputation,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    @staticmethod
    def resource_exhausted(
        resource_type: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build resource exhausted message"""
        return {
            'message_type': 'resource.exhausted',
            'sender': 'rex',
            'recipient': 'broadcast',
            'data': {
                'resource_type': resource_type,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
