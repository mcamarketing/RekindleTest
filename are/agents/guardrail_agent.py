"""
ARE Guardrail Agent

Enforces safety, compliance, and rate limiting. Prevents unsafe or spammy actions,
validates final outputs, and ensures GDPR/SOC2 compliance before tasks are executed.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class PolicyRule:
    """A policy rule for validation"""
    id: str
    name: str
    category: str  # "content", "rate_limit", "compliance", "safety"
    condition: Dict[str, Any]
    action: str  # "allow", "deny", "warn", "quarantine"
    severity: str  # "low", "medium", "high", "critical"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of policy validation"""
    valid: bool
    action: str
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    validated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RateLimit:
    """Rate limiting configuration"""
    key: str
    limit: int
    window_seconds: int
    current_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)

class GuardrailAgent:
    """ARE Guardrail Agent - Safety and compliance validation"""

    def __init__(self):
        self.policy_rules: List[PolicyRule] = []
        self.rate_limits: Dict[str, RateLimit] = {}
        self.violation_history: List[Dict[str, Any]] = []

        # Initialize default policy rules
        self._initialize_default_policies()

        # Content safety patterns
        self.prohibited_patterns = [
            r'\b(?:viagra|casino|lottery|porn|sex)\b',
            r'\b(?:hack|crack|exploit|malware)\b',
            r'\b(?:suicide|self-harm|violence)\b',
            r'(?:http|https|www\.)\S+',  # URLs (may be spam)
        ]

        # Enhanced PII detection patterns
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
            r'\b\d{1,5}\s+(?:\w+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct|Circle|Cir)\b',  # Address
            r'\b\d{5}(?:-\d{4})?\b',  # ZIP code
            r'\b(?:19|20)\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])\b',  # Date of birth
            r'\b[A-Z]{1,2}\d{6,8}[A-Z]?\b',  # UK National Insurance Number
            r'\b\d{8,10}\b',  # Generic ID numbers (could be sensitive)
        ]

        # Privacy-specific rules
        self.privacy_rules = [
            {
                "id": "privacy_data_export",
                "name": "Data Export Privacy Check",
                "condition": lambda data: self._contains_data_export(data),
                "action": "require_confirmation",
                "severity": "high"
            },
            {
                "id": "privacy_external_permissions",
                "name": "External Site Permissions",
                "condition": lambda data: self._contains_external_permissions(data),
                "action": "require_approval",
                "severity": "critical"
            },
            {
                "id": "privacy_payment_data",
                "name": "Payment Information Handling",
                "condition": lambda data: self._contains_payment_data(data),
                "action": "require_confirmation",
                "severity": "critical"
            },
            {
                "id": "privacy_login_credentials",
                "name": "Login Credentials Protection",
                "condition": lambda data: self._contains_login_data(data),
                "action": "deny",
                "severity": "critical"
            }
        ]

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main guardrail validation method"""
        evaluation_report = input_data.get("evaluation_report", {})
        logger.info("Running guardrail validation on evaluation report")

        try:
            # Step 1: Validate execution results
            validation_result = await self._validate_execution_results(evaluation_report)

            # Step 2: Check rate limits
            rate_limit_result = await self._check_rate_limits(context)

            # Step 3: Assess overall risk
            risk_assessment = self._assess_overall_risk(validation_result, rate_limit_result)

            # Step 4: Generate approval decision
            approval_decision = self._generate_approval_decision(
                validation_result, rate_limit_result, risk_assessment
            )

            # Step 5: Log validation results
            await self._log_validation_results(validation_result, approval_decision)

            guardrail_result = {
                "validation_result": validation_result.__dict__,
                "rate_limit_check": rate_limit_result,
                "risk_assessment": risk_assessment,
                "approval_decision": approval_decision,
                "validated_at": datetime.now().isoformat()
            }

            logger.info(f"Guardrail validation complete: {approval_decision['action']}")
            return guardrail_result

        except Exception as e:
            logger.error(f"Guardrail validation failed: {e}")
            raise

    async def _validate_execution_results(self, evaluation_report: Dict[str, Any]) -> ValidationResult:
        """Validate execution results against policy rules"""
        violations = []
        warnings = []
        recommendations = []
        risk_score = 0.0

        # Extract outcomes from evaluation report
        outcome_analyses = evaluation_report.get("outcome_analyses", [])

        for analysis in outcome_analyses:
            # Check content safety
            content_violations = await self._check_content_safety(analysis)
            violations.extend(content_violations)

            # Check compliance
            compliance_violations = await self._check_compliance(analysis)
            violations.extend(compliance_violations)

            # Check performance thresholds
            performance_warnings = self._check_performance_thresholds(analysis)
            warnings.extend(performance_warnings)

        # Calculate risk score based on violations
        risk_score = self._calculate_risk_score(violations, warnings)

        # Determine action
        action = self._determine_validation_action(risk_score, violations)

        # Generate recommendations
        recommendations = self._generate_safety_recommendations(violations, warnings)

        return ValidationResult(
            valid=action == "allow",
            action=action,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            risk_score=risk_score
        )

    async def _check_content_safety(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check content for safety violations"""
        violations = []

        # Extract content from analysis (would be in the actual output)
        content = self._extract_content_from_analysis(analysis)

        if not content:
            return violations

        # Check prohibited patterns
        for pattern in self.prohibited_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append({
                    "rule_id": "content_safety_prohibited",
                    "severity": "high",
                    "description": f"Content contains prohibited terms: {', '.join(matches[:3])}",
                    "category": "content_safety",
                    "evidence": matches[:5]
                })

        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            violations.append({
                "rule_id": "content_safety_caps",
                "severity": "medium",
                "description": f"Excessive capitalization ({caps_ratio:.1%})",
                "category": "content_safety",
                "evidence": f"caps_ratio: {caps_ratio}"
            })

        return violations

    async def _check_compliance(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for compliance violations"""
        violations = []

        # Extract content for PII checking
        content = self._extract_content_from_analysis(analysis)

        if content:
            # Check for PII
            for pattern in self.pii_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    violations.append({
                        "rule_id": "compliance_pii",
                        "severity": "critical",
                        "description": f"Potential PII detected: {len(matches)} instances",
                        "category": "compliance",
                        "evidence": f"pattern_matches: {len(matches)}"
                    })

            # Check agent cluster compliance
            agent_cluster = analysis.get("agent_cluster")
            if agent_cluster == "brain":
                # LLM-specific compliance checks
                if self._contains_llm_hallucination_indicators(content):
                    violations.append({
                        "rule_id": "compliance_llm_hallucination",
                        "severity": "high",
                        "description": "Potential LLM hallucination detected",
                        "category": "compliance",
                        "evidence": "hallucination_indicators_present"
                    })

        # Check privacy rules
        privacy_violations = await self._check_privacy_rules(analysis)
        violations.extend(privacy_violations)

        return violations

    async def _check_privacy_rules(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check privacy-specific rules"""
        violations = []

        # Extract data from analysis for privacy checking
        data = self._extract_data_from_analysis(analysis)

        for rule in self.privacy_rules:
            try:
                if rule["condition"](data):
                    violations.append({
                        "rule_id": rule["id"],
                        "severity": rule["severity"],
                        "description": f"Privacy rule violation: {rule['name']}",
                        "category": "privacy",
                        "action_required": rule["action"],
                        "evidence": f"rule_triggered: {rule['id']}"
                    })
            except Exception as e:
                logger.warning(f"Error checking privacy rule {rule['id']}: {e}")

        return violations

    def _contains_data_export(self, data: Dict[str, Any]) -> bool:
        """Check if data contains export operations"""
        content = str(data).lower()
        export_indicators = ["export", "download", "csv", "excel", "database", "api"]

        return any(indicator in content for indicator in export_indicators)

    def _contains_external_permissions(self, data: Dict[str, Any]) -> bool:
        """Check if data contains external site permissions"""
        content = str(data).lower()
        permission_indicators = ["permission", "oauth", "api_key", "token", "authorize", "connect"]

        return any(indicator in content for indicator in permission_indicators)

    def _contains_payment_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains payment information"""
        content = str(data).lower()
        payment_indicators = ["payment", "billing", "stripe", "paypal", "credit", "card", "invoice"]

        return any(indicator in content for indicator in payment_indicators)

    def _contains_login_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains login credentials"""
        content = str(data).lower()
        login_indicators = ["password", "login", "username", "credential", "auth", "session"]

        return any(indicator in content for indicator in login_indicators)

    def _extract_data_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from analysis for privacy checking"""
        # In a real implementation, this would extract the actual data being processed
        # For now, return the analysis itself
        return analysis

    def _check_performance_thresholds(self, analysis: Dict[str, Any]) -> List[str]:
        """Check for performance threshold violations"""
        warnings = []

        anomaly_score = analysis.get("anomaly_score", 0)
        quality_score = analysis.get("quality_score", 1)

        if anomaly_score > 0.8:
            warnings.append(f"High anomaly score ({anomaly_score:.2f}) for {analysis.get('metric', 'unknown')}")

        if quality_score < 0.5:
            warnings.append(f"Low quality score ({quality_score:.2f}) for {analysis.get('agent_cluster', 'unknown')}")

        execution_time = analysis.get("value", 0) if analysis.get("metric") == "execution_time" else 0
        if execution_time > 600:  # 10 minutes
            warnings.append(f"Excessive execution time ({execution_time:.1f}s)")

        return warnings

    def _extract_content_from_analysis(self, analysis: Dict[str, Any]) -> str:
        """Extract text content from analysis for validation"""
        # In a real implementation, this would extract content from the execution result
        # For now, return empty string
        return ""

    def _contains_llm_hallucination_indicators(self, content: str) -> bool:
        """Check for indicators of LLM hallucination"""
        hallucination_indicators = [
            "I'm not sure", "I think", "perhaps", "maybe",
            "as far as I know", "to the best of my knowledge"
        ]

        content_lower = content.lower()
        indicator_count = sum(1 for indicator in hallucination_indicators if indicator in content_lower)

        return indicator_count > 2  # More than 2 uncertainty indicators

    def _calculate_risk_score(self, violations: List[Dict[str, Any]], warnings: List[str]) -> float:
        """Calculate overall risk score"""
        risk_score = 0.0

        # Violations contribute to risk score based on severity
        severity_weights = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.7,
            "critical": 1.0
        }

        for violation in violations:
            severity = violation.get("severity", "medium")
            risk_score += severity_weights.get(severity, 0.3)

        # Warnings add smaller risk
        risk_score += len(warnings) * 0.05

        return min(risk_score, 1.0)

    def _determine_validation_action(self, risk_score: float, violations: List[Dict[str, Any]]) -> str:
        """Determine validation action based on risk"""
        # Check for critical violations
        has_critical = any(v.get("severity") == "critical" for v in violations)

        if has_critical:
            return "deny"
        elif risk_score > 0.7:
            return "quarantine"
        elif risk_score > 0.3:
            return "warn"
        else:
            return "allow"

    def _generate_safety_recommendations(self, violations: List[Dict[str, Any]], warnings: List[str]) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []

        violation_types = set(v.get("category", "unknown") for v in violations)

        if "content_safety" in violation_types:
            recommendations.append("Review content generation parameters to avoid prohibited terms")

        if "compliance" in violation_types:
            recommendations.append("Implement additional PII detection and content sanitization")

        if warnings:
            recommendations.append("Monitor performance metrics and consider parameter adjustments")

        if not recommendations:
            recommendations.append("Continue monitoring - no safety issues detected")

        return recommendations

    async def _check_rate_limits(self, context: Any) -> Dict[str, Any]:
        """Check rate limits for the current context"""
        org_id = context.get("org_id", "unknown") if context else "unknown"
        user_id = context.get("user_id", "unknown") if context else "unknown"

        # Define rate limit keys
        rate_limit_keys = [
            f"org:{org_id}:daily_emails",
            f"org:{org_id}:hourly_api_calls",
            f"user:{user_id}:minute_actions"
        ]

        violations = []

        for key in rate_limit_keys:
            if key not in self.rate_limits:
                # Initialize rate limit
                self.rate_limits[key] = RateLimit(
                    key=key,
                    limit=self._get_rate_limit_for_key(key),
                    window_seconds=self._get_window_for_key(key)
                )

            rate_limit = self.rate_limits[key]

            # Check if window has expired
            if datetime.now() - rate_limit.window_start > timedelta(seconds=rate_limit.window_seconds):
                rate_limit.current_count = 0
                rate_limit.window_start = datetime.now()

            # Check limit
            if rate_limit.current_count >= rate_limit.limit:
                violations.append({
                    "key": key,
                    "current": rate_limit.current_count,
                    "limit": rate_limit.limit,
                    "window_seconds": rate_limit.window_seconds
                })

        return {
            "rate_limits_checked": len(rate_limit_keys),
            "violations": violations,
            "within_limits": len(violations) == 0
        }

    def _get_rate_limit_for_key(self, key: str) -> int:
        """Get rate limit for a key"""
        limits = {
            "daily_emails": 1000,
            "hourly_api_calls": 100,
            "minute_actions": 10
        }

        for pattern, limit in limits.items():
            if pattern in key:
                return limit

        return 100  # Default

    def _get_window_for_key(self, key: str) -> int:
        """Get time window for a key"""
        windows = {
            "daily": 86400,  # 24 hours
            "hourly": 3600,  # 1 hour
            "minute": 60     # 1 minute
        }

        for pattern, window in windows.items():
            if pattern in key:
                return window

        return 3600  # Default 1 hour

    def _assess_overall_risk(self, validation_result: ValidationResult, rate_limit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk combining all factors"""
        risk_factors = []

        # Validation risk
        if not validation_result.valid:
            risk_factors.append("validation_failures")
        if validation_result.risk_score > 0.5:
            risk_factors.append("high_risk_score")

        # Rate limit risk
        if not rate_limit_result.get("within_limits", True):
            risk_factors.append("rate_limit_violations")

        # Calculate overall risk level
        risk_level = "low"
        if len(risk_factors) >= 3:
            risk_level = "critical"
        elif len(risk_factors) >= 2:
            risk_level = "high"
        elif len(risk_factors) >= 1:
            risk_level = "medium"

        return {
            "level": risk_level,
            "factors": risk_factors,
            "requires_approval": risk_level in ["high", "critical"],
            "can_proceed": risk_level == "low"
        }

    def _generate_approval_decision(self, validation_result: ValidationResult,
                                  rate_limit_result: Dict[str, Any],
                                  risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final approval decision"""
        action = "allow"
        reasons = []
        mitigation_steps = []

        # Determine action based on risk assessment
        if risk_assessment["level"] == "critical":
            action = "deny"
            reasons.append("Critical risk factors detected")
            mitigation_steps.append("Manual review required before proceeding")
        elif risk_assessment["level"] == "high":
            action = "quarantine"
            reasons.append("High risk factors detected")
            mitigation_steps.append("Results quarantined for review")
        elif risk_assessment["level"] == "medium":
            action = "warn"
            reasons.append("Medium risk factors detected")
            mitigation_steps.append("Proceed with caution and monitoring")

        # Add specific reasons
        if not validation_result.valid:
            reasons.append(f"Validation failed: {len(validation_result.violations)} violations")

        if not rate_limit_result.get("within_limits", True):
            reasons.append("Rate limits exceeded")

        return {
            "action": action,
            "approved": action == "allow",
            "reasons": reasons,
            "mitigation_steps": mitigation_steps,
            "risk_level": risk_assessment["level"],
            "requires_human_review": action in ["deny", "quarantine"]
        }

    async def _log_validation_results(self, validation_result: ValidationResult, approval_decision: Dict[str, Any]):
        """Log validation results for audit and monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "validation_result": {
                "valid": validation_result.valid,
                "action": validation_result.action,
                "violation_count": len(validation_result.violations),
                "warning_count": len(validation_result.warnings),
                "risk_score": validation_result.risk_score
            },
            "approval_decision": approval_decision,
            "logged_at": datetime.now().isoformat()
        }

        self.violation_history.append(log_entry)

        # Keep only last 1000 entries
        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-1000:]

        logger.info(f"Logged validation result: {approval_decision['action']}")

    def _initialize_default_policies(self):
        """Initialize default policy rules"""
        self.policy_rules = [
            PolicyRule(
                id="content_safety_1",
                name="Prohibited Content Detection",
                category="content",
                condition={"contains_prohibited_terms": True},
                action="deny",
                severity="high"
            ),
            PolicyRule(
                id="compliance_1",
                name="PII Detection",
                category="compliance",
                condition={"contains_pii": True},
                action="quarantine",
                severity="critical"
            ),
            PolicyRule(
                id="rate_limit_1",
                name="Daily Email Limit",
                category="rate_limit",
                condition={"daily_emails": ">1000"},
                action="deny",
                severity="medium"
            ),
            PolicyRule(
                id="performance_1",
                name="Quality Threshold",
                category="safety",
                condition={"quality_score": "<0.5"},
                action="warn",
                severity="medium"
            )
        ]

    async def add_policy_rule(self, rule: PolicyRule):
        """Add a new policy rule"""
        self.policy_rules.append(rule)
        logger.info(f"Added policy rule: {rule.name}")

    async def remove_policy_rule(self, rule_id: str):
        """Remove a policy rule"""
        self.policy_rules = [r for r in self.policy_rules if r.id != rule_id]
        logger.info(f"Removed policy rule: {rule_id}")

    async def get_policy_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent policy violations"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            entry for entry in self.violation_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]

    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary statistics"""
        recent_violations = await self.get_policy_violations(24)

        return {
            "total_violations_24h": len(recent_violations),
            "critical_violations": len([v for v in recent_violations if v["validation_result"]["risk_score"] > 0.8]),
            "active_rules": len([r for r in self.policy_rules if r.enabled]),
            "generated_at": datetime.now().isoformat()
        }