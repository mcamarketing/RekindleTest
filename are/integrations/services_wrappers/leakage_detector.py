"""
ARE Leakage Detector Service Wrapper

Identifies revenue leakage points, pipeline gaps, and optimization opportunities
using advanced analytics and ML-driven insights.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class LeakageType(Enum):
    """Types of revenue leakage"""
    STALLED_DEALS = "stalled_deals"
    DISQUALIFIED_LEADS = "disqualified_leads"
    LOW_ENGAGEMENT = "low_engagement"
    PRICING_ISSUES = "pricing_issues"
    COMPETITOR_WIN = "competitor_win"
    TIMING_MISSED = "timing_missed"
    FOLLOW_UP_GAPS = "follow_up_gaps"

class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class LeakagePoint:
    """Represents a detected revenue leakage point"""
    leakage_id: str
    type: LeakageType
    description: str
    affected_leads: List[str]
    estimated_loss: float
    risk_level: RiskLevel
    detection_date: datetime
    root_cause: str
    recommended_actions: List[str]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineAnalysis:
    """Analysis of sales pipeline health"""
    analysis_id: str
    time_period: str
    total_pipeline_value: float
    leakage_points: List[LeakagePoint]
    overall_health_score: float
    risk_distribution: Dict[str, int]
    top_risks: List[str]
    recommendations: List[str]
    generated_at: datetime

class LeakageDetectorAgent:
    """ARE Leakage Detector - Revenue leakage identification and analysis"""

    def __init__(self):
        self.detected_leakage: Dict[str, LeakagePoint] = {}
        self.pipeline_analyses: List[PipelineAnalysis] = {}
        self.leakage_thresholds = {
            "stalled_deal_days": 30,
            "low_engagement_threshold": 0.3,
            "follow_up_gap_days": 7,
            "pipeline_health_threshold": 0.7
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'analyze')

        logger.info(f"Leakage Detector Agent executing action: {action}")

        try:
            if action == 'analyze_pipeline':
                return await self._analyze_pipeline(input_data)
            elif action == 'detect_leakage':
                return await self._detect_leakage(input_data)
            elif action == 'assess_risk':
                return await self._assess_risk(input_data)
            elif action == 'generate_report':
                return await self._generate_report(input_data)
            elif action == 'get_leakage_insights':
                return self._get_leakage_insights()
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Leakage Detector execution failed: {e}")
            raise

    async def _analyze_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales pipeline for leakage points"""
        pipeline_data = input_data.get('pipeline_data', {})
        time_period = input_data.get('time_period', 'last_30_days')

        # Detect various types of leakage
        leakage_points = []

        # Stalled deals detection
        stalled_leakage = await self._detect_stalled_deals(pipeline_data)
        leakage_points.extend(stalled_leakage)

        # Low engagement detection
        engagement_leakage = await self._detect_low_engagement(pipeline_data)
        leakage_points.extend(engagement_leakage)

        # Follow-up gaps detection
        followup_leakage = await self._detect_followup_gaps(pipeline_data)
        leakage_points.extend(followup_leakage)

        # Pricing issues detection
        pricing_leakage = await self._detect_pricing_issues(pipeline_data)
        leakage_points.extend(pricing_leakage)

        # Calculate overall pipeline health
        total_pipeline_value = pipeline_data.get('total_value', 0)
        total_leakage_value = sum(lp.estimated_loss for lp in leakage_points)
        health_score = max(0, min(1, 1 - (total_leakage_value / total_pipeline_value) if total_pipeline_value > 0 else 1))

        # Risk distribution
        risk_distribution = {}
        for lp in leakage_points:
            risk_distribution[lp.risk_level.value] = risk_distribution.get(lp.risk_level.value, 0) + 1

        # Top risks
        top_risks = sorted(leakage_points, key=lambda x: x.estimated_loss, reverse=True)[:5]
        top_risk_descriptions = [f"{lp.type.value}: £{lp.estimated_loss:,.0f}" for lp in top_risks]

        # Generate recommendations
        recommendations = await self._generate_pipeline_recommendations(leakage_points, health_score)

        analysis = PipelineAnalysis(
            analysis_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            time_period=time_period,
            total_pipeline_value=total_pipeline_value,
            leakage_points=leakage_points,
            overall_health_score=health_score,
            risk_distribution=risk_distribution,
            top_risks=top_risk_descriptions,
            recommendations=recommendations,
            generated_at=datetime.now()
        )

        self.pipeline_analyses.append(analysis)

        logger.info(f"Pipeline analysis completed: {len(leakage_points)} leakage points detected")

        return {
            "status": "analyzed",
            "analysis_id": analysis.analysis_id,
            "leakage_points_detected": len(leakage_points),
            "total_estimated_loss": total_leakage_value,
            "pipeline_health_score": health_score,
            "risk_distribution": risk_distribution,
            "recommendations": recommendations[:5]  # Top 5 recommendations
        }

    async def _detect_leakage(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect specific types of leakage"""
        leakage_type = input_data.get('leakage_type')
        target_data = input_data.get('target_data', {})

        if not leakage_type:
            raise ValueError("leakage_type is required")

        try:
            leakage_enum = LeakageType(leakage_type.upper())
        except ValueError:
            raise ValueError(f"Unknown leakage type: {leakage_type}")

        # Detect specific leakage type
        if leakage_enum == LeakageType.STALLED_DEALS:
            leakage_points = await self._detect_stalled_deals(target_data)
        elif leakage_enum == LeakageType.LOW_ENGAGEMENT:
            leakage_points = await self._detect_low_engagement(target_data)
        elif leakage_enum == LeakageType.FOLLOW_UP_GAPS:
            leakage_points = await self._detect_followup_gaps(target_data)
        elif leakage_enum == LeakageType.PRICING_ISSUES:
            leakage_points = await self._detect_pricing_issues(target_data)
        else:
            leakage_points = []

        # Store detected leakage
        for lp in leakage_points:
            self.detected_leakage[lp.leakage_id] = lp

        return {
            "status": "detected",
            "leakage_type": leakage_type,
            "points_detected": len(leakage_points),
            "total_estimated_loss": sum(lp.estimated_loss for lp in leakage_points),
            "results": [
                {
                    "id": lp.leakage_id,
                    "description": lp.description,
                    "estimated_loss": lp.estimated_loss,
                    "risk_level": lp.risk_level.value,
                    "affected_leads": len(lp.affected_leads)
                }
                for lp in leakage_points
            ]
        }

    async def _assess_risk(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level for detected leakage"""
        leakage_id = input_data.get('leakage_id')

        if not leakage_id or leakage_id not in self.detected_leakage:
            raise ValueError("Valid leakage_id is required")

        leakage_point = self.detected_leakage[leakage_id]

        # Perform detailed risk assessment
        risk_factors = await self._analyze_risk_factors(leakage_point)
        mitigation_strategies = await self._suggest_mitigation_strategies(leakage_point)

        # Update risk level if needed
        updated_risk = self._reassess_risk_level(leakage_point, risk_factors)

        return {
            "status": "assessed",
            "leakage_id": leakage_id,
            "current_risk_level": leakage_point.risk_level.value,
            "updated_risk_level": updated_risk.value,
            "risk_factors": risk_factors,
            "mitigation_strategies": mitigation_strategies,
            "confidence_score": leakage_point.confidence_score
        }

    async def _generate_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive leakage report"""
        time_period = input_data.get('time_period', 'last_30_days')
        include_recommendations = input_data.get('include_recommendations', True)

        # Get recent analyses
        recent_analyses = [
            analysis for analysis in self.pipeline_analyses
            if (datetime.now() - analysis.generated_at).days <= 30
        ]

        if not recent_analyses:
            return {"status": "no_data", "message": "No recent pipeline analyses found"}

        # Aggregate data from recent analyses
        total_analyses = len(recent_analyses)
        avg_health_score = sum(a.overall_health_score for a in recent_analyses) / total_analyses

        all_leakage_points = []
        for analysis in recent_analyses:
            all_leakage_points.extend(analysis.leakage_points)

        # Remove duplicates by ID
        unique_leakage = {lp.leakage_id: lp for lp in all_leakage_points}.values()

        total_leakage_value = sum(lp.estimated_loss for lp in unique_leakage)

        # Group by type
        by_type = {}
        for lp in unique_leakage:
            lp_type = lp.type.value
            if lp_type not in by_type:
                by_type[lp_type] = []
            by_type[lp_type].append(lp)

        # Generate executive summary
        summary = await self._generate_executive_summary(unique_leakage, total_leakage_value, avg_health_score)

        report = {
            "report_id": f"leakage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "time_period": time_period,
            "generated_at": datetime.now().isoformat(),
            "executive_summary": summary,
            "key_metrics": {
                "total_leakage_points": len(unique_leakage),
                "estimated_total_loss": total_leakage_value,
                "average_pipeline_health": avg_health_score,
                "analyses_reviewed": total_analyses
            },
            "leakage_by_type": {
                lp_type: {
                    "count": len(points),
                    "total_loss": sum(lp.estimated_loss for lp in points),
                    "avg_confidence": sum(lp.confidence_score for lp in points) / len(points) if points else 0
                }
                for lp_type, points in by_type.items()
            },
            "top_risks": sorted(
                [{"id": lp.leakage_id, "description": lp.description, "loss": lp.estimated_loss}
                 for lp in unique_leakage],
                key=lambda x: x["loss"],
                reverse=True
            )[:10]
        }

        if include_recommendations:
            report["recommendations"] = await self._generate_comprehensive_recommendations(unique_leakage)

        logger.info(f"Generated leakage report with {len(unique_leakage)} leakage points")

        return {
            "status": "generated",
            "report": report
        }

    def _get_leakage_insights(self) -> Dict[str, Any]:
        """Get aggregated leakage insights"""
        total_leakage_points = len(self.detected_leakage)

        if total_leakage_points == 0:
            return {"status": "no_leakage_detected"}

        # Calculate aggregate metrics
        total_estimated_loss = sum(lp.estimated_loss for lp in self.detected_leakage.values())
        avg_confidence = sum(lp.confidence_score for lp in self.detected_leakage.values()) / total_leakage_points

        # Distribution by type and risk level
        by_type = {}
        by_risk = {}
        for lp in self.detected_leakage.values():
            # By type
            lp_type = lp.type.value
            if lp_type not in by_type:
                by_type[lp_type] = {"count": 0, "total_loss": 0}
            by_type[lp_type]["count"] += 1
            by_type[lp_type]["total_loss"] += lp.estimated_loss

            # By risk
            risk = lp.risk_level.value
            if risk not in by_risk:
                by_risk[risk] = 0
            by_risk[risk] += 1

        return {
            "status": "insights_generated",
            "total_leakage_points": total_leakage_points,
            "total_estimated_loss": total_estimated_loss,
            "average_confidence": avg_confidence,
            "distribution_by_type": by_type,
            "distribution_by_risk": by_risk,
            "most_common_types": sorted(by_type.items(), key=lambda x: x[1]["count"], reverse=True)[:5],
            "highest_risk_areas": sorted(by_risk.items(), key=lambda x: x[1], reverse=True),
            "generated_at": datetime.now().isoformat()
        }

    # Detection methods (simplified implementations)
    async def _detect_stalled_deals(self, pipeline_data: Dict[str, Any]) -> List[LeakagePoint]:
        """Detect stalled deals in pipeline"""
        deals = pipeline_data.get('deals', [])
        leakage_points = []

        for deal in deals:
            last_update = deal.get('last_update')
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))

            days_stalled = (datetime.now() - last_update).days if last_update else 0

            if days_stalled > self.leakage_thresholds['stalled_deal_days']:
                deal_value = deal.get('value', 0)
                estimated_loss = deal_value * 0.3  # Assume 30% chance of losing stalled deals

                risk_level = RiskLevel.HIGH if days_stalled > 60 else RiskLevel.MEDIUM

                leakage_point = LeakagePoint(
                    leakage_id=f"stalled_{deal.get('id', 'unknown')}",
                    type=LeakageType.STALLED_DEALS,
                    description=f"Deal stalled for {days_stalled} days",
                    affected_leads=[deal.get('lead_id', '')],
                    estimated_loss=estimated_loss,
                    risk_level=risk_level,
                    detection_date=datetime.now(),
                    root_cause="Lack of follow-up or engagement",
                    recommended_actions=[
                        "Schedule immediate follow-up call",
                        "Send value-add content",
                        "Re-qualify deal requirements"
                    ],
                    confidence_score=min(0.9, 0.5 + (days_stalled / 100))
                )
                leakage_points.append(leakage_point)

        return leakage_points

    async def _detect_low_engagement(self, pipeline_data: Dict[str, Any]) -> List[LeakagePoint]:
        """Detect leads with low engagement"""
        leads = pipeline_data.get('leads', [])
        leakage_points = []

        for lead in leads:
            engagement_score = lead.get('engagement_score', 1.0)

            if engagement_score < self.leakage_thresholds['low_engagement_threshold']:
                deal_value = lead.get('potential_value', 1000)
                estimated_loss = deal_value * (1 - engagement_score) * 0.5

                leakage_point = LeakagePoint(
                    leakage_id=f"low_engagement_{lead.get('id', 'unknown')}",
                    type=LeakageType.LOW_ENGAGEMENT,
                    description=f"Lead engagement score: {engagement_score:.2f}",
                    affected_leads=[lead.get('id', '')],
                    estimated_loss=estimated_loss,
                    risk_level=RiskLevel.MEDIUM,
                    detection_date=datetime.now(),
                    root_cause="Insufficient nurturing or irrelevant content",
                    recommended_actions=[
                        "Review lead scoring criteria",
                        "Personalize communication approach",
                        "Increase touch frequency"
                    ],
                    confidence_score=0.8
                )
                leakage_points.append(leakage_point)

        return leakage_points

    async def _detect_followup_gaps(self, pipeline_data: Dict[str, Any]) -> List[LeakagePoint]:
        """Detect gaps in follow-up sequences"""
        leads = pipeline_data.get('leads', [])
        leakage_points = []

        for lead in leads:
            last_contact = lead.get('last_contact_date')
            if isinstance(last_contact, str):
                last_contact = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))

            days_since_contact = (datetime.now() - last_contact).days if last_contact else 0

            if days_since_contact > self.leakage_thresholds['follow_up_gap_days']:
                potential_value = lead.get('potential_value', 500)
                estimated_loss = potential_value * min(0.8, days_since_contact / 90)

                leakage_point = LeakagePoint(
                    leakage_id=f"followup_gap_{lead.get('id', 'unknown')}",
                    type=LeakageType.FOLLOW_UP_GAPS,
                    description=f"No follow-up for {days_since_contact} days",
                    affected_leads=[lead.get('id', '')],
                    estimated_loss=estimated_loss,
                    risk_level=RiskLevel.HIGH if days_since_contact > 14 else RiskLevel.MEDIUM,
                    detection_date=datetime.now(),
                    root_cause="Inconsistent follow-up process",
                    recommended_actions=[
                        "Implement automated follow-up sequences",
                        "Set up reminder system for sales team",
                        "Review lead nurturing workflow"
                    ],
                    confidence_score=min(0.9, 0.6 + (days_since_contact / 60))
                )
                leakage_points.append(leakage_point)

        return leakage_points

    async def _detect_pricing_issues(self, pipeline_data: Dict[str, Any]) -> List[LeakagePoint]:
        """Detect pricing-related objections"""
        deals = pipeline_data.get('deals', [])
        leakage_points = []

        for deal in deals:
            objections = deal.get('objections', [])
            pricing_keywords = ['price', 'cost', 'expensive', 'budget', 'afford']

            has_pricing_objection = any(
                any(keyword in objection.lower() for keyword in pricing_keywords)
                for objection in objections
            )

            if has_pricing_objection:
                deal_value = deal.get('value', 0)
                estimated_loss = deal_value * 0.4  # Assume 40% of deals lost to pricing

                leakage_point = LeakagePoint(
                    leakage_id=f"pricing_{deal.get('id', 'unknown')}",
                    type=LeakageType.PRICING_ISSUES,
                    description="Pricing objections detected",
                    affected_leads=[deal.get('lead_id', '')],
                    estimated_loss=estimated_loss,
                    risk_level=RiskLevel.HIGH,
                    detection_date=datetime.now(),
                    root_cause="Pricing not aligned with perceived value",
                    recommended_actions=[
                        "Review pricing strategy",
                        "Develop value-based pricing models",
                        "Create pricing objection handling scripts"
                    ],
                    confidence_score=0.7
                )
                leakage_points.append(leakage_point)

        return leakage_points

    async def _analyze_risk_factors(self, leakage_point: LeakagePoint) -> List[str]:
        """Analyze risk factors for a leakage point"""
        risk_factors = []

        # Time-based risk
        days_old = (datetime.now() - leakage_point.detection_date).days
        if days_old > 7:
            risk_factors.append(f"Leakage point {days_old} days old - urgency increasing")

        # Loss magnitude risk
        if leakage_point.estimated_loss > 10000:
            risk_factors.append("High financial impact")

        # Affected leads count
        if len(leakage_point.affected_leads) > 5:
            risk_factors.append("Multiple leads affected")

        # Type-specific risks
        if leakage_point.type == LeakageType.STALLED_DEALS:
            risk_factors.append("Competitor may be engaging the lead")
        elif leakage_point.type == LeakageType.PRICING_ISSUES:
            risk_factors.append("Price sensitivity indicates budget constraints")

        return risk_factors

    async def _suggest_mitigation_strategies(self, leakage_point: LeakagePoint) -> List[str]:
        """Suggest mitigation strategies"""
        strategies = leakage_point.recommended_actions.copy()

        # Add additional strategies based on type and risk
        if leakage_point.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            strategies.insert(0, "URGENT: Immediate action required")

        if leakage_point.type == LeakageType.STALLED_DEALS:
            strategies.extend([
                "Escalate to sales leadership",
                "Consider offering incentives"
            ])

        return strategies

    def _reassess_risk_level(self, leakage_point: LeakagePoint, risk_factors: List[str]) -> RiskLevel:
        """Reassess risk level based on additional factors"""
        current_risk = leakage_point.risk_level

        # Escalate risk based on factors
        if any("URGENT" in factor for factor in risk_factors):
            if current_risk == RiskLevel.LOW:
                return RiskLevel.MEDIUM
            elif current_risk == RiskLevel.MEDIUM:
                return RiskLevel.HIGH
            elif current_risk == RiskLevel.HIGH:
                return RiskLevel.CRITICAL

        if any("High financial impact" in factor for factor in risk_factors):
            if current_risk != RiskLevel.CRITICAL:
                return RiskLevel.HIGH

        return current_risk

    async def _generate_pipeline_recommendations(self, leakage_points: List[LeakagePoint],
                                               health_score: float) -> List[str]:
        """Generate pipeline-wide recommendations"""
        recommendations = []

        if health_score < 0.5:
            recommendations.append("CRITICAL: Pipeline health is poor - immediate intervention required")

        # Analyze leakage patterns
        stalled_count = sum(1 for lp in leakage_points if lp.type == LeakageType.STALLED_DEALS)
        if stalled_count > len(leakage_points) * 0.3:
            recommendations.append("Implement automated deal progression tracking")

        engagement_count = sum(1 for lp in leakage_points if lp.type == LeakageType.LOW_ENGAGEMENT)
        if engagement_count > len(leakage_points) * 0.4:
            recommendations.append("Review and optimize lead nurturing sequences")

        followup_count = sum(1 for lp in leakage_points if lp.type == LeakageType.FOLLOW_UP_GAPS)
        if followup_count > 5:
            recommendations.append("Implement automated follow-up reminder system")

        return recommendations

    async def _generate_executive_summary(self, leakage_points: List[LeakagePoint],
                                        total_loss: float, health_score: float) -> str:
        """Generate executive summary for reports"""
        point_count = len(leakage_points)

        if point_count == 0:
            return "No significant revenue leakage detected. Pipeline health is excellent."

        severity = "minor" if health_score > 0.8 else "moderate" if health_score > 0.6 else "significant"

        summary = f"Detected {point_count} revenue leakage points representing an estimated £{total_loss:,.0f} in potential losses. "

        if severity == "significant":
            summary += "Immediate action is required to prevent further deterioration of pipeline health."
        elif severity == "moderate":
            summary += "Monitor closely and implement recommended improvements."
        else:
            summary += "Address identified issues to maintain optimal pipeline performance."

        return summary

    async def _generate_comprehensive_recommendations(self, leakage_points: List[LeakagePoint]) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []

        # Group by type for targeted recommendations
        by_type = {}
        for lp in leakage_points:
            lp_type = lp.type.value
            if lp_type not in by_type:
                by_type[lp_type] = []
            by_type[lp_type].append(lp)

        # Process recommendations
        if 'stalled_deals' in by_type:
            recommendations.append("Implement deal velocity tracking and escalation protocols")
            recommendations.append("Create standardized follow-up cadences for stalled deals")

        if 'low_engagement' in by_type:
            recommendations.append("Audit lead scoring and qualification criteria")
            recommendations.append("Develop personalized engagement strategies based on lead profiles")

        if 'follow_up_gaps' in by_type:
            recommendations.append("Deploy automated follow-up sequence management")
            recommendations.append("Implement sales team notification system for overdue follow-ups")

        if 'pricing_issues' in by_type:
            recommendations.append("Conduct pricing strategy review and competitor analysis")
            recommendations.append("Develop value-based pricing communication materials")

        # Add general recommendations
        recommendations.extend([
            "Establish regular pipeline health monitoring and reporting",
            "Implement early warning system for at-risk deals",
            "Create standardized operating procedures for common leakage scenarios"
        ])

        return recommendations