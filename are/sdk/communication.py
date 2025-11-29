"""
ARE SDK Communication Layer

Handles HTTP and WebSocket communication with ARE services.
Provides retry logic, error handling, and connection management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
import aiohttp
import websockets
import json
from datetime import datetime

from .types import AREConfig, AREEvent
from .exceptions import (
    NetworkError, TimeoutError, AuthenticationError,
    RateLimitError, AREError
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for ARE API communication"""

    def __init__(self, config: AREConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._headers = {}

        if config.api_key:
            self._headers["Authorization"] = f"Bearer {config.api_key}"

        if config.org_id:
            self._headers["X-Org-ID"] = config.org_id

        if config.user_id:
            self._headers["X-User-ID"] = config.user_id

    async def connect(self):
        """Establish HTTP connection"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._headers
            )

    async def disconnect(self):
        """Close HTTP connection"""
        if self.session:
            await self.session.close()
            self.session = None

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """HTTP GET request"""
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Dict[str, Any] = None, timeout: int = None) -> Dict[str, Any]:
        """HTTP POST request"""
        return await self._request("POST", endpoint, data=data, timeout=timeout)

    async def put(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """HTTP PUT request"""
        return await self._request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """HTTP DELETE request"""
        return await self._request("DELETE", endpoint)

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Execute HTTP request with retry logic"""
        if not self.session:
            raise AREError("HTTP client not connected")

        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        request_data = {
            "method": method,
            "url": url,
            "params": params,
            "json": data,
            "timeout": aiohttp.ClientTimeout(total=timeout or self.config.timeout)
        }

        last_error = None

        for attempt in range(self.config.retry_attempts + 1):
            try:
                async with self.session.request(**request_data) as response:
                    return await self._handle_response(response)

            except asyncio.TimeoutError as e:
                last_error = TimeoutError(endpoint, timeout or self.config.timeout, str(e))
            except aiohttp.ClientError as e:
                last_error = NetworkError(url, method, str(e))
            except Exception as e:
                last_error = AREError(f"HTTP request failed: {str(e)}")

            if attempt < self.config.retry_attempts:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff

        raise last_error

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response"""
        try:
            if response.status == 401:
                raise AuthenticationError("Invalid API key or credentials")
            elif response.status == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status == 429:
                reset_in = int(response.headers.get("X-RateLimit-Reset", 60))
                limit = int(response.headers.get("X-RateLimit-Limit", 100))
                raise RateLimitError(limit, reset_in, "Rate limit exceeded")
            elif response.status >= 400:
                error_data = await response.json()
                raise AREError(
                    error_data.get("message", f"HTTP {response.status}"),
                    error_data.get("error_code", f"HTTP_{response.status}")
                )

            # Success response
            if response.content_type == "application/json":
                return await response.json()
            else:
                return {"data": await response.text()}

        except json.JSONDecodeError:
            raise AREError("Invalid JSON response from server")


class WebSocketClient:
    """WebSocket client for real-time ARE communication"""

    def __init__(self, config: AREConfig):
        self.config = config
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._subscriptions: List[str] = []
        self._reconnect_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Establish WebSocket connection"""
        if not self.config.websocket_url:
            raise AREError("WebSocket URL not configured")

        try:
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            self.websocket = await websockets.connect(
                self.config.websocket_url,
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )

            self.connected = True
            logger.info("WebSocket connected to ARE")

            # Start message handling
            asyncio.create_task(self._handle_messages())

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise NetworkError(self.config.websocket_url, "WEBSOCKET", str(e))

    async def disconnect(self):
        """Close WebSocket connection"""
        self.connected = False

        if self._reconnect_task:
            self._reconnect_task.cancel()

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        logger.info("WebSocket disconnected from ARE")

    async def subscribe(self, event_types: List[str]):
        """Subscribe to specific event types"""
        if not self.connected or not self.websocket:
            raise AREError("WebSocket not connected")

        self._subscriptions = event_types

        subscription_message = {
            "type": "subscribe",
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }

        await self.websocket.send(json.dumps(subscription_message))
        logger.info(f"Subscribed to events: {event_types}")

    async def unsubscribe(self, event_types: List[str]):
        """Unsubscribe from specific event types"""
        if not self.connected or not self.websocket:
            raise AREError("WebSocket not connected")

        for event_type in event_types:
            if event_type in self._subscriptions:
                self._subscriptions.remove(event_type)

        unsubscription_message = {
            "type": "unsubscribe",
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }

        await self.websocket.send(json.dumps(unsubscription_message))
        logger.info(f"Unsubscribed from events: {event_types}")

    def on_event(self, callback: Callable):
        """Register event handler for all events"""
        if "*" not in self._event_handlers:
            self._event_handlers["*"] = []
        self._event_handlers["*"].append(callback)

    def on_event_type(self, event_type: str, callback: Callable):
        """Register event handler for specific event type"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(callback)

    async def send_event(self, event: AREEvent):
        """Send event through WebSocket"""
        if not self.connected or not self.websocket:
            raise AREError("WebSocket not connected")

        message = {
            "type": "event",
            **event.to_dict()
        }

        await self.websocket.send(json.dumps(message))

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    await self._process_message(message)

                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    self.connected = False
                    break

                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    continue

        except Exception as e:
            logger.error(f"WebSocket message handling error: {e}")
        finally:
            self.connected = False

    async def _process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)

            if data.get("type") == "event":
                # Create ARE event
                event = AREEvent(
                    event_type=data.get("event_type", "unknown"),
                    event_id=data.get("event_id", ""),
                    source=data.get("source", "unknown"),
                    data=data.get("data", {}),
                    timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                    correlation_id=data.get("correlation_id")
                )

                # Call handlers
                await self._dispatch_event(event)

            elif data.get("type") == "pong":
                # Heartbeat response
                pass

            elif data.get("type") == "error":
                logger.error(f"WebSocket error: {data.get('message', 'Unknown error')}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")

    async def _dispatch_event(self, event: AREEvent):
        """Dispatch event to registered handlers"""
        # Call type-specific handlers
        type_handlers = self._event_handlers.get(event.event_type, [])
        for handler in type_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event.event_type}: {e}")

        # Call global handlers
        global_handlers = self._event_handlers.get("*", [])
        for handler in global_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Global event handler error: {e}")

    async def _reconnect(self):
        """Attempt to reconnect WebSocket"""
        logger.info("Attempting WebSocket reconnection...")

        try:
            await self.connect()

            # Resubscribe to previous subscriptions
            if self._subscriptions:
                await self.subscribe(self._subscriptions)

        except Exception as e:
            logger.error(f"WebSocket reconnection failed: {e}")
            # Schedule another attempt
            self._reconnect_task = asyncio.create_task(self._delayed_reconnect())

    async def _delayed_reconnect(self):
        """Delayed reconnection attempt"""
        await asyncio.sleep(5)  # Wait 5 seconds before retry
        await self._reconnect()