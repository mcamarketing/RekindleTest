"""
ARE ICP Generator Service Wrapper

Generates Ideal Customer Profiles using data analysis, market research,
and predictive modeling to identify high-value customer segments.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import json

logger = logging.getLogger(__name__)

class ICPQuality(Enum):
    """ICP quality assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"

class SegmentType(Enum):
    """Types of customer segments"""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PSYCHOGRAPHIC = "psychographic"
    TECHNOGRAPHIC = "technographic"
    FIRMOGRAPHIC = "firmographic"

@dataclass
class CustomerSegment:
    """Represents a customer segment"""
    segment_id: str
    name: str
    segment_type: SegmentType
    size_estimate: int
    characteristics: Dict[str, Any]
    pain_points: List[str]
    buying_behavior: Dict[str, Any]
    value_metrics: Dict[str, float]
    confidence_score: float
    created_at: datetime

@dataclass
class IdealCustomerProfile:
    """Represents an Ideal Customer Profile"""
    icp_id: str
    name: str
    segments: List[CustomerSegment]
    core_characteristics: Dict[str, Any]
    decision_makers: List[Dict[str, Any]]
    buying_process: Dict[str, Any]
    value_proposition: str
    quality_score: ICPQuality
    validation_metrics: Dict[str, Any]
    market_size: int
    revenue_potential: float
    created_at: datetime
    last_updated: datetime

@dataclass
class ICPRecommendation:
    """ICP-based recommendation"""
    recommendation_id: str
    icp_id: str
    target_segment: str
    recommendation_type: str
    content: str
    expected_impact: Dict[str, Any]
    confidence_score: float
    generated_at: datetime

class ICPGeneratorAgent:
    """ARE ICP Generator - Ideal Customer Profile creation and management"""

    def __init__(self):
        self.icps: Dict[str, IdealCustomerProfile] = {}
        self.segments: Dict[str, CustomerSegment] = {}
        self.recommendations: Dict[str, ICPRecommendation] = {}
        self.customer_data: List[Dict[str, Any]] = []

        # ICP generation parameters
        self.min_segment_size = 100
        self.quality_thresholds = {
            ICPQuality.LOW: 0.3,
            ICPQuality.MEDIUM: 0.6,
            ICPQuality.HIGH: 0.8,
            ICPQuality.PREMIUM: 0.95
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'generate')

        logger.info(f"ICP Generator Agent executing action: {action}")

        try:
            if action == 'generate_icp':
                return await self._generate_icp(input_data)
            elif action == 'analyze_segments':
                return await self._analyze_segments(input_data)
            elif action == 'validate_icp':
                return await self._validate_icp(input_data)
            elif action == 'generate_recommendations':
                return await self._generate_recommendations(input_data)
            elif action == 'get_icp_insights':
                return self._get_icp_insights()
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"ICP Generator execution failed: {e}")
            raise

    async def _generate_icp(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Ideal Customer Profile"""
        customer_data = input_data.get('customer_data', [])
        business_context = input_data.get('business_context', {})
        target_criteria = input_data.get('target_criteria', {})

        # Store customer data for analysis
        self.customer_data.extend(customer_data)

        # Analyze customer segments
        segments = await self._analyze_customer_segments(customer_data, target_criteria)

        # Identify best segments for ICP
        top_segments = sorted(segments.values(),
                            key=lambda s: s.value_metrics.get('revenue_potential', 0),
                            reverse=True)[:5]

        # Generate core ICP characteristics
        core_characteristics = await self._generate_core_characteristics(top_segments, business_context)

        # Identify decision makers
        decision_makers = await self._identify_decision_makers(top_segments)

        # Map buying process
        buying_process = await self._map_buying_process(top_segments)

        # Craft value proposition
        value_proposition = await self._craft_value_proposition(core_characteristics, business_context)

        # Calculate quality score
        quality_score = self._calculate_icp_quality(top_segments, core_characteristics)

        # Estimate market size and revenue potential
        market_size = sum(s.size_estimate for s in top_segments)
        revenue_potential = sum(s.value_metrics.get('revenue_potential', 0) for s in top_segments)

        # Generate validation metrics
        validation_metrics = await self._generate_validation_metrics(top_segments, customer_data)

        icp = IdealCustomerProfile(
            icp_id=f"icp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=input_data.get('name', f"ICP {datetime.now().strftime('%Y%m%d')}"),
            segments=top_segments,
            core_characteristics=core_characteristics,
            decision_makers=decision_makers,
            buying_process=buying_process,
            value_proposition=value_proposition,
            quality_score=quality_score,
            validation_metrics=validation_metrics,
            market_size=market_size,
            revenue_potential=revenue_potential,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )

        self.icps[icp.icp_id] = icp

        # Store segments
        for segment in top_segments:
            self.segments[segment.segment_id] = segment

        logger.info(f"Generated ICP: {icp.name} with {len(top_segments)} segments")

        return {
            "status": "generated",
            "icp_id": icp.icp_id,
            "name": icp.name,
            "quality_score": icp.quality_score.value,
            "market_size": icp.market_size,
            "revenue_potential": icp.revenue_potential,
            "segment_count": len(top_segments)
        }

    async def _analyze_segments(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer segments"""
        customer_data = input_data.get('customer_data', [])
        segment_types = input_data.get('segment_types', [t.value for t in SegmentType])

        segments = await self._analyze_customer_segments(customer_data, {})

        # Filter by requested types
        filtered_segments = {
            sid: segment for sid, segment in segments.items()
            if segment.segment_type.value in segment_types
        }

        # Calculate segment metrics
        segment_metrics = {}
        for segment in filtered_segments.values():
            segment_metrics[segment.segment_id] = {
                "size": segment.size_estimate,
                "revenue_potential": segment.value_metrics.get('revenue_potential', 0),
                "confidence": segment.confidence_score,
                "type": segment.segment_type.value
            }

        return {
            "status": "analyzed",
            "segment_count": len(filtered_segments),
            "segment_metrics": segment_metrics,
            "top_segments": sorted(
                [{"id": s.segment_id, "name": s.name, "revenue": s.value_metrics.get('revenue_potential', 0)}
                 for s in filtered_segments.values()],
                key=lambda x: x["revenue"],
                reverse=True
            )[:10]
        }

    async def _validate_icp(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ICP against new data"""
        icp_id = input_data.get('icp_id')
        validation_data = input_data.get('validation_data', [])

        if not icp_id or icp_id not in self.icps:
            raise ValueError("Valid icp_id is required")

        icp = self.icps[icp_id]

        # Perform validation
        validation_results = await self._validate_icp_accuracy(icp, validation_data)

        # Update ICP with validation results
        icp.validation_metrics.update(validation_results)
        icp.last_updated = datetime.now()

        return {
            "status": "validated",
            "icp_id": icp_id,
            "validation_score": validation_results.get('overall_accuracy', 0),
            "recommendations": validation_results.get('improvement_recommendations', []),
            "confidence_adjustment": validation_results.get('confidence_change', 0)
        }

    async def _generate_recommendations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ICP-based recommendations"""
        icp_id = input_data.get('icp_id')
        context_data = input_data.get('context_data', {})

        if not icp_id or icp_id not in self.icps:
            raise ValueError("Valid icp_id is required")

        icp = self.icps[icp_id]

        # Generate recommendations for each segment
        recommendations = []
        for segment in icp.segments:
            segment_recs = await self._generate_segment_recommendations(segment, context_data)
            recommendations.extend(segment_recs)

        # Store recommendations
        for rec in recommendations:
            self.recommendations[rec.recommendation_id] = rec

        return {
            "status": "generated",
            "icp_id": icp_id,
            "recommendation_count": len(recommendations),
            "recommendations": [
                {
                    "id": r.recommendation_id,
                    "type": r.recommendation_type,
                    "target_segment": r.target_segment,
                    "content": r.content,
                    "expected_impact": r.expected_impact
                }
                for r in recommendations
            ]
        }

    def _get_icp_insights(self) -> Dict[str, Any]:
        """Get aggregated ICP insights"""
        total_icps = len(self.icps)
        total_segments = len(self.segments)

        if total_icps == 0:
            return {"status": "no_icps"}

        # Calculate aggregate metrics
        recent_icps = [
            icp for icp in self.icps.values()
            if (datetime.now() - icp.created_at).days <= 30
        ]

        if recent_icps:
            avg_market_size = sum(icp.market_size for icp in recent_icps) / len(recent_icps)
            avg_revenue_potential = sum(icp.revenue_potential for icp in recent_icps) / len(recent_icps)
            quality_distribution = {}
            for icp in recent_icps:
                quality = icp.quality_score.value
                quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        else:
            avg_market_size = 0
            avg_revenue_potential = 0
            quality_distribution = {}

        # Segment type distribution
        segment_types = {}
        for segment in self.segments.values():
            s_type = segment.segment_type.value
            segment_types[s_type] = segment_types.get(s_type, 0) + 1

        return {
            "status": "insights_generated",
            "total_icps": total_icps,
            "total_segments": total_segments,
            "recent_icps": len(recent_icps),
            "average_market_size": avg_market_size,
            "average_revenue_potential": avg_revenue_potential,
            "quality_distribution": quality_distribution,
            "segment_type_distribution": segment_types,
            "most_common_segment_type": max(segment_types.items(), key=lambda x: x[1])[0] if segment_types else None,
            "generated_at": datetime.now().isoformat()
        }

    async def _analyze_customer_segments(self, customer_data: List[Dict[str, Any]],
                                       criteria: Dict[str, Any]) -> Dict[str, CustomerSegment]:
        """Analyze customer data to identify segments"""
        segments = {}

        if not customer_data:
            return segments

        # Demographic segmentation
        demo_segments = await self._segment_demographic(customer_data)
        segments.update(demo_segments)

        # Behavioral segmentation
        behavioral_segments = await self._segment_behavioral(customer_data)
        segments.update(behavioral_segments)

        # Firmographic segmentation (for B2B)
        firmo_segments = await self._segment_firmographic(customer_data)
        segments.update(firmo_segments)

        # Technographic segmentation
        techno_segments = await self._segment_technographic(customer_data)
        segments.update(techno_segments)

        # Calculate value metrics for each segment
        for segment in segments.values():
            segment.value_metrics = await self._calculate_segment_value(segment, customer_data)

        return segments

    async def _segment_demographic(self, customer_data: List[Dict[str, Any]]) -> Dict[str, CustomerSegment]:
        """Demographic segmentation"""
        segments = {}

        # Group by company size
        size_groups = {}
        for customer in customer_data:
            size = customer.get('company_size', 'unknown')
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(customer)

        for size, customers in size_groups.items():
            if len(customers) >= self.min_segment_size:
                segment = CustomerSegment(
                    segment_id=f"demo_size_{size}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"{size.title()} Companies",
                    segment_type=SegmentType.DEMOGRAPHIC,
                    size_estimate=len(customers),
                    characteristics={"company_size": size},
                    pain_points=[],  # Will be filled by analysis
                    buying_behavior={},
                    value_metrics={},
                    confidence_score=0.8
                )
                segments[segment.segment_id] = segment

        return segments

    async def _segment_behavioral(self, customer_data: List[Dict[str, Any]]) -> Dict[str, CustomerSegment]:
        """Behavioral segmentation"""
        segments = {}

        # Group by engagement level
        engagement_groups = {"high": [], "medium": [], "low": []}

        for customer in customer_data:
            engagement_score = customer.get('engagement_score', 0.5)
            if engagement_score > 0.7:
                engagement_groups["high"].append(customer)
            elif engagement_score > 0.3:
                engagement_groups["medium"].append(customer)
            else:
                engagement_groups["low"].append(customer)

        for level, customers in engagement_groups.items():
            if len(customers) >= self.min_segment_size:
                segment = CustomerSegment(
                    segment_id=f"behavioral_engagement_{level}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"{level.title()} Engagement Users",
                    segment_type=SegmentType.BEHAVIORAL,
                    size_estimate=len(customers),
                    characteristics={"engagement_level": level},
                    pain_points=[],
                    buying_behavior={},
                    value_metrics={},
                    confidence_score=0.7
                )
                segments[segment.segment_id] = segment

        return segments

    async def _segment_firmographic(self, customer_data: List[Dict[str, Any]]) -> Dict[str, CustomerSegment]:
        """Firmographic segmentation"""
        segments = {}

        # Group by industry
        industry_groups = {}
        for customer in customer_data:
            industry = customer.get('industry', 'unknown')
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(customer)

        for industry, customers in industry_groups.items():
            if len(customers) >= self.min_segment_size:
                segment = CustomerSegment(
                    segment_id=f"firmo_industry_{industry.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"{industry.title()} Industry",
                    segment_type=SegmentType.FIRMOGRAPHIC,
                    size_estimate=len(customers),
                    characteristics={"industry": industry},
                    pain_points=[],
                    buying_behavior={},
                    value_metrics={},
                    confidence_score=0.9
                )
                segments[segment.segment_id] = segment

        return segments

    async def _segment_technographic(self, customer_data: List[Dict[str, Any]]) -> Dict[str, CustomerSegment]:
        """Technographic segmentation"""
        segments = {}

        # Group by tech stack usage
        tech_groups = {}
        for customer in customer_data:
            tech_stack = customer.get('tech_stack', [])
            if isinstance(tech_stack, str):
                tech_stack = [tech_stack]

            for tech in tech_stack:
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(customer)

        for tech, customers in tech_groups.items():
            if len(customers) >= self.min_segment_size:
                segment = CustomerSegment(
                    segment_id=f"techno_{tech.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"{tech.title()} Users",
                    segment_type=SegmentType.TECHNOGRAPHIC,
                    size_estimate=len(customers),
                    characteristics={"technology": tech},
                    pain_points=[],
                    buying_behavior={},
                    value_metrics={},
                    confidence_score=0.6
                )
                segments[segment.segment_id] = segment

        return segments

    async def _calculate_segment_value(self, segment: CustomerSegment,
                                     customer_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate value metrics for a segment"""
        # Find customers in this segment
        segment_customers = []
        for customer in customer_data:
            if self._customer_matches_segment(customer, segment):
                segment_customers.append(customer)

        if not segment_customers:
            return {"revenue_potential": 0, "lifetime_value": 0, "conversion_rate": 0}

        # Calculate metrics
        revenues = [c.get('revenue', 0) for c in segment_customers if c.get('revenue')]
        avg_revenue = statistics.mean(revenues) if revenues else 0

        conversion_rates = [c.get('conversion_rate', 0) for c in segment_customers if c.get('conversion_rate')]
        avg_conversion = statistics.mean(conversion_rates) if conversion_rates else 0

        # Estimate lifetime value
        lifetime_value = avg_revenue * (1 / (1 - avg_conversion)) if avg_conversion < 1 else avg_revenue * 10

        # Revenue potential based on segment size
        revenue_potential = lifetime_value * segment.size_estimate * 0.1  # Assume 10% market capture

        return {
            "revenue_potential": revenue_potential,
            "lifetime_value": lifetime_value,
            "conversion_rate": avg_conversion,
            "average_revenue": avg_revenue
        }

    def _customer_matches_segment(self, customer: Dict[str, Any], segment: CustomerSegment) -> bool:
        """Check if customer matches segment criteria"""
        characteristics = segment.characteristics

        for key, value in characteristics.items():
            customer_value = customer.get(key)
            if customer_value != value:
                return False

        return True

    async def _generate_core_characteristics(self, segments: List[CustomerSegment],
                                           business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate core characteristics for ICP"""
        # Aggregate characteristics from top segments
        all_characteristics = {}
        characteristic_counts = {}

        for segment in segments:
            for key, value in segment.characteristics.items():
                if key not in characteristic_counts:
                    characteristic_counts[key] = {}
                    all_characteristics[key] = []

                characteristic_counts[key][value] = characteristic_counts[key].get(value, 0) + 1
                all_characteristics[key].append(value)

        # Select most common characteristics
        core_characteristics = {}
        for key, values in all_characteristics.items():
            # Find most common value
            most_common = max(set(values), key=values.count)
            confidence = values.count(most_common) / len(values)
            core_characteristics[key] = {
                "value": most_common,
                "confidence": confidence,
                "alternatives": list(set(values))
            }

        return core_characteristics

    async def _identify_decision_makers(self, segments: List[CustomerSegment]) -> List[Dict[str, Any]]:
        """Identify key decision makers"""
        # Mock decision maker identification
        decision_makers = [
            {
                "role": "CEO",
                "influence": "high",
                "concerns": ["ROI", "Strategic Fit", "Risk"],
                "timeline": "3-6 months"
            },
            {
                "role": "CTO",
                "influence": "high",
                "concerns": ["Technical Integration", "Scalability", "Security"],
                "timeline": "1-3 months"
            },
            {
                "role": "Procurement Manager",
                "influence": "medium",
                "concerns": ["Budget", "Compliance", "Vendor Management"],
                "timeline": "2-4 months"
            }
        ]

        return decision_makers

    async def _map_buying_process(self, segments: List[CustomerSegment]) -> Dict[str, Any]:
        """Map customer buying process"""
        return {
            "awareness": {
                "channels": ["content_marketing", "social_media", "industry_events"],
                "duration": "1-2 months",
                "key_activities": ["Problem identification", "Solution exploration"]
            },
            "consideration": {
                "channels": ["website", "product_demos", "case_studies"],
                "duration": "1-3 months",
                "key_activities": ["Requirements gathering", "Vendor evaluation", "ROI analysis"]
            },
            "decision": {
                "channels": ["sales_calls", "proposals", "negotiations"],
                "duration": "1-2 months",
                "key_activities": ["Stakeholder alignment", "Contract review", "Final approval"]
            }
        }

    async def _craft_value_proposition(self, characteristics: Dict[str, Any],
                                     business_context: Dict[str, Any]) -> str:
        """Craft compelling value proposition"""
        # Extract key characteristics
        industry = None
        company_size = None

        for key, data in characteristics.items():
            if key == "industry":
                industry = data["value"]
            elif key == "company_size":
                company_size = data["value"]

        # Generate value proposition based on characteristics
        if industry and company_size:
            return f"For {company_size} {industry} companies struggling with lead reactivation, we deliver a 3x increase in pipeline velocity through AI-powered, personalized outreach that converts dormant leads into revenue in 30 days."
        else:
            return "Transform your dormant leads into revenue with AI-powered reactivation campaigns that deliver 5x higher engagement rates and 3x faster pipeline velocity."

    def _calculate_icp_quality(self, segments: List[CustomerSegment],
                             characteristics: Dict[str, Any]) -> ICPQuality:
        """Calculate ICP quality score"""
        # Base score from segment quality
        segment_score = sum(s.confidence_score for s in segments) / len(segments) if segments else 0

        # Characteristic confidence
        char_confidence = sum(data["confidence"] for data in characteristics.values()) / len(characteristics) if characteristics else 0

        # Overall quality score
        quality_score = (segment_score + char_confidence) / 2

        # Determine quality level
        if quality_score >= self.quality_thresholds[ICPQuality.PREMIUM]:
            return ICPQuality.PREMIUM
        elif quality_score >= self.quality_thresholds[ICPQuality.HIGH]:
            return ICPQuality.HIGH
        elif quality_score >= self.quality_thresholds[ICPQuality.MEDIUM]:
            return ICPQuality.MEDIUM
        else:
            return ICPQuality.LOW

    async def _generate_validation_metrics(self, segments: List[CustomerSegment],
                                         customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate validation metrics for ICP"""
        # Calculate validation scores
        segment_coverage = len([c for c in customer_data if any(self._customer_matches_segment(c, s) for s in segments)])
        coverage_rate = segment_coverage / len(customer_data) if customer_data else 0

        # Revenue concentration
        segment_revenue = sum(s.value_metrics.get('revenue_potential', 0) for s in segments)
        total_revenue = sum(c.get('revenue', 0) for c in customer_data)
        revenue_concentration = segment_revenue / total_revenue if total_revenue > 0 else 0

        return {
            "coverage_rate": coverage_rate,
            "revenue_concentration": revenue_concentration,
            "segment_diversity": len(set(s.segment_type.value for s in segments)),
            "data_quality_score": 0.8,  # Mock score
            "validation_timestamp": datetime.now().isoformat()
        }

    async def _validate_icp_accuracy(self, icp: IdealCustomerProfile,
                                   validation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate ICP accuracy against new data"""
        # Calculate how well ICP predicts new customer behavior
        matches = 0
        total = len(validation_data)

        for customer in validation_data:
            customer_matches = False
            for segment in icp.segments:
                if self._customer_matches_segment(customer, segment):
                    customer_matches = True
                    break
            if customer_matches:
                matches += 1

        accuracy = matches / total if total > 0 else 0

        # Generate improvement recommendations
        recommendations = []
        if accuracy < 0.7:
            recommendations.append("Consider expanding segment criteria to improve coverage")
        if accuracy > 0.9:
            recommendations.append("ICP shows excellent predictive accuracy")

        return {
            "overall_accuracy": accuracy,
            "matches": matches,
            "total_validated": total,
            "improvement_recommendations": recommendations,
            "confidence_change": accuracy - 0.5  # Adjust confidence based on validation
        }

    async def _generate_segment_recommendations(self, segment: CustomerSegment,
                                              context_data: Dict[str, Any]) -> List[ICPRecommendation]:
        """Generate recommendations for a specific segment"""
        recommendations = []

        # Messaging recommendations
        if segment.segment_type == SegmentType.DEMOGRAPHIC:
            rec = ICPRecommendation(
                recommendation_id=f"rec_msg_{segment.segment_id}_{datetime.now().strftime('%H%M%S')}",
                icp_id="",  # Will be set by caller
                target_segment=segment.name,
                recommendation_type="messaging",
                content=f"Focus messaging on {segment.characteristics.get('company_size', 'company')} specific challenges and growth opportunities",
                expected_impact={"engagement_increase": 0.25, "conversion_boost": 0.15},
                confidence_score=0.8,
                generated_at=datetime.now()
            )
            recommendations.append(rec)

        # Channel recommendations
        if segment.segment_type == SegmentType.BEHAVIORAL:
            engagement_level = segment.characteristics.get('engagement_level', 'medium')
            if engagement_level == 'high':
                channel_rec = "prioritize_direct_sales"
            elif engagement_level == 'medium':
                channel_rec = "use_content_marketing"
            else:
                channel_rec = "focus_on_nurturing_campaigns"

            rec = ICPRecommendation(
                recommendation_id=f"rec_channel_{segment.segment_id}_{datetime.now().strftime('%H%M%S')}",
                icp_id="",
                target_segment=segment.name,
                recommendation_type="channel_strategy",
                content=f"For {engagement_level} engagement customers, {channel_rec.replace('_', ' ')}",
                expected_impact={"channel_efficiency": 0.3, "cost_reduction": 0.2},
                confidence_score=0.7,
                generated_at=datetime.now()
            )
            recommendations.append(rec)

        return recommendations