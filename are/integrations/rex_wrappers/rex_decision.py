"""
ARE REX Decision Agent Wrapper

Provides real-time decision making, rule engine execution, and LLM reasoning
for the REX (Real-time Execution) system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Types of decisions that can be made"""
    ROUTING = "routing"
    PRIORITIZATION = "prioritization"
    ESCALATION = "escalation"
    OPTIMIZATION = "optimization"
    APPROVAL = "approval"
    RESOURCE_ALLOCATION = "resource_allocation"

class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DecisionRule:
    """Represents a decision rule"""
    rule_id: str
    name: str
    condition: str  # Python expression
    action: str
    priority: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionContext:
    """Context for making a decision"""
    decision_id: str
    decision_type: DecisionType
    input_data: Dict[str, Any]
    rules: List[DecisionRule]
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Decision:
    """Represents a decision made by the system"""
    decision_id: str
    decision_type: DecisionType
    outcome: str
    confidence: ConfidenceLevel
    reasoning: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    made_at: datetime = field(default_factory=datetime.now)
    context: DecisionContext = None

class RexDecisionAgent:
    """ARE REX Decision Agent - Real-time decision making"""

    def __init__(self):
        self.decision_rules: Dict[str, List[DecisionRule]] = {}
        self.decision_history: List[Decision] = []
        self.llm_reasoning_enabled = True
        self.confidence_thresholds = {
            ConfidenceLevel.LOW: 0.3,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.HIGH: 0.8,
            ConfidenceLevel.CRITICAL: 0.95
        }

        # Setup default decision rules
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default decision rules for common scenarios"""
        # Routing rules
        routing_rules = [
            DecisionRule(
                rule_id="route_high_priority",
                name="Route High Priority Tasks",
                condition="input_data.get('priority', 1) >= 3",
                action="route_to_brain",
                priority=10
            ),
            DecisionRule(
                rule_id="route_research_tasks",
                name="Route Research Tasks",
                condition="'research' in input_data.get('capabilities', [])",
                action="route_to_crewai",
                priority=5
            ),
            DecisionRule(
                rule_id="route_complex_tasks",
                name="Route Complex Tasks",
                condition="len(input_data.get('dependencies', [])) > 2",
                action="route_to_brain",
                priority=7
            )
        ]

        # Prioritization rules
        prioritization_rules = [
            DecisionRule(
                rule_id="prioritize_urgent",
                name="Prioritize Urgent Tasks",
                condition="input_data.get('urgency', 'normal') == 'urgent'",
                action="set_priority_high",
                priority=9
            ),
            DecisionRule(
                rule_id="prioritize_revenue_impact",
                name="Prioritize Revenue Impact",
                condition="input_data.get('revenue_impact', 0) > 1000",
                action="set_priority_high",
                priority=8
            )
        ]

        # Escalation rules
        escalation_rules = [
            DecisionRule(
                rule_id="escalate_failures",
                name="Escalate Task Failures",
                condition="input_data.get('failure_count', 0) >= 3",
                action="escalate_to_guardrail",
                priority=10
            ),
            DecisionRule(
                rule_id="escalate_long_running",
                name="Escalate Long Running Tasks",
                condition="input_data.get('execution_time', 0) > 600",
                action="escalate_to_critic",
                priority=7
            )
        ]

        self.decision_rules = {
            "routing": routing_rules,
            "prioritization": prioritization_rules,
            "escalation": escalation_rules
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        decision_type_str = input_data.get('decision_type', 'routing')
        decision_type = DecisionType(decision_type_str.upper())

        logger.info(f"REX Decision Agent making {decision_type.value} decision")

        try:
            decision_context = DecisionContext(
                decision_id=f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                decision_type=decision_type,
                input_data=input_data,
                rules=self.decision_rules.get(decision_type.value, []),
                constraints=input_data.get('constraints', {})
            )

            decision = await self._make_decision(decision_context)

            # Record decision
            self.decision_history.append(decision)

            return {
                "status": "decided",
                "decision": {
                    "decision_id": decision.decision_id,
                    "outcome": decision.outcome,
                    "confidence": decision.confidence.value,
                    "reasoning": decision.reasoning,
                    "execution_plan": decision.execution_plan
                }
            }

        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            raise

    async def _make_decision(self, context: DecisionContext) -> Decision:
        """Make a decision based on context"""
        # Apply rule-based decisions first
        rule_based_decision = await self._apply_rules(context)

        if rule_based_decision:
            return rule_based_decision

        # Fall back to LLM reasoning if enabled
        if self.llm_reasoning_enabled:
            return await self._llm_reasoning_decision(context)

        # Default decision
        return await self._default_decision(context)

    async def _apply_rules(self, context: DecisionContext) -> Optional[Decision]:
        """Apply decision rules to context"""
        applicable_rules = []

        for rule in context.rules:
            if not rule.enabled:
                continue

            try:
                # Evaluate condition (simple eval for now - in production use safe evaluation)
                condition_met = self._evaluate_condition(rule.condition, context.input_data)

                if condition_met:
                    applicable_rules.append(rule)

            except Exception as e:
                logger.warning(f"Failed to evaluate rule {rule.rule_id}: {e}")
                continue

        if not applicable_rules:
            return None

        # Sort by priority and take highest
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        best_rule = applicable_rules[0]

        # Calculate confidence based on rule priority and number of matching rules
        confidence_score = min(0.9, 0.5 + (best_rule.priority * 0.1) + (len(applicable_rules) * 0.05))
        confidence_level = self._get_confidence_level(confidence_score)

        decision = Decision(
            decision_id=context.decision_id,
            decision_type=context.decision_type,
            outcome=best_rule.action,
            confidence=confidence_level,
            reasoning=f"Applied rule '{best_rule.name}' with priority {best_rule.priority}",
            alternatives=[{"rule": r.rule_id, "action": r.action} for r in applicable_rules[1:]],
            context=context
        )

        return decision

    async def _llm_reasoning_decision(self, context: DecisionContext) -> Decision:
        """Use LLM reasoning for decision making"""
        # Placeholder for LLM integration
        # In production, this would call an LLM with structured prompts

        prompt = self._build_decision_prompt(context)

        # Mock LLM response - replace with actual LLM call
        llm_response = await self._mock_llm_call(prompt)

        try:
            decision_data = json.loads(llm_response)
            outcome = decision_data.get('outcome', 'default_action')
            reasoning = decision_data.get('reasoning', 'LLM-based decision')
            confidence_score = decision_data.get('confidence', 0.7)

        except json.JSONDecodeError:
            outcome = 'default_action'
            reasoning = 'Failed to parse LLM response'
            confidence_score = 0.3

        confidence_level = self._get_confidence_level(confidence_score)

        decision = Decision(
            decision_id=context.decision_id,
            decision_type=context.decision_type,
            outcome=outcome,
            confidence=confidence_level,
            reasoning=reasoning,
            context=context
        )

        return decision

    async def _default_decision(self, context: DecisionContext) -> Decision:
        """Make a default decision when other methods fail"""
        default_outcomes = {
            DecisionType.ROUTING: "route_to_brain",
            DecisionType.PRIORITIZATION: "set_priority_medium",
            DecisionType.ESCALATION: "continue_normal",
            DecisionType.OPTIMIZATION: "no_change",
            DecisionType.APPROVAL: "approve",
            DecisionType.RESOURCE_ALLOCATION: "standard_allocation"
        }

        outcome = default_outcomes.get(context.decision_type, "default_action")

        decision = Decision(
            decision_id=context.decision_id,
            decision_type=context.decision_type,
            outcome=outcome,
            confidence=ConfidenceLevel.LOW,
            reasoning="Default decision due to insufficient information",
            context=context
        )

        return decision

    def _evaluate_condition(self, condition: str, input_data: Dict[str, Any]) -> bool:
        """Safely evaluate a condition expression"""
        # Simple evaluation - in production use a safe evaluation library
        try:
            # Create a restricted globals dict
            restricted_globals = {
                '__builtins__': {},
                'input_data': input_data,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            }

            # Add common methods
            restricted_globals.update({
                name: getattr(input_data, name)
                for name in ['get', 'keys', 'values', 'items']
                if hasattr(input_data, name)
            })

            result = eval(condition, restricted_globals)
            return bool(result)

        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False

    def _get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Get confidence level from score"""
        if confidence_score >= self.confidence_thresholds[ConfidenceLevel.CRITICAL]:
            return ConfidenceLevel.CRITICAL
        elif confidence_score >= self.confidence_thresholds[ConfidenceLevel.HIGH]:
            return ConfidenceLevel.HIGH
        elif confidence_score >= self.confidence_thresholds[ConfidenceLevel.MEDIUM]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _build_decision_prompt(self, context: DecisionContext) -> str:
        """Build a prompt for LLM decision making"""
        return f"""
        Make a {context.decision_type.value} decision based on the following context:

        Input Data: {json.dumps(context.input_data, indent=2)}

        Decision Type: {context.decision_type.value}

        Available Rules: {[rule.name for rule in context.rules]}

        Constraints: {json.dumps(context.constraints, indent=2)}

        Please provide a JSON response with:
        - outcome: the decision outcome
        - reasoning: explanation of the decision
        - confidence: confidence score (0-1)
        - alternatives: list of alternative options considered
        """

    async def _mock_llm_call(self, prompt: str) -> str:
        """Mock LLM call - replace with actual LLM integration"""
        # Simulate processing time
        await asyncio.sleep(0.1)

        # Mock responses based on decision type
        if "routing" in prompt.lower():
            return json.dumps({
                "outcome": "route_to_brain",
                "reasoning": "Task requires strategic analysis and content generation",
                "confidence": 0.8,
                "alternatives": ["route_to_crewai", "route_to_services"]
            })
        elif "prioritization" in prompt.lower():
            return json.dumps({
                "outcome": "set_priority_high",
                "reasoning": "Task has high revenue impact and urgency",
                "confidence": 0.9,
                "alternatives": ["set_priority_medium"]
            })
        else:
            return json.dumps({
                "outcome": "default_action",
                "reasoning": "Standard decision for this scenario",
                "confidence": 0.6,
                "alternatives": []
            })

    async def add_decision_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new decision rule"""
        rule = DecisionRule(
            rule_id=rule_data['rule_id'],
            name=rule_data['name'],
            condition=rule_data['condition'],
            action=rule_data['action'],
            priority=rule_data.get('priority', 1),
            enabled=rule_data.get('enabled', True),
            metadata=rule_data.get('metadata', {})
        )

        decision_type = rule_data.get('decision_type', 'routing')
        if decision_type not in self.decision_rules:
            self.decision_rules[decision_type] = []

        self.decision_rules[decision_type].append(rule)

        logger.info(f"Added decision rule: {rule.rule_id}")

        return {
            "status": "added",
            "rule_id": rule.rule_id
        }

    async def update_decision_rule(self, rule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing decision rule"""
        for rule_list in self.decision_rules.values():
            for rule in rule_list:
                if rule.rule_id == rule_id:
                    for key, value in updates.items():
                        if hasattr(rule, key):
                            setattr(rule, key, value)

                    logger.info(f"Updated decision rule: {rule_id}")
                    return {"status": "updated", "rule_id": rule_id}

        raise ValueError(f"Rule {rule_id} not found")

    async def get_decision_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        recent_decisions = self.decision_history[-limit:]

        return [
            {
                "decision_id": d.decision_id,
                "decision_type": d.decision_type.value,
                "outcome": d.outcome,
                "confidence": d.confidence.value,
                "reasoning": d.reasoning,
                "made_at": d.made_at.isoformat()
            }
            for d in recent_decisions
        ]

    async def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision-making statistics"""
        if not self.decision_history:
            return {"total_decisions": 0}

        decisions_by_type = {}
        confidence_distribution = {
            "low": 0, "medium": 0, "high": 0, "critical": 0
        }

        for decision in self.decision_history:
            # Count by type
            dt = decision.decision_type.value
            decisions_by_type[dt] = decisions_by_type.get(dt, 0) + 1

            # Count by confidence
            conf = decision.confidence.value
            confidence_distribution[conf] += 1

        return {
            "total_decisions": len(self.decision_history),
            "decisions_by_type": decisions_by_type,
            "confidence_distribution": confidence_distribution,
            "average_confidence": sum(
                self.confidence_thresholds[ConfidenceLevel(d.confidence.value.upper())]
                for d in self.decision_history
            ) / len(self.decision_history)
        }