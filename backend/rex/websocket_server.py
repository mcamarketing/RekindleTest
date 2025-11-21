"""
REX WebSocket Server
Real-time updates for missions, agents, and domain health
"""

import json
import logging
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

from .message_bus import MessageBus, Message

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)

        # Subscriptions: user_id -> set of subscription types
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'connection_errors': 0
        }

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()

        self.active_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow().isoformat(),
            'last_ping': datetime.utcnow()
        }

        self.stats['total_connections'] += 1
        self.stats['active_connections'] = sum(len(conns) for conns in self.active_connections.values())

        logger.info(f"WebSocket connected: user={user_id}, total_active={self.stats['active_connections']}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return

        user_id = metadata['user_id']

        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

        if user_id in self.subscriptions and not self.active_connections.get(user_id):
            del self.subscriptions[user_id]

        del self.connection_metadata[websocket]

        self.stats['active_connections'] = sum(len(conns) for conns in self.active_connections.values())

        logger.info(f"WebSocket disconnected: user={user_id}, total_active={self.stats['active_connections']}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
            self.stats['messages_sent'] += 1
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.stats['connection_errors'] += 1

    async def send_to_user(self, message: dict, user_id: str):
        """Send message to all connections of a user"""
        if user_id not in self.active_connections:
            return

        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
                self.stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(websocket)
                self.stats['connection_errors'] += 1

        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            if exclude_user and user_id == exclude_user:
                continue

            await self.send_to_user(message, user_id)

    def subscribe(self, user_id: str, subscription_type: str):
        """Subscribe user to specific update type"""
        self.subscriptions[user_id].add(subscription_type)
        logger.debug(f"User {user_id} subscribed to {subscription_type}")

    def unsubscribe(self, user_id: str, subscription_type: str):
        """Unsubscribe user from update type"""
        self.subscriptions[user_id].discard(subscription_type)
        logger.debug(f"User {user_id} unsubscribed from {subscription_type}")

    def is_subscribed(self, user_id: str, subscription_type: str) -> bool:
        """Check if user is subscribed to update type"""
        return subscription_type in self.subscriptions.get(user_id, set())

    def get_subscribed_users(self, subscription_type: str) -> Set[str]:
        """Get all users subscribed to update type"""
        return {
            user_id
            for user_id, subs in self.subscriptions.items()
            if subscription_type in subs
        }

    async def ping_all(self):
        """Send ping to all connections to keep them alive"""
        ping_message = {'type': 'ping', 'timestamp': datetime.utcnow().isoformat()}

        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(ping_message, user_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            **self.stats,
            'users_connected': len(self.active_connections),
            'subscription_count': sum(len(subs) for subs in self.subscriptions.values())
        }


class RexWebSocketServer:
    """
    WebSocket server for Rex real-time updates.
    Subscribes to message bus and broadcasts to connected clients.
    """

    # Subscription types
    SUBSCRIPTION_TYPES = {
        'missions': 'mission.*',  # All mission events
        'agents': 'agent.*',  # Agent status updates
        'domains': 'domain.*',  # Domain health updates
        'analytics': 'analytics.*',  # Analytics updates
        'errors': 'error.*',  # Error notifications
        'system': 'system.*',  # System-wide events
    }

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.connection_manager = ConnectionManager()

        # Register message handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register message bus handlers for WebSocket broadcasting"""

        # Mission events
        self.message_bus.register_handler('mission.assigned', self._handle_mission_assigned)
        self.message_bus.register_handler('mission.started', self._handle_mission_started)
        self.message_bus.register_handler('mission.progress', self._handle_mission_progress)
        self.message_bus.register_handler('mission.completed', self._handle_mission_completed)
        self.message_bus.register_handler('mission.failed', self._handle_mission_failed)

        # System events
        self.message_bus.register_handler('domain.rotation_needed', self._handle_domain_rotation)
        self.message_bus.register_handler('error.escalation', self._handle_error_escalation)
        self.message_bus.register_handler('resource.exhausted', self._handle_resource_exhausted)

        # Analytics events
        self.message_bus.register_handler('analytics.snapshot', self._handle_analytics_snapshot)
        self.message_bus.register_handler('analytics.anomaly', self._handle_analytics_anomaly)

    async def _handle_mission_assigned(self, message: Message):
        """Handle mission assigned event"""
        await self._broadcast_to_subscribed('missions', {
            'type': 'mission.assigned',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_mission_started(self, message: Message):
        """Handle mission started event"""
        await self._broadcast_to_subscribed('missions', {
            'type': 'mission.started',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_mission_progress(self, message: Message):
        """Handle mission progress event"""
        await self._broadcast_to_subscribed('missions', {
            'type': 'mission.progress',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_mission_completed(self, message: Message):
        """Handle mission completed event"""
        await self._broadcast_to_subscribed('missions', {
            'type': 'mission.completed',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_mission_failed(self, message: Message):
        """Handle mission failed event"""
        await self._broadcast_to_subscribed('missions', {
            'type': 'mission.failed',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_domain_rotation(self, message: Message):
        """Handle domain rotation event"""
        await self._broadcast_to_subscribed('domains', {
            'type': 'domain.rotation_needed',
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_error_escalation(self, message: Message):
        """Handle error escalation event"""
        await self._broadcast_to_subscribed('errors', {
            'type': 'error.escalation',
            'mission_id': message.mission_id,
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_resource_exhausted(self, message: Message):
        """Handle resource exhausted event"""
        await self._broadcast_to_subscribed('system', {
            'type': 'resource.exhausted',
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_analytics_snapshot(self, message: Message):
        """Handle analytics snapshot event"""
        await self._broadcast_to_subscribed('analytics', {
            'type': 'analytics.snapshot',
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _handle_analytics_anomaly(self, message: Message):
        """Handle analytics anomaly event"""
        await self._broadcast_to_subscribed('analytics', {
            'type': 'analytics.anomaly',
            'data': message.data,
            'timestamp': message.timestamp
        })

    async def _broadcast_to_subscribed(self, subscription_type: str, message: dict):
        """Broadcast message to all users subscribed to type"""
        subscribed_users = self.connection_manager.get_subscribed_users(subscription_type)

        for user_id in subscribed_users:
            await self.connection_manager.send_to_user(message, user_id)

    async def handle_websocket(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection lifecycle"""
        await self.connection_manager.connect(websocket, user_id)

        # Send welcome message
        await self.connection_manager.send_personal_message({
            'type': 'connected',
            'message': 'Connected to Rex WebSocket server',
            'timestamp': datetime.utcnow().isoformat(),
            'available_subscriptions': list(self.SUBSCRIPTION_TYPES.keys())
        }, websocket)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                await self._handle_client_message(websocket, user_id, data)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: user={user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
        finally:
            self.connection_manager.disconnect(websocket)

    async def _handle_client_message(self, websocket: WebSocket, user_id: str, data: str):
        """Handle incoming message from client"""
        try:
            message = json.loads(data)
            message_type = message.get('type')

            if message_type == 'subscribe':
                # Subscribe to update types
                subscription_types = message.get('subscriptions', [])
                for sub_type in subscription_types:
                    if sub_type in self.SUBSCRIPTION_TYPES:
                        self.connection_manager.subscribe(user_id, sub_type)

                await self.connection_manager.send_personal_message({
                    'type': 'subscribed',
                    'subscriptions': subscription_types,
                    'timestamp': datetime.utcnow().isoformat()
                }, websocket)

            elif message_type == 'unsubscribe':
                # Unsubscribe from update types
                subscription_types = message.get('subscriptions', [])
                for sub_type in subscription_types:
                    self.connection_manager.unsubscribe(user_id, sub_type)

                await self.connection_manager.send_personal_message({
                    'type': 'unsubscribed',
                    'subscriptions': subscription_types,
                    'timestamp': datetime.utcnow().isoformat()
                }, websocket)

            elif message_type == 'ping':
                # Respond to ping
                await self.connection_manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                }, websocket)

            else:
                logger.warning(f"Unknown message type from user {user_id}: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from user {user_id}: {data}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def start_ping_loop(self):
        """Start periodic ping to keep connections alive"""
        while True:
            try:
                await asyncio.sleep(30)  # Ping every 30 seconds
                await self.connection_manager.ping_all()
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket server statistics"""
        return self.connection_manager.get_stats()


# ============================================================================
# FASTAPI INTEGRATION
# ============================================================================

# Global WebSocket server instance
_ws_server: Optional[RexWebSocketServer] = None


def init_websocket_server(message_bus: MessageBus):
    """Initialize WebSocket server"""
    global _ws_server
    _ws_server = RexWebSocketServer(message_bus)
    logger.info("WebSocket server initialized")


def get_websocket_server() -> RexWebSocketServer:
    """Get WebSocket server instance"""
    if not _ws_server:
        raise RuntimeError("WebSocket server not initialized")
    return _ws_server


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint handler"""
    ws_server = get_websocket_server()
    await ws_server.handle_websocket(websocket, user_id)
