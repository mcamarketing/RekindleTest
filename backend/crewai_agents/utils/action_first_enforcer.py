"""
Action-First Enforcer Utility

Ensures all agents follow action-first, execution-focused behavior.
Removes demo/sales/tutorial patterns from responses.
"""

from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ActionFirstEnforcer:
    """Enforces action-first behavior across all agents."""
    
    # Patterns to remove (demo/sales/tutorial language)
    DEMO_PATTERNS = [
        r"would you like",
        r"can i help",
        r"let me help",
        r"i can help",
        r"i'll help",
        r"step-by-step",
        r"here's how",
        r"here is how",
        r"tutorial",
        r"guide",
        r"instructions",
        r"how to",
        r"would you like me to",
        r"should i",
        r"do you want",
        r"would you like to",
        r"i can show you",
        r"let me show you",
        r"i'll show you",
        r"i can explain",
        r"let me explain",
        r"i'll explain",
        r"demo",
        r"demonstration",
        r"example",
        r"for example",
        r"here's an example",
        r"sales",
        r"pricing",
        r"upgrade",
        r"subscribe",
        r"sign up",
        r"onboarding",
        r"welcome",
        r"getting started"
    ]
    
    # Response prefixes to remove (conversational fluff)
    FLUFF_PREFIXES = [
        "Good morning",
        "Good afternoon",
        "Good evening",
        "Hello",
        "Hi there",
        "Hi!",
        "Hey",
        "Sure!",
        "Absolutely!",
        "Of course!",
        "I'd be happy to",
        "I'm happy to",
        "I'll be glad to",
        "Great question",
        "That's a great question",
        "I understand",
        "I see",
        "Let me",
        "I'll",
        "I can",
        "I will",
        "I'm going to",
        "I'm here to",
        "I'm ready to"
    ]
    
    @staticmethod
    def clean_response(response: str) -> str:
        """
        Clean response to remove demo/sales/tutorial language.
        
        Returns concise, action-first response.
        """
        if not response:
            return response
        
        # Remove fluff prefixes
        response_clean = response.strip()
        for prefix in ActionFirstEnforcer.FLUFF_PREFIXES:
            if response_clean.startswith(prefix):
                # Remove prefix and any following punctuation/whitespace
                response_clean = re.sub(rf"^{re.escape(prefix)}[.,!?\s]*", "", response_clean, flags=re.IGNORECASE).strip()
        
        # Remove demo patterns (replace with action)
        for pattern in ActionFirstEnforcer.DEMO_PATTERNS:
            response_clean = re.sub(rf"\b{pattern}\b[^.]*\.?", "", response_clean, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        response_clean = re.sub(r"\s+", " ", response_clean).strip()
        
        # Remove trailing punctuation if response is too short (likely fluff)
        if len(response_clean) < 10:
            response_clean = response_clean.rstrip(".,!?")
        
        return response_clean if response_clean else response
    
    @staticmethod
    def enforce_action_first(system_prompt: str) -> str:
        """
        Add action-first directives to system prompt.
        """
        action_first_directive = """

ACTION-FIRST PROTOCOL (MANDATORY):
- Execute actions immediately. Never ask for permission or confirmation.
- Never provide step-by-step guides unless explicitly requested with "explain" or "how".
- Never act like a demo, sales, or tutorial bot.
- Responses must be concise and actionable:
  • "Campaign launched."
  • "Lead research complete."
  • "Sequence deployed."
  • "Done."
- Never use phrases like "would you like", "can I help", "let me help", "step-by-step", "tutorial", "guide".
- Confirm success AFTER execution, not before.
- Only ask for clarification if the request is logically impossible.
"""
        
        # Add directive before any existing instructions
        if "[PERSONALITY]" in system_prompt:
            # Insert after PERSONALITY block
            parts = system_prompt.split("[/PERSONALITY]")
            if len(parts) > 1:
                return parts[0] + "[/PERSONALITY]" + action_first_directive + parts[1]
        
        # Otherwise, prepend to system prompt
        return action_first_directive + "\n" + system_prompt
    
    @staticmethod
    def validate_response(response: str) -> bool:
        """
        Validate that response follows action-first protocol.
        
        Returns True if response is action-first, False if it contains demo/sales language.
        """
        if not response:
            return True
        
        response_lower = response.lower()
        
        # Check for demo patterns
        for pattern in ActionFirstEnforcer.DEMO_PATTERNS:
            if re.search(rf"\b{pattern}\b", response_lower):
                logger.warning(f"Response contains demo pattern '{pattern}': {response[:100]}")
                return False
        
        # Check for fluff prefixes
        for prefix in ActionFirstEnforcer.FLUFF_PREFIXES:
            if response_lower.startswith(prefix.lower()):
                logger.warning(f"Response starts with fluff prefix '{prefix}': {response[:100]}")
                return False
        
        return True

