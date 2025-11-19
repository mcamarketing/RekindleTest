"""
Command Parser for REX

Parses natural-language user input and maps to structured commands and workflows.
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class CommandParser:
    """Parses user commands into structured actions."""
    
    # Command patterns and their mappings
    COMMAND_PATTERNS = {
        # Campaign commands
        "launch_campaign": [
            r"launch\s+(?:a\s+)?campaign",
            r"start\s+(?:a\s+)?campaign",
            r"create\s+(?:a\s+)?campaign",
            r"send\s+(?:a\s+)?campaign",
            r"run\s+(?:a\s+)?campaign",
            r"execute\s+(?:a\s+)?campaign"
        ],
        "reactivate_leads": [
            r"reactivate\s+(?:leads?|dormant|dead)",
            r"revive\s+(?:leads?|dormant|dead)",
            r"re-engage\s+(?:leads?|dormant)",
            r"warm\s+(?:the\s+)?(?:cold\s+)?list",
            r"reactivation"
        ],
        "analyze_icp": [
            r"analyze\s+icp",
            r"icp\s+analysis",
            r"extract\s+icp",
            r"find\s+my\s+icp"
        ],
        "source_leads": [
            r"source\s+leads?",
            r"find\s+(?:new\s+)?leads?",
            r"get\s+(?:new\s+)?leads?",
            r"discover\s+leads?"
        ],
        "research_leads": [
            r"research\s+(?:my\s+)?leads?",
            r"analyze\s+(?:my\s+)?leads?",
            r"investigate\s+(?:my\s+)?leads?"
        ],
        # Query commands
        "get_kpis": [
            r"how\s+many\s+leads?",
            r"what'?s\s+my\s+status",
            r"show\s+(?:me\s+)?(?:my\s+)?kpis?",
            r"my\s+stats?",
            r"dashboard",
            r"overview"
        ],
        "get_campaign_status": [
            r"campaign\s+status",
            r"my\s+campaigns?",
            r"campaign\s+list",
            r"active\s+campaigns?"
        ],
        "get_lead_details": [
            r"lead\s+details?",
            r"show\s+lead",
            r"lead\s+info",
            r"details?\s+for\s+lead"
        ]
    }
    
    def __init__(self):
        """Initialize command parser."""
        # Compile regex patterns for performance
        self.compiled_patterns = {}
        for command, patterns in self.COMMAND_PATTERNS.items():
            self.compiled_patterns[command] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def parse(self, user_message: str) -> Dict[str, Any]:
        """
        Parse user message into structured command.
        
        Returns:
            {
                "action": "launch_campaign" | "reactivate_leads" | etc.,
                "entities": {...},  # Extracted entities (lead_ids, emails, etc.)
                "confidence": 0.0-1.0,
                "requires_clarification": bool
            }
        """
        user_message_lower = user_message.lower().strip()
        
        # Detect action
        action = None
        confidence = 0.0
        
        for command, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(user_message_lower):
                    action = command
                    confidence = 0.9
                    break
            if action:
                break
        
        # Extract entities
        entities = self._extract_entities(user_message)
        
        # Determine if clarification needed
        requires_clarification = self._needs_clarification(action, entities)
        
        return {
            "action": action,
            "entities": entities,
            "confidence": confidence,
            "requires_clarification": requires_clarification,
            "raw_message": user_message
        }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities (lead IDs, emails, criteria) from message."""
        entities = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message, re.IGNORECASE)
        if emails:
            entities["lead_email"] = emails[0].lower()
        
        # Extract UUIDs (lead IDs)
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuids = re.findall(uuid_pattern, message, re.IGNORECASE)
        if uuids:
            entities["lead_ids"] = uuids
        
        # Extract criteria
        message_lower = message.lower()
        
        # State/location
        states = ["texas", "california", "new york", "florida", "illinois"]
        for state in states:
            if state in message_lower:
                entities["state"] = state.title()
                break
        
        # Industry
        industries = ["tech", "technology", "saas", "software", "finance", "healthcare"]
        for industry in industries:
            if industry in message_lower:
                entities["industry"] = industry
                break
        
        # Hot leads indicator
        if any(word in message_lower for word in ["hot", "high score", "70+", "high-value"]):
            entities["hot_only"] = True
        
        # Campaign name
        if "campaign" in message_lower:
            # Try to extract name after "campaign"
            parts = message_lower.split("campaign")
            if len(parts) > 1:
                name_part = parts[1].strip()
                if len(name_part) > 3 and not any(word in name_part for word in ["for", "with", "to"]):
                    entities["campaign_name"] = name_part.title()
        
        return entities
    
    def _needs_clarification(self, action: Optional[str], entities: Dict[str, Any]) -> bool:
        """
        Determine if clarification is needed.
        
        Only returns True if the request is logically impossible.
        Otherwise, defaults will be used.
        """
        if not action:
            return False  # Will be handled as general query
        
        # Only need clarification for get_lead_details if no email provided
        if action == "get_lead_details" and not entities.get("lead_email"):
            return True
        
        # All other cases can use intelligent defaults
        return False

