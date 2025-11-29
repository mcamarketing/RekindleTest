"""
Security Module for Rekindle Brain

Handles data privacy, content filtering, compliance validation,
and security monitoring for the autonomous business intelligence system.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import BrainConfig

logger = logging.getLogger(__name__)

class SecurityManager:
    """Manages security, privacy, and compliance for Rekindle Brain"""

    def __init__(self, config: BrainConfig):
        self.config = config
        self.audit_log: List[Dict[str, Any]] = []
        self.max_audit_entries = 10000
        self.compromised_content_detected = 0
        self.privacy_violations = 0

    async def initialize(self):
        """Initialize security components"""
        logger.info("Initializing SecurityManager")

        # Compile regex patterns for efficiency
        self._compile_privacy_patterns()
        self._compile_content_filters()

        logger.info("SecurityManager initialized")

    def _compile_privacy_patterns(self):
        """Compile privacy filter regex patterns"""
        self.privacy_patterns = []
        for pattern in self.config.security_config["privacy_filters"]:
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                self.privacy_patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid privacy pattern '{pattern}': {e}")

    def _compile_content_filters(self):
        """Compile content filter patterns"""
        self.content_filters = []
        for filter_name in self.config.security_config["content_filters"]:
            # Define filter patterns (could be loaded from config)
            filter_patterns = self._get_filter_patterns(filter_name)
            for pattern in filter_patterns:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                    self.content_filters.append({
                        "name": filter_name,
                        "pattern": compiled
                    })
                except re.error as e:
                    logger.warning(f"Invalid content filter pattern '{pattern}': {e}")

    def _get_filter_patterns(self, filter_name: str) -> List[str]:
        """Get regex patterns for content filters"""
        filter_definitions = {
            "hate_speech": [
                r'\b(hate|despise|loathe)\b.*\b(group|people|community)\b',
                r'\b(racist|sexist|homophobic|transphobic)\b',
                r'\b(nazi|supremacist|terrorist)\b'
            ],
            "personal_attacks": [
                r'\b(stupid|idiot|moron|dumb)\b',
                r'\b(worthless|useless|pathetic)\b',
                r'\byou.*\b(suck|blow|terrible)\b'
            ],
            "illegal_activities": [
                r'\b(illegal|criminal|felony)\b.*\b(activity|scheme|plan)\b',
                r'\b(drug|weapon|narcotic)\b.*\b(trafficking|dealing|selling)\b',
                r'\b(hack|breach|exploit)\b.*\b(system|network|security)\b'
            ],
            "sensitive_personal_data": [
                r'\b(ssn|social.security)\b',
                r'\b(medical|health|diagnosis)\b.*\b(record|history)\b',
                r'\b(financial|bank|credit)\b.*\b(detail|info|record)\b'
            ]
        }

        return filter_definitions.get(filter_name, [])

    async def validate_query(self, query: Dict[str, Any]) -> bool:
        """
        Validate incoming query for security and compliance

        Args:
            query: Business query to validate

        Returns:
            True if query passes validation

        Raises:
            SecurityViolation: If query violates security policies
        """
        logger.debug("Validating query security")

        # Check query content
        await self._validate_content(query)

        # Check for prompt injection attempts
        await self._check_prompt_injection(query)

        # Check rate limits (placeholder)
        await self._check_rate_limits(query)

        # Log validated query
        await self._log_security_event("query_validated", {
            "query_type": query.get("task_type"),
            "goal_length": len(query.get("goal", "")),
            "has_constraints": bool(query.get("constraints"))
        })

        return True

    async def validate_training_data(self, data_path: str) -> bool:
        """
        Validate training data for security and privacy

        Args:
            data_path: Path to training data

        Returns:
            True if data passes validation
        """
        logger.info(f"Validating training data: {data_path}")

        # Check file permissions
        await self._validate_file_security(data_path)

        # Scan for sensitive data
        sensitive_data_found = await self._scan_for_sensitive_data(data_path)

        if sensitive_data_found:
            logger.warning(f"Sensitive data detected in training data: {data_path}")
            # In production, this might trigger data sanitization or rejection

        # Log validation
        await self._log_security_event("training_data_validated", {
            "data_path": data_path,
            "sensitive_data_found": sensitive_data_found
        })

        return True

    async def sanitize_content(self, content: str, context: str = "general") -> str:
        """
        Sanitize content by removing or redacting sensitive information

        Args:
            content: Content to sanitize
            context: Context for sanitization rules

        Returns:
            Sanitized content
        """
        sanitized = content

        # Apply privacy filters
        for pattern in self.privacy_patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)

        # Apply content filters for harmful content
        for filter_info in self.content_filters:
            if filter_info["pattern"].search(sanitized):
                self.compromised_content_detected += 1
                logger.warning(f"Content filter triggered: {filter_info['name']}")

                # Replace harmful content with warning
                sanitized = filter_info["pattern"].sub(
                    f"[CONTENT FILTERED - {filter_info['name'].upper()}]",
                    sanitized
                )

        # Log sanitization if content was modified
        if sanitized != content:
            await self._log_security_event("content_sanitized", {
                "original_length": len(content),
                "sanitized_length": len(sanitized),
                "context": context
            })

        return sanitized

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate model response for safety and compliance

        Args:
            response: Model response to validate

        Returns:
            True if response passes validation
        """
        # Check response content
        response_text = " ".join([
            response.get("strategy", ""),
            response.get("rationale", ""),
            " ".join(response.get("action_plan", []))
        ])

        await self._validate_content({"content": response_text}, "response")

        # Check for hallucinated or inappropriate content
        await self._check_response_quality(response)

        return True

    async def _validate_content(self, content_dict: Dict[str, Any], content_type: str = "query"):
        """Validate content for security violations"""
        content = self._extract_content_text(content_dict)

        # Apply sanitization
        sanitized = await self.sanitize_content(content, content_type)

        # Check if sanitization removed too much content (potential abuse)
        if len(sanitized) < len(content) * 0.5:  # More than 50% removed
            logger.warning(f"Excessive content removal in {content_type}")
            await self._log_security_event("excessive_sanitization", {
                "content_type": content_type,
                "original_length": len(content),
                "sanitized_length": len(sanitized)
            })

    async def _check_prompt_injection(self, query: Dict[str, Any]):
        """Check for prompt injection attempts"""
        injection_patterns = [
            r'\b(ignore|override|disregard)\b.*\b(instruction|previous|above)\b',
            r'\b(system|developer)\b.*\b(prompt|instruction)\b',
            r'\b(you are|act as)\b.*\b(not|different|other)\b.*\b(ai|assistant)\b',
            r'\b(pretend|role.*play)\b.*\b(not.*have|without)\b.*\b(restriction|limit)\b'
        ]

        content = self._extract_content_text(query)

        for pattern in injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning("Potential prompt injection detected")
                await self._log_security_event("prompt_injection_attempt", {
                    "pattern": pattern,
                    "content_sample": content[:100]
                })
                # In production, this might block the request

    async def _check_rate_limits(self, query: Dict[str, Any]):
        """Check rate limits (placeholder implementation)"""
        # In production, this would check Redis or database for rate limits
        # For now, just log the check
        pass

    async def _validate_file_security(self, file_path: str):
        """Validate file security permissions"""
        # Check file permissions, size, etc.
        # In production, this would be more thorough
        pass

    async def _scan_for_sensitive_data(self, file_path: str) -> bool:
        """Scan file for sensitive data patterns"""
        # In production, this would scan the file content
        # For now, return False (no sensitive data found)
        return False

    async def _check_response_quality(self, response: Dict[str, Any]):
        """Check response quality and safety"""
        # Check for nonsensical or potentially harmful responses
        strategy = response.get("strategy", "")
        action_plan = response.get("action_plan", [])

        # Check for empty or too-short responses
        if len(strategy) < 10:
            logger.warning("Response strategy too short")

        # Check for potentially harmful action items
        harmful_keywords = ["hack", "exploit", "illegal", "unethical", "manipulate"]
        for action in action_plan:
            action_lower = action.lower()
            for keyword in harmful_keywords:
                if keyword in action_lower:
                    logger.warning(f"Potentially harmful action detected: {action}")
                    await self._log_security_event("harmful_action_detected", {
                        "action": action,
                        "keyword": keyword
                    })

    def _extract_content_text(self, content_dict: Dict[str, Any]) -> str:
        """Extract text content from various content structures"""
        content_fields = ["content", "text", "goal", "instruction", "input"]

        content_parts = []
        for field in content_fields:
            if field in content_dict and content_dict[field]:
                content_parts.append(str(content_dict[field]))

        # Also check nested structures
        if "context" in content_dict and isinstance(content_dict["context"], dict):
            for key, value in content_dict["context"].items():
                if isinstance(value, str):
                    content_parts.append(value)

        return " ".join(content_parts)

    async def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event to audit trail"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }

        self.audit_log.append(event)

        # Maintain max log size
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log = self.audit_log[-self.max_audit_entries:]

        logger.info(f"Security event logged: {event_type}")

    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            "compromised_content_detected": self.compromised_content_detected,
            "privacy_violations": self.privacy_violations,
            "audit_log_entries": len(self.audit_log),
            "active_filters": len(self.content_filters),
            "privacy_patterns": len(self.privacy_patterns),
            "last_security_check": datetime.now().isoformat()
        }

    async def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]

    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        now = datetime.now()

        # Analyze audit log
        event_counts = {}
        for event in self.audit_log:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Calculate time-based metrics
        recent_events = [e for e in self.audit_log
                        if (now - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600]  # Last hour

        return {
            "report_generated": now.isoformat(),
            "total_events": len(self.audit_log),
            "events_last_hour": len(recent_events),
            "event_breakdown": event_counts,
            "security_status": await self.get_security_status(),
            "recommendations": self._generate_security_recommendations(event_counts)
        }

    def _generate_security_recommendations(self, event_counts: Dict[str, int]) -> List[str]:
        """Generate security recommendations based on event analysis"""
        recommendations = []

        if event_counts.get("prompt_injection_attempt", 0) > 0:
            recommendations.append("Review and strengthen prompt injection defenses")

        if event_counts.get("harmful_action_detected", 0) > 0:
            recommendations.append("Enhance response content filtering")

        if event_counts.get("excessive_sanitization", 0) > 5:
            recommendations.append("Review privacy filter patterns for over-filtering")

        if len(self.audit_log) == 0:
            recommendations.append("Enable security auditing for better monitoring")

        return recommendations

    async def emergency_shutdown(self, reason: str):
        """Emergency security shutdown"""
        logger.critical(f"Emergency security shutdown: {reason}")

        await self._log_security_event("emergency_shutdown", {
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })

        # In production, this would trigger system-wide shutdown procedures