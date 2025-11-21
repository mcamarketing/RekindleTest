"""
Base Agent Class for REX Special Forces

Provides common functionality for all CrewAI agents:
- Mission lifecycle management
- Telemetry and logging
- Error handling and retries
- Idempotency
- PII redaction for LLM calls
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class MissionContext:
    """Context passed to agent for mission execution"""
    mission_id: str
    user_id: str
    mission_type: str
    priority: int
    params: Dict[str, Any]
    resources: Dict[str, Any]
    idempotency_key: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AgentResult:
    """Result returned by agent after mission execution"""
    success: bool
    data: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    next_actions: Optional[List[str]] = None


class BaseAgent(ABC):
    """
    Base class for all REX Special Forces agents.

    All agents must:
    1. Implement handle_mission() method
    2. Use deterministic logic first, LLM only when necessary
    3. Log all actions to agent_logs table
    4. Handle errors gracefully with retries
    5. Respect idempotency keys
    6. Redact PII before LLM calls
    """

    def __init__(self, db, redis, config: Optional[Dict[str, Any]] = None):
        self.db = db
        self.redis = redis
        self.config = config or {}
        self.agent_name = self.__class__.__name__

        # Statistics
        self.stats = {
            'missions_handled': 0,
            'missions_succeeded': 0,
            'missions_failed': 0,
            'total_duration_ms': 0,
            'llm_calls': 0
        }

    @abstractmethod
    async def handle_mission(self, context: MissionContext) -> AgentResult:
        """
        Main mission handler - must be implemented by each agent.

        Args:
            context: Mission context with all necessary information

        Returns:
            AgentResult with success status, data, and metrics
        """
        pass

    async def execute_mission(self, context: MissionContext) -> AgentResult:
        """
        Wrapper for mission execution with error handling, retries, and telemetry.

        This is the public interface called by Rex scheduler.
        """
        start_time = datetime.utcnow()

        try:
            # Check idempotency
            if context.idempotency_key:
                cached_result = await self._check_idempotency(context.idempotency_key)
                if cached_result:
                    logger.info(f"Idempotent mission {context.mission_id}: returning cached result")
                    return cached_result

            # Log mission start
            await self._log_event(
                mission_id=context.mission_id,
                event_type='mission_started',
                data={'agent': self.agent_name, 'retry_count': context.retry_count}
            )

            # Execute actual mission logic
            result = await self.handle_mission(context)

            # Update statistics
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self.stats['missions_handled'] += 1
            self.stats['total_duration_ms'] += duration_ms

            if result.success:
                self.stats['missions_succeeded'] += 1
            else:
                self.stats['missions_failed'] += 1

            # Add metrics to result
            if not result.metrics:
                result.metrics = {}
            result.metrics['duration_ms'] = duration_ms
            result.metrics['agent'] = self.agent_name

            # Log mission completion
            await self._log_event(
                mission_id=context.mission_id,
                event_type='mission_completed' if result.success else 'mission_failed',
                data={
                    'agent': self.agent_name,
                    'duration_ms': duration_ms,
                    'result': result.data if result.success else result.error
                }
            )

            # Cache result if idempotent
            if context.idempotency_key and result.success:
                await self._cache_result(context.idempotency_key, result)

            return result

        except Exception as e:
            logger.error(f"Mission {context.mission_id} failed: {e}", exc_info=True)

            # Log error
            await self._log_event(
                mission_id=context.mission_id,
                event_type='mission_error',
                data={
                    'agent': self.agent_name,
                    'error': str(e),
                    'retry_count': context.retry_count
                }
            )

            # Return error result
            return AgentResult(
                success=False,
                data={},
                error={
                    'code': 'agent_error',
                    'message': str(e),
                    'recoverable': context.retry_count < context.max_retries
                },
                metrics={'duration_ms': int((datetime.utcnow() - start_time).total_seconds() * 1000)}
            )

    async def _check_idempotency(self, idempotency_key: str) -> Optional[AgentResult]:
        """Check if mission has already been executed"""
        try:
            cached = await self.redis.get(f'idempotency:{idempotency_key}')
            if cached:
                data = json.loads(cached)
                return AgentResult(**data)
        except Exception as e:
            logger.warning(f"Idempotency check failed: {e}")
        return None

    async def _cache_result(self, idempotency_key: str, result: AgentResult):
        """Cache result for idempotency"""
        try:
            await self.redis.setex(
                f'idempotency:{idempotency_key}',
                3600,  # 1 hour TTL
                json.dumps({
                    'success': result.success,
                    'data': result.data,
                    'error': result.error,
                    'metrics': result.metrics
                })
            )
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

    async def _log_event(self, mission_id: str, event_type: str, data: Dict[str, Any]):
        """Write event to agent_logs table"""
        try:
            await self.db.table('agent_logs').insert({
                'mission_id': mission_id,
                'agent_name': self.agent_name,
                'event_type': event_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log event: {e}")

    def redact_pii(self, data: Dict[str, Any], consent: bool = False) -> Dict[str, Any]:
        """
        Redact PII from data before sending to LLM.

        Args:
            data: Data to redact
            consent: If True, PII is allowed (user gave consent)

        Returns:
            Redacted data safe for LLM
        """
        if consent:
            return data

        redacted = data.copy()

        # Fields to always redact
        pii_fields = [
            'email', 'phone', 'ssn', 'tax_id',
            'address', 'credit_card', 'password',
            'api_key', 'token', 'secret'
        ]

        for field in pii_fields:
            if field in redacted:
                redacted[field] = '[REDACTED]'

        # Redact nested objects
        for key, value in redacted.items():
            if isinstance(value, dict):
                redacted[key] = self.redact_pii(value, consent)
            elif isinstance(value, list):
                redacted[key] = [
                    self.redact_pii(item, consent) if isinstance(item, dict) else item
                    for item in value
                ]

        return redacted

    def generate_idempotency_key(self, *args) -> str:
        """Generate idempotency key from arguments"""
        data = json.dumps(args, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        avg_duration = (
            self.stats['total_duration_ms'] / self.stats['missions_handled']
            if self.stats['missions_handled'] > 0 else 0
        )

        success_rate = (
            self.stats['missions_succeeded'] / self.stats['missions_handled']
            if self.stats['missions_handled'] > 0 else 0
        )

        return {
            **self.stats,
            'avg_duration_ms': avg_duration,
            'success_rate': success_rate
        }
