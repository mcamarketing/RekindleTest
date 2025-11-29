"""
Rekindle Brain Prompting Utilities

Utilities for crafting effective prompts for the Rekindle Brain LLM model.
Includes prompt templates, formatting helpers, and optimization strategies.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class BrainPromptBuilder:
    """Builder for crafting effective Brain prompts"""

    def __init__(self):
        self.templates = {
            "write_message": self._get_message_template(),
            "plan_actions": self._get_planning_template(),
            "improve_sequence": self._get_sequence_template(),
            "infer_persona": self._get_persona_template()
        }

    def build_prompt(self, capability: str, **kwargs) -> str:
        """Build a prompt for the specified capability"""
        if capability not in self.templates:
            raise ValueError(f"Unknown capability: {capability}")

        template = self.templates[capability]
        return template.format(**kwargs)

    def _get_message_template(self) -> str:
        """Template for message writing"""
        return """You are an expert sales copywriter specializing in B2B SaaS outreach.

CONTEXT:
- Lead: {lead_profile}
- Persona: {persona}
- Channel: {channel}
- Objective: {objective}
- Tone: {tone}
- Previous interactions: {interaction_history}

TASK:
Write a personalized {channel} message that will {objective}.

REQUIREMENTS:
- Keep it under 100 words
- Include specific value proposition
- End with clear call-to-action
- Match the specified tone
- Reference something specific about their company/role

OUTPUT FORMAT:
{{
  "subject": "Email subject line",
  "body": "Message body",
  "call_to_action": "Specific CTA",
  "tone": "actual_tone_used",
  "personalization_score": 0.0-1.0,
  "confidence": 0.0-1.0
}}

Write the message:"""

    def _get_planning_template(self) -> str:
        """Template for action planning"""
        return """You are a strategic sales operations expert.

CURRENT SITUATION:
- Pipeline: {pipeline_state}
- Risks: {risks}
- Time horizon: {time_horizon}
- Business goals: {goals}

TASK:
Recommend the next best actions to optimize revenue outcomes.

CONSIDER:
- Risk mitigation
- Resource efficiency
- Conversion optimization
- Timing and sequencing

OUTPUT FORMAT:
{{
  "actions": [
    {{
      "type": "action_type",
      "priority": "high|medium|low",
      "reason": "why this action",
      "expected_impact": "quantitative impact",
      "timeline": "when to execute"
    }}
  ],
  "expected_outcomes": {{
    "meetings_booked": 0.XX,
    "pipeline_value": XXXX,
    "conversion_rate": 0.XX
  }},
  "risk_assessment": {{
    "overall_risk": "low|medium|high",
    "mitigations": ["mitigation strategies"]
  }},
  "confidence": 0.0-1.0
}}

Plan the optimal actions:"""

    def _get_sequence_template(self) -> str:
        """Template for sequence improvement"""
        return """You are a sales sequence optimization expert.

CURRENT SEQUENCE:
{current_sequence}

PERFORMANCE DATA:
{performance_data}

TARGET IMPROVEMENT: {target_improvement}

TASK:
Analyze the current sequence and suggest improvements to increase reply rates and meetings booked.

OUTPUT FORMAT:
{{
  "analysis": {{
    "strengths": ["what works well"],
    "weaknesses": ["what needs improvement"],
    "bottlenecks": ["where prospects drop off"]
  }},
  "improved_sequence": [
    {{
      "step": 1,
      "channel": "email|linkedin|call",
      "delay_days": 0,
      "content_type": "value_prop|question|social_proof",
      "expected_response_rate": 0.XX
    }}
  ],
  "expected_improvement": {{
    "reply_rate_increase": 0.XX,
    "meeting_rate_increase": 0.XX,
    "overall_conversion_lift": 0.XX
  }},
  "implementation_notes": ["how to roll out changes"],
  "confidence": 0.0-1.0
}}

Improve the sequence:"""

    def _get_persona_template(self) -> str:
        """Template for persona inference"""
        return """You are an expert at B2B buyer persona analysis.

LEAD DATA:
{lead_data}

INTERACTION HISTORY:
{interaction_history}

COMPANY CONTEXT:
{company_context}

TASK:
Infer the most likely buyer persona and communication preferences.

OUTPUT FORMAT:
{{
  "persona": "technical_evaluator|economic_buyer|user_influencer|coach_champion",
  "confidence": 0.0-1.0,
  "traits": [
    {{
      "trait": "decision_style",
      "value": "analytical|intuitive|consensus|authoritative",
      "evidence": "why this trait"
    }}
  ],
  "communication_style": {{
    "preferred_channel": "email|call|linkedin",
    "tone": "formal|casual|technical|business",
    "content_focus": "features|benefits|ROI|relationships",
    "response_time": "immediate|scheduled|delayed"
  }},
  "buying_signals": [
    {{
      "signal": "signal_description",
      "strength": "weak|medium|strong",
      "timeline": "immediate|short_term|long_term"
    }}
  ]
}}

Analyze the persona:"""

class PromptOptimizer:
    """Optimizes prompts for better Brain performance"""

    @staticmethod
    def optimize_for_clarity(prompt: str) -> str:
        """Optimize prompt for clarity"""
        # Add clear section headers
        if "TASK:" not in prompt:
            prompt = "TASK:\n" + prompt

        if "OUTPUT FORMAT:" not in prompt:
            prompt += "\n\nOUTPUT FORMAT:\nProvide response in valid JSON format."

        return prompt

    @staticmethod
    def add_context_boost(prompt: str, context: Dict[str, Any]) -> str:
        """Add context to improve response quality"""
        context_str = f"\n\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"
        return prompt + context_str

    @staticmethod
    def add_examples(prompt: str, examples: List[Dict[str, Any]]) -> str:
        """Add examples to improve consistency"""
        if not examples:
            return prompt

        examples_str = "\n\nEXAMPLES:\n"
        for i, example in enumerate(examples[:3]):  # Limit to 3 examples
            examples_str += f"Example {i+1}:\n{json.dumps(example, indent=2)}\n\n"

        return prompt + examples_str

class ResponseValidator:
    """Validates Brain API responses"""

    @staticmethod
    def validate_json_response(response: str) -> tuple[bool, Any]:
        """Validate that response is valid JSON"""
        try:
            parsed = json.loads(response)
            return True, parsed
        except json.JSONDecodeError as e:
            return False, {"error": f"Invalid JSON: {e}", "raw_response": response}

    @staticmethod
    def validate_response_structure(response: Dict[str, Any], capability: str) -> tuple[bool, List[str]]:
        """Validate response has required structure"""
        required_fields = {
            "write_message": ["subject", "body", "call_to_action"],
            "plan_actions": ["actions", "expected_outcomes"],
            "improve_sequence": ["improved_sequence", "expected_improvement"],
            "infer_persona": ["persona", "traits", "communication_style"]
        }

        if capability not in required_fields:
            return True, []

        missing_fields = []
        for field in required_fields[capability]:
            if field not in response:
                missing_fields.append(field)

        return len(missing_fields) == 0, missing_fields

    @staticmethod
    def sanitize_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response to remove potentially harmful content"""
        # Remove any script tags or dangerous content
        def sanitize_text(text: str) -> str:
            if not isinstance(text, str):
                return text

            # Remove script tags
            text = text.replace("<script", "").replace("</script>", "")
            text = text.replace("javascript:", "")
            text = text.replace("data:", "")

            return text

        sanitized = {}
        for key, value in response.items():
            if isinstance(value, str):
                sanitized[key] = sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = ResponseValidator.sanitize_response(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    ResponseValidator.sanitize_response(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized