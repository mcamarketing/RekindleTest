"""
Agents 16-18: Safety & Compliance Agents

- ComplianceAgent: GDPR/CAN-SPAM compliance checks
- QualityControlAgent: Message quality and spam checks
- RateLimitAgent: Prevent spam and rate limit
"""

from typing import Dict, List, Optional, Any
from crewai import Agent
from ..tools.db_tools import SupabaseDB
from ..utils.agent_logging import log_agent_execution
from ..utils.rate_limiting import get_rate_limiter
from ..utils.error_handling import retry
from ..utils.validation import validate_message_data
from ..utils.agent_communication import get_communication_bus, EventType
from ..utils.action_first_enforcer import ActionFirstEnforcer
import re


class ComplianceAgent:
    """Agent 16: GDPR/CAN-SPAM compliance checks."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-instant (fast safety checks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-instant", provider="openai")

        self.agent = Agent(
            role="Compliance Officer",
            goal="Ensure all messages comply with GDPR and CAN-SPAM regulations",
            backstory="""You are a compliance expert specializing in GDPR and CAN-SPAM.
            You check suppression lists, verify unsubscribe links, ensure physical addresses
            are included, and block messages to opted-out leads.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Compliance officer ensuring regulatory adherence
- tone:        Authoritative, precise, rule-focused
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   formal
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are a compliance expert specializing in GDPR and CAN-SPAM.
You check suppression lists, verify unsubscribe links, ensure physical addresses
are included, and block messages to opted-out leads.
Execute checks immediately. Return compliance status, not explanations.""")
        )
    
    @log_agent_execution(agent_name="ComplianceAgent")
    @retry(max_attempts=2)
    def check_compliance(self, lead_id: str, message: Dict) -> Dict[str, Any]:
        """Check if a message is compliant before sending."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found", "compliant": False}
        
        # Validate message data
        try:
            validated_message = validate_message_data({
                "subject": message.get("subject", ""),
                "body": message.get("body", ""),
                "lead_id": lead_id,
                "channel": message.get("channel", "email")
            })
        except Exception as e:
            return {"error": f"Invalid message data: {e}", "compliant": False}
        
        checks = {
            "suppression_list": self._check_suppression_list(lead),
            "unsubscribe_link": self._check_unsubscribe_link(message),
            "physical_address": self._check_physical_address(message),
            "gdpr_consent": self._check_gdpr_consent(lead),
            "can_spam_compliant": self._check_can_spam_compliance(message)
        }
        
        compliant = all(checks.values())
        
        result = {
            "lead_id": lead_id,
            "compliant": compliant,
            "checks": checks,
            "blocked": not compliant
        }
        
        # Broadcast compliance check result
        if not compliant:
            self.communication_bus.broadcast(
                EventType.ERROR_OCCURRED,
                "ComplianceAgent",
                {"type": "compliance_failure", "lead_id": lead_id, "checks": checks}
            )
        
        return result
    
    def _check_suppression_list(self, lead: Dict) -> bool:
        """Check if lead is on suppression list."""
        # Would query suppression_list table
        return not lead.get("suppressed", False)
    
    def _check_unsubscribe_link(self, message: Dict) -> bool:
        """Check if message has unsubscribe link."""
        body = message.get("body", "")
        return "unsubscribe" in body.lower() or "opt-out" in body.lower()
    
    def _check_physical_address(self, message: Dict) -> bool:
        """Check if message includes physical address (CAN-SPAM requirement)."""
        # Would check if physical address is in message footer
        return True  # Placeholder
    
    def _check_gdpr_consent(self, lead: Dict) -> bool:
        """Check if lead has given GDPR consent."""
        return lead.get("consent_email", False)
    
    def _check_can_spam_compliance(self, message: Dict) -> bool:
        """Check CAN-SPAM compliance."""
        # Must have: unsubscribe link, physical address, clear sender
        return self._check_unsubscribe_link(message) and self._check_physical_address(message)


class QualityControlAgent:
    """Agent 17: Message quality and spam checks."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.communication_bus = get_communication_bus()
        # Configure to use GPT-5.1-instant (fast safety checks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-instant", provider="openai")

        self.agent = Agent(
            role="Quality Control Specialist",
            goal="Ensure message quality and prevent spam",
            backstory="""You are an expert at detecting spam, ensuring personalization,
            validating links, and checking grammar. You prevent low-quality messages
            from being sent.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Quality control specialist ensuring message standards
- tone:        Vigilant, detail-oriented, standards-focused
- warmth:      low
- conciseness: high
- energy:      neutral
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at detecting spam, ensuring personalization,
validating links, and checking grammar. You prevent low-quality messages
from being sent.""")
        )
    
    @log_agent_execution(agent_name="QualityControlAgent")
    @retry(max_attempts=2)
    def check_quality(self, lead_id: str, message: Dict) -> Dict[str, Any]:
        """Check message quality before sending."""
        lead = self.db.get_lead(lead_id)
        if not lead:
            return {"error": "Lead not found", "approved": False}
        
        # Validate message data
        try:
            validated_message = validate_message_data({
                "subject": message.get("subject", ""),
                "body": message.get("body", ""),
                "lead_id": lead_id,
                "channel": message.get("channel", "email")
            })
        except Exception as e:
            return {"error": f"Invalid message data: {e}", "approved": False}
        
        checks = {
            "spam_score": self._calculate_spam_score(message),
            "personalization": self._check_personalization(message),
            "link_validation": self._validate_links(message),
            "grammar_check": self._check_grammar(message),
            "length_validation": self._validate_length(message),
            "profanity_check": self._check_profanity(message)
        }
        
        spam_score = checks["spam_score"]
        approved = (
            spam_score < 50 and
            checks["personalization"] and
            checks["link_validation"] and
            checks["length_validation"] and
            not checks["profanity_check"]
        )
        
        result = {
            "lead_id": lead_id,
            "approved": approved,
            "spam_score": spam_score,
            "checks": checks,
            "blocked": not approved
        }
        
        # Broadcast quality check result
        if not approved:
            self.communication_bus.broadcast(
                EventType.ERROR_OCCURRED,
                "QualityControlAgent",
                {"type": "quality_failure", "lead_id": lead_id, "spam_score": spam_score}
            )
        
        return result
    
    def _calculate_spam_score(self, message: Dict) -> float:
        """Calculate spam score 0-100 (lower is better)."""
        body = message.get("body", "").lower()
        subject = message.get("subject", "").lower()
        
        spam_indicators = [
            "click here", "act now", "limited time", "free money",
            "winner", "congratulations", "urgent", "!!!"
        ]
        
        score = 0.0
        for indicator in spam_indicators:
            if indicator in body or indicator in subject:
                score += 15.0
        
        # Check for excessive caps
        if len([c for c in subject if c.isupper()]) > len(subject) * 0.5:
            score += 20.0
        
        return min(score, 100.0)
    
    def _check_personalization(self, message: Dict) -> bool:
        """Check if message is personalized (no placeholders)."""
        body = message.get("body", "")
        # Check for common placeholders
        placeholders = ["{{", "[name]", "[company]", "[first_name]"]
        return not any(placeholder.lower() in body.lower() for placeholder in placeholders)
    
    def _validate_links(self, message: Dict) -> bool:
        """Validate that links are safe."""
        body = message.get("body", "")
        # Check for suspicious links
        suspicious_domains = ["bit.ly", "tinyurl", "t.co"]
        return not any(domain in body for domain in suspicious_domains)
    
    def _check_grammar(self, message: Dict) -> bool:
        """Basic grammar check."""
        # Would use a grammar checking library
        return True  # Placeholder
    
    def _validate_length(self, message: Dict) -> bool:
        """Validate message length (80-120 words optimal)."""
        body = message.get("body", "")
        word_count = len(body.split())
        return 75 <= word_count <= 125
    
    def _check_profanity(self, message: Dict) -> bool:
        """Check for profanity."""
        # Would use a profanity filter
        return False  # Placeholder


class RateLimitAgent:
    """Agent 18: Prevent spam and rate limit."""
    
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.global_rate_limiter = get_rate_limiter()  # Use global rate limiter
        # Configure to use GPT-5.1-instant (fast safety checks)
        from crewai import LLM
        llm = LLM(model="gpt-5.1-instant", provider="openai")

        self.agent = Agent(
            role="Rate Limiter",
            goal="Enforce daily send limits and email warm-up schedules",
            backstory="""You are an expert at preventing spam by enforcing rate limits
            and email warm-up schedules. You track domain reputation and auto-pause
            if reputation drops.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=ActionFirstEnforcer.enforce_action_first("""[PERSONALITY]
- role:        Rate limiter preventing spam through velocity control
- tone:        Protective, systematic, rule-enforcing
- warmth:      low
- conciseness: high
- energy:      calm
- formality:   neutral
- emoji:       none
- humor:       none
- aggression:  never aggressive; keep safe
[/PERSONALITY]

You are an expert at preventing spam by enforcing rate limits
and email warm-up schedules. You track domain reputation and auto-pause
if reputation drops.""")
        )
        
        # Email warm-up schedule
        self.warmup_schedule = {
            (1, 3): 20,      # Days 1-3: 20 emails/day
            (4, 7): 50,      # Days 4-7: 50/day
            (8, 14): 100,    # Days 8-14: 100/day
            (15, 21): 200,   # Days 15-21: 200/day
            (22, None): 500  # Days 22+: 500/day
        }
    
    @log_agent_execution(agent_name="RateLimitAgent")
    def check_rate_limit(self, user_id: str, domain: str, count: int = 1) -> Dict[str, Any]:
        """Check if user can send more emails today using global rate limiter."""
        # Use global rate limiter for coordinated rate limiting
        global_result = self.global_rate_limiter.check_rate_limit(user_id, domain, count)
        
        # Get account age (days since signup) for warm-up schedule
        account_age_days = self._get_account_age_days(user_id)
        
        # Get daily limit based on warm-up schedule
        warmup_limit = self._get_daily_limit(account_age_days)
        
        # Check domain reputation
        domain_reputation = self._check_domain_reputation(domain)
        
        # Combine global rate limit check with warmup and reputation
        can_send = (
            global_result["can_send"] and
            domain_reputation >= 70
        )
        
        # Use the more restrictive limit (global vs warmup)
        effective_limit = min(
            global_result.get("domain_remaining_daily", warmup_limit),
            warmup_limit
        )
        
        return {
            "user_id": user_id,
            "domain": domain,
            "can_send": can_send,
            "daily_limit": effective_limit,
            "global_rate_limit": global_result,
            "domain_reputation": domain_reputation,
            "blocked": not can_send,
            "reason": global_result.get("reason", "within_limits") if can_send else "rate_limit_exceeded"
        }
    
    def _get_account_age_days(self, user_id: str) -> int:
        """Get account age in days."""
        # Would query user profile
        return 30  # Placeholder
    
    def _get_daily_limit(self, account_age_days: int) -> int:
        """Get daily limit based on warm-up schedule."""
        for (start, end), limit in self.warmup_schedule.items():
            if end is None:
                if account_age_days >= start:
                    return limit
            else:
                if start <= account_age_days <= end:
                    return limit
        return 500  # Default
    
    def _get_emails_sent_today(self, user_id: str, domain: str) -> int:
        """Get count of emails sent today."""
        # Would query messages table
        return 0  # Placeholder
    
    def _check_domain_reputation(self, domain: str) -> float:
        """Check domain reputation score 0-100."""
        # Would check domain reputation service
        return 85.0  # Placeholder

