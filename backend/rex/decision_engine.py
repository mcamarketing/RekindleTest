"""
REX Decision Engine Core
Three-layer decision architecture:
1. State Machine (deterministic, fast)
2. Rule Engine (business logic)
3. LLM Reasoner (complex context-aware decisions)
"""

import json
import logging
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import openai

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class MissionType(str, Enum):
    LEAD_REACTIVATION = "lead_reactivation"
    CAMPAIGN_EXECUTION = "campaign_execution"
    ICP_EXTRACTION = "icp_extraction"
    DOMAIN_ROTATION = "domain_rotation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_RECOVERY = "error_recovery"


class MissionState(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Mission:
    id: str
    type: MissionType
    state: MissionState
    priority: int
    user_id: str
    campaign_id: Optional[str] = None
    lead_ids: Optional[List[str]] = None
    custom_params: Optional[Dict[str, Any]] = None
    assigned_crew: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Decision:
    action: str
    params: Dict[str, Any] = None
    target_state: Optional[MissionState] = None
    reason: str = ""
    confidence: float = 1.0
    alternatives_considered: List[str] = None
    llm_used: bool = False

    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.alternatives_considered is None:
            self.alternatives_considered = []


# ============================================================================
# STATE MACHINE (Layer 1: Deterministic)
# ============================================================================

class StateMachine:
    """Deterministic state transitions"""

    TRANSITIONS = {
        MissionState.QUEUED: [MissionState.ASSIGNED, MissionState.FAILED],
        MissionState.ASSIGNED: [MissionState.EXECUTING, MissionState.FAILED],
        MissionState.EXECUTING: [MissionState.COLLECTING, MissionState.FAILED],
        MissionState.COLLECTING: [MissionState.ANALYZING, MissionState.FAILED],
        MissionState.ANALYZING: [MissionState.OPTIMIZING, MissionState.COMPLETED],
        MissionState.OPTIMIZING: [MissionState.COMPLETED, MissionState.FAILED],
    }

    def can_handle(self, state: MissionState, context: Dict[str, Any]) -> bool:
        """Check if this is a simple state transition"""
        target = context.get('target_state')
        if not target:
            return False

        try:
            target_state = MissionState(target)
            return target_state in self.TRANSITIONS.get(state, [])
        except ValueError:
            return False

    async def decide(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Execute deterministic state transition"""
        target_str = context.get('target_state')
        target_state = MissionState(target_str)

        if target_state not in self.TRANSITIONS[mission.state]:
            raise ValueError(
                f"Invalid transition: {mission.state} -> {target_state}"
            )

        logger.info(
            f"State machine: Mission {mission.id} transitioning "
            f"{mission.state} -> {target_state}"
        )

        return Decision(
            action='transition_state',
            target_state=target_state,
            reason='deterministic_state_machine',
            confidence=1.0
        )


# ============================================================================
# RULE ENGINE (Layer 2: Business Logic)
# ============================================================================

class Rule:
    """Base class for business logic rules"""

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        """Check if this rule applies to the mission"""
        raise NotImplementedError

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Execute the rule and return a decision"""
        raise NotImplementedError


class DomainRotationRule(Rule):
    """Rotate domain if reputation drops below threshold"""

    REPUTATION_THRESHOLD = 0.7

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.type == MissionType.CAMPAIGN_EXECUTION and
            context.get('domain_reputation') is not None and
            context['domain_reputation'] < self.REPUTATION_THRESHOLD
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        domain = context.get('domain')
        reputation = context['domain_reputation']

        logger.warning(
            f"Domain rotation triggered: {domain} "
            f"(reputation: {reputation:.2f} < {self.REPUTATION_THRESHOLD})"
        )

        return Decision(
            action='rotate_domain',
            params={
                'domain': domain,
                'reason': 'reputation_drop',
                'current_reputation': reputation,
                'threshold': self.REPUTATION_THRESHOLD,
                'replacement_strategy': 'prewarmed_pool'
            },
            reason=f'domain_reputation_below_threshold ({reputation:.2f} < {self.REPUTATION_THRESHOLD})',
            confidence=0.95
        )


class ResourceAllocationRule(Rule):
    """Allocate resources based on mission priority"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.state == MissionState.QUEUED and
            context.get('action') == 'allocate_resources'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Check resource availability
        available_resources = context.get('available_resources', {})

        # Prioritize based on mission type and priority
        if mission.priority >= 80:
            # High priority - allocate immediately
            return Decision(
                action='allocate_resources',
                params={'strategy': 'immediate', 'resources': available_resources},
                reason='high_priority_mission',
                confidence=0.9
            )
        elif mission.priority >= 50:
            # Medium priority - standard allocation
            return Decision(
                action='allocate_resources',
                params={'strategy': 'standard', 'resources': available_resources},
                reason='standard_priority_mission',
                confidence=0.85
            )
        else:
            # Low priority - queue if resources constrained
            return Decision(
                action='queue_mission',
                params={'reason': 'low_priority_resource_constraint'},
                reason='low_priority_with_resource_constraint',
                confidence=0.8
            )


class ErrorEscalationRule(Rule):
    """Escalate errors based on severity and retry count"""

    MAX_RETRIES = 3

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return context.get('error') is not None

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        error = context['error']
        retry_count = error.get('retry_count', 0)
        recoverable = error.get('recoverable', False)

        if not recoverable:
            # Non-recoverable error - escalate immediately
            return Decision(
                action='escalate_error',
                params={
                    'error': error,
                    'escalation_reason': 'non_recoverable_error'
                },
                target_state=MissionState.FAILED,
                reason='non_recoverable_error_detected',
                confidence=1.0
            )

        if retry_count < self.MAX_RETRIES:
            # Retry with exponential backoff
            backoff_seconds = 2 ** retry_count
            return Decision(
                action='retry_mission',
                params={
                    'retry_count': retry_count + 1,
                    'backoff_seconds': backoff_seconds,
                    'error': error
                },
                reason=f'recoverable_error_retry_{retry_count + 1}',
                confidence=0.7 - (retry_count * 0.1)
            )
        else:
            # Max retries exceeded - escalate
            return Decision(
                action='escalate_error',
                params={
                    'error': error,
                    'escalation_reason': 'max_retries_exceeded'
                },
                target_state=MissionState.FAILED,
                reason='max_retries_exceeded',
                confidence=0.95
            )


class PriorityBoostRule(Rule):
    """Boost priority for time-sensitive missions"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            mission.state == MissionState.QUEUED and
            context.get('action') == 'check_priority'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Check if mission has been queued for too long
        queue_time = datetime.utcnow() - mission.created_at
        queue_hours = queue_time.total_seconds() / 3600

        if queue_hours > 24:
            # Boost priority if queued for over 24 hours
            new_priority = min(mission.priority + 20, 100)
            return Decision(
                action='boost_priority',
                params={
                    'old_priority': mission.priority,
                    'new_priority': new_priority,
                    'reason': 'long_queue_time'
                },
                reason=f'mission_queued_for_{queue_hours:.1f}_hours',
                confidence=0.9
            )

        return Decision(
            action='maintain_priority',
            params={'current_priority': mission.priority},
            reason='queue_time_acceptable',
            confidence=0.8
        )


class IdleOptimizationRule(Rule):
    """Trigger idle optimization when no missions active"""

    def __init__(self, db):
        self.db = db

    def matches(self, mission: Mission, context: Dict[str, Any]) -> bool:
        return (
            context.get('system_state') == 'idle' and
            context.get('action') == 'optimize_idle'
        )

    async def execute(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        # Identify optimization opportunities
        opportunities = []

        # Check domain warmup needs
        warming_domains = context.get('warming_domains', 0)
        if warming_domains < 2:
            opportunities.append('start_domain_warmup')

        # Check for performance analysis
        last_analysis = context.get('last_performance_analysis')
        if not last_analysis or (datetime.utcnow() - last_analysis).days >= 1:
            opportunities.append('run_performance_analysis')

        return Decision(
            action='idle_optimization',
            params={'opportunities': opportunities},
            reason='system_idle_optimization_triggered',
            confidence=0.75
        )


class RuleEngine:
    """Business logic rules"""

    def __init__(self, db):
        self.db = db
        self.rules: List[Rule] = [
            DomainRotationRule(db),
            ResourceAllocationRule(db),
            ErrorEscalationRule(db),
            PriorityBoostRule(db),
            IdleOptimizationRule(db),
        ]

    def has_matching_rule(self, mission: Mission, context: Dict[str, Any]) -> bool:
        """Check if any rule matches"""
        return any(rule.matches(mission, context) for rule in self.rules)

    async def evaluate(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Evaluate rules and return decision"""
        for rule in self.rules:
            if rule.matches(mission, context):
                logger.info(f"Rule matched: {rule.__class__.__name__}")
                return await rule.execute(mission, context)

        raise ValueError("No matching rule found")


# ============================================================================
# LLM REASONER (Layer 3: Complex Context-Aware Decisions)
# ============================================================================

class LLMReasoner:
    """LLM-based complex reasoning for ambiguous decisions"""

    SYSTEM_PROMPT = """You are Rex, the autonomous orchestration system for RekindlePro.

CORE IDENTITY:
- You are an AI orchestrator managing 28 specialized AI agents across 4 crews
- Your purpose: Maximize lead reactivation performance with minimal human intervention
- You operate deterministically when possible, use reasoning only for complex decisions

OPERATIONAL CONSTRAINTS:
1. NEVER execute unsafe actions (delete data, external API calls without validation)
2. ALWAYS respect user preferences and approval settings
3. ALWAYS prioritize domain reputation protection
4. NEVER exceed API rate limits (OpenAI, SendGrid, Twilio)
5. ALWAYS log every decision for audit trail

DECISION FRAMEWORK:
When making decisions, evaluate in this order:
1. Is there a deterministic rule? → Apply it immediately
2. Is there sufficient data? → Use data-driven decision
3. Is uncertainty high? → Request human confirmation
4. Is this a novel situation? → Use LLM reasoning with low temperature

OUTPUT FORMAT:
Always respond in structured JSON:
{
  "action": "action_name",
  "params": {...},
  "reason": "clear explanation",
  "confidence": 0.0-1.0,
  "alternatives_considered": ["alt1", "alt2"]
}

Be concise, technical, and factual. No marketing language."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key

    async def reason(self, mission: Mission, context: Dict[str, Any]) -> Decision:
        """Use LLM to make complex decision"""
        if not self.api_key:
            logger.error("OpenAI API key not configured - cannot use LLM reasoner")
            raise ValueError("LLM reasoner requires OpenAI API key")

        prompt = self._build_prompt(mission, context)

        logger.info(f"LLM reasoning for mission {mission.id}")

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=500
            )

            content = response.choices[0].message.content
            decision_json = json.loads(content)

            return Decision(
                action=decision_json['action'],
                params=decision_json.get('params', {}),
                reason=decision_json['reason'],
                confidence=decision_json['confidence'],
                alternatives_considered=decision_json.get('alternatives_considered', []),
                llm_used=True
            )

        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            # Fallback to safe default
            return Decision(
                action='escalate_to_human',
                params={'error': str(e), 'mission_id': mission.id},
                reason='llm_reasoning_failed',
                confidence=0.0,
                llm_used=True
            )

    def _build_prompt(self, mission: Mission, context: Dict[str, Any]) -> str:
        """Build prompt for LLM"""
        return f"""Mission Context:
ID: {mission.id}
Type: {mission.type}
State: {mission.state}
Priority: {mission.priority}
User ID: {mission.user_id}

Additional Context:
{json.dumps(context, indent=2, default=str)}

What action should Rex take next? Provide your decision in JSON format."""


# ============================================================================
# REX DECISION ENGINE (Main Orchestrator)
# ============================================================================

class RexDecisionEngine:
    """
    Three-layer decision architecture:
    1. State Machine (deterministic, fast) - 80% of decisions
    2. Rule Engine (business logic) - 15% of decisions
    3. LLM Reasoner (complex decisions) - 5% of decisions
    """

    def __init__(self, supabase, openai_api_key: Optional[str] = None):
        self.db = supabase
        self.state_machine = StateMachine()
        self.rule_engine = RuleEngine(supabase)
        self.llm_reasoner = LLMReasoner(openai_api_key)

        self.stats = {
            'state_machine_decisions': 0,
            'rule_engine_decisions': 0,
            'llm_decisions': 0,
        }

    async def decide_next_action(
        self,
        mission: Mission,
        context: Dict[str, Any]
    ) -> Decision:
        """
        Main decision entry point.
        Routes to appropriate decision layer.
        """
        logger.info(
            f"Decision request: Mission {mission.id} ({mission.type}) "
            f"in state {mission.state}"
        )

        # Layer 1: State Machine (deterministic transitions)
        if self.state_machine.can_handle(mission.state, context):
            self.stats['state_machine_decisions'] += 1
            decision = await self.state_machine.decide(mission, context)
            logger.info(f"Decision: State machine → {decision.action}")
            return decision

        # Layer 2: Rule Engine (business logic)
        if self.rule_engine.has_matching_rule(mission, context):
            self.stats['rule_engine_decisions'] += 1
            decision = await self.rule_engine.evaluate(mission, context)
            logger.info(f"Decision: Rule engine → {decision.action}")
            return decision

        # Layer 3: LLM Reasoner (complex reasoning)
        logger.info("No deterministic decision found - using LLM reasoner")
        self.stats['llm_decisions'] += 1
        decision = await self.llm_reasoner.reason(mission, context)
        logger.info(f"Decision: LLM reasoner → {decision.action}")
        return decision

    def get_stats(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        total = sum(self.stats.values())
        return {
            **self.stats,
            'total_decisions': total,
            'state_machine_percentage': (
                (self.stats['state_machine_decisions'] / total * 100)
                if total > 0 else 0
            ),
            'rule_engine_percentage': (
                (self.stats['rule_engine_decisions'] / total * 100)
                if total > 0 else 0
            ),
            'llm_percentage': (
                (self.stats['llm_decisions'] / total * 100)
                if total > 0 else 0
            ),
        }
