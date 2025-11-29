"""
ARE Critic Agent

Aggregates outcomes from all agents, grades performance, detects anomalies or bottlenecks,
and generates learning signals for the Planner and Executor. Continuously improves routing
and agent selection based on real outcomes.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, stdev
import json

logger = logging.getLogger(__name__)

@dataclass
class OutcomeAnalysis:
    """Analysis of a single outcome"""
    outcome_id: str
    task_id: str
    agent_cluster: str
    metric: str
    value: float
    expected_range: Tuple[float, float]
    deviation: float
    anomaly_score: float
    quality_score: float
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics"""
    agent_cluster: str
    time_range: Tuple[datetime, datetime]
    total_outcomes: int
    success_rate: float
    average_quality: float
    average_response_time: float
    anomaly_rate: float
    trend_direction: str  # "improving", "declining", "stable"
    confidence_score: float

@dataclass
class LearningSignal:
    """Learning signal for system improvement"""
    signal_type: str  # "agent_preference", "routing_rule", "parameter_adjustment"
    target: str  # What to adjust (agent, parameter, rule)
    action: str  # "increase_weight", "decrease_weight", "add_rule", "remove_rule"
    value: Any
    confidence: float
    reasoning: str
    generated_at: datetime

@dataclass
class AgentROI:
    """Return on Investment metrics for an agent"""
    agent_type: str
    time_period: str
    total_cost: float  # USD
    revenue_attributed: float  # USD
    roi_percentage: float  # (revenue - cost) / cost * 100
    tasks_completed: int
    success_rate: float  # 0-1
    average_response_time: float  # seconds
    quality_score: float  # 0-1
    efficiency_score: float  # 0-1
    business_impact_score: float  # 0-1
    key_contributions: List[str]
    improvement_opportunities: List[str]
    calculated_at: datetime = field(default_factory=datetime.now)

@dataclass
class CrewROI:
    """Return on Investment metrics for a CrewAI crew composition"""
    crew_type: str
    crew_id: str
    time_period: str
    total_cost: float  # USD
    revenue_attributed: float  # USD
    roi_percentage: float  # (revenue - cost) / cost * 100
    tasks_completed: int
    success_rate: float  # 0-1
    average_response_time: float  # seconds
    quality_score: float  # 0-1
    efficiency_score: float  # 0-1
    business_impact_score: float  # 0-1
    agent_composition: Dict[str, Any]  # Which agents and their roles
    key_contributions: List[str]
    improvement_opportunities: List[str]
    calculated_at: datetime = field(default_factory=datetime.now)

@dataclass
class CrewTemplate:
    """Template for CrewAI crew compositions"""
    crew_type: str
    description: str
    agent_composition: Dict[str, str]  # agent_type -> role
    typical_use_case: str
    expected_roi_range: Tuple[float, float]  # min, max percentage
    average_cost_per_task: float
    average_revenue_per_task: float

@dataclass
class ROIMetrics:
    """Detailed ROI calculation components"""
    operational_costs: Dict[str, float]  # API calls, compute, storage
    revenue_sources: Dict[str, float]  # Direct revenue, retention value, expansion
    quality_metrics: Dict[str, float]  # Accuracy, user satisfaction, error rates
    efficiency_metrics: Dict[str, float]  # Speed, resource usage, throughput
    business_metrics: Dict[str, float]  # Conversion rates, retention, expansion

class CriticAgent:
    """ARE Critic Agent - Outcome evaluation and learning"""

    def __init__(self):
        self.performance_history: Dict[str, List[PerformanceMetrics]] = {}
        self.learning_signals: List[LearningSignal] = []
        self.roi_reports: List[AgentROI] = []
        self.crew_roi_reports: List[CrewROI] = []
        self.anomaly_thresholds = {
            "quality_drop": 0.2,  # 20% drop in quality
            "success_rate_drop": 0.15,  # 15% drop in success rate
            "response_time_increase": 1.5,  # 50% increase in response time
            "anomaly_rate_threshold": 0.1  # 10% of outcomes are anomalous
        }

        # ROI calculation parameters
        self.cost_per_api_call = 0.01  # USD
        self.cost_per_compute_second = 0.02  # USD
        self.revenue_attribution_window = 30  # days

        # Crew templates (standard CrewAI compositions)
        self.crew_templates = self._load_crew_templates()

    def _load_crew_templates(self) -> Dict[str, CrewTemplate]:
        """Load standard CrewAI crew composition templates"""
        return {
            "cold_outreach": CrewTemplate(
                crew_type="cold_outreach",
                description="Multi-channel cold outreach and lead generation",
                agent_composition={
                    "planner": "campaign_strategy",
                    "executor": "outreach_coordination",
                    "rex": "real_time_optimization",
                    "brain": "content_generation"
                },
                typical_use_case="Generate qualified leads through cold email/SMS campaigns",
                expected_roi_range=(400.0, 700.0),
                average_cost_per_task=2.50,
                average_revenue_per_task=15.00
            ),
            "lead_revival": CrewTemplate(
                crew_type="lead_revival",
                description="Reactivate dormant leads with personalized sequences",
                agent_composition={
                    "planner": "revival_strategy",
                    "brain": "personalization_content",
                    "critic": "performance_analysis",
                    "services": "lead_scoring"
                },
                typical_use_case="Re-engage inactive leads with tailored messaging",
                expected_roi_range=(300.0, 600.0),
                average_cost_per_task=2.10,
                average_revenue_per_task=10.50
            ),
            "objection_handling": CrewTemplate(
                crew_type="objection_handling",
                description="Intelligent objection detection and response",
                agent_composition={
                    "executor": "response_coordination",
                    "brain": "objection_analysis",
                    "rex": "real_time_decisions",
                    "critic": "response_evaluation"
                },
                typical_use_case="Handle prospect objections with contextual responses",
                expected_roi_range=(350.0, 650.0),
                average_cost_per_task=1.80,
                average_revenue_per_task=11.50
            ),
            "conversion_optimization": CrewTemplate(
                crew_type="conversion_optimization",
                description="Optimize conversion funnels with A/B testing",
                agent_composition={
                    "planner": "experiment_design",
                    "brain": "content_variation",
                    "critic": "performance_analysis",
                    "services": "statistical_analysis"
                },
                typical_use_case="Improve conversion rates through data-driven optimization",
                expected_roi_range=(500.0, 900.0),
                average_cost_per_task=3.20,
                average_revenue_per_task=25.00
            ),
            "retention_management": CrewTemplate(
                crew_type="retention_management",
                description="Proactive customer retention and expansion",
                agent_composition={
                    "services": "churn_prediction",
                    "brain": "retention_messaging",
                    "planner": "expansion_strategy",
                    "critic": "retention_metrics"
                },
                typical_use_case="Reduce churn and increase customer lifetime value",
                expected_roi_range=(600.0, 1200.0),
                average_cost_per_task=4.50,
                average_revenue_per_task=35.00
            )
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main critic evaluation method"""
        action = input_data.get('action', 'evaluate')

        logger.info(f"Critic Agent executing action: {action}")

        try:
            if action == 'evaluate_performance':
                return await self._evaluate_performance(input_data)
            elif action == 'generate_insights':
                return await self._generate_insights(input_data)
            elif action == 'assess_outcomes':
                return await self._assess_outcomes(input_data)
            elif action == 'calculate_roi':
                return await self._calculate_roi(input_data)
            elif action == 'calculate_crew_roi':
                return await self._calculate_crew_roi(input_data)
            elif action == 'get_roi_report':
                return await self._get_roi_report(input_data)
            elif action == 'get_crew_roi_report':
                return await self._get_crew_roi_report(input_data)
            elif action == 'get_crew_templates':
                return self._get_crew_templates()
            elif action == 'get_learning_signals':
                return self._get_learning_signals()
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Critic execution failed: {e}")
            raise

    async def _evaluate_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main evaluation method - moved from run method"""
        execution_results = input_data.get("execution_results", [])
        social_intel = input_data.get("social_intelligence", {})
        logger.info(f"Evaluating {len(execution_results)} execution results and social intelligence")

        try:
            # Step 1: Analyze individual outcomes
            outcome_analyses = await self._analyze_outcomes(execution_results)

            # Step 2: Evaluate social intelligence quality
            social_evaluation = await self._evaluate_social_intelligence(social_intel)

            # Step 3: Assess latency performance
            latency_analysis = self._assess_latency_performance(execution_results)

            # Step 4: Aggregate performance metrics
            performance_metrics = self._aggregate_performance_metrics(outcome_analyses)

            # Step 5: Detect anomalies and trends
            anomalies = self._detect_anomalies(outcome_analyses, performance_metrics)

            # Step 6: Assess overall execution quality
            quality_assessment = self._assess_execution_quality(outcome_analyses, performance_metrics)

            # Step 7: Generate learning signals
            learning_signals = self._generate_learning_signals(
                outcome_analyses, performance_metrics, anomalies, quality_assessment
            )

            # Step 8: Filter and prioritize social insights
            filtered_insights = self._filter_social_insights(social_evaluation)

            # Step 9: Update performance history
            self._update_performance_history(performance_metrics)

            # Step 10: Generate improvement recommendations
            recommendations = self._generate_recommendations(
                performance_metrics, anomalies, learning_signals
            )

            evaluation_result = {
                "outcome_analyses": [analysis.__dict__ for analysis in outcome_analyses],
                "social_evaluation": social_evaluation,
                "latency_analysis": latency_analysis,
                "filtered_insights": filtered_insights,
                "performance_metrics": [metric.__dict__ for metric in performance_metrics],
                "anomalies": anomalies,
                "quality_assessment": quality_assessment,
                "learning_signals": [signal.__dict__ for signal in learning_signals],
                "recommendations": recommendations,
                "evaluated_at": datetime.now().isoformat()
            }

            logger.info(f"Critic evaluation complete: {len(learning_signals)} learning signals, {len(filtered_insights)} filtered insights")
            return evaluation_result

        except Exception as e:
            logger.error(f"Critic evaluation failed: {e}")
            raise

    async def _evaluate_social_intelligence(self, social_intel: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate quality and relevance of social intelligence data"""
        if not social_intel:
            return {"quality_score": 0, "insights_count": 0, "relevance_score": 0}

        insights = social_intel.get("insights", [])
        sentiment_data = social_intel.get("sentiment_distribution", {})

        # Evaluate data quality
        quality_score = self._assess_social_data_quality(insights)

        # Evaluate relevance
        relevance_score = self._assess_social_relevance(insights, sentiment_data)

        # Calculate actionability
        actionability_score = self._assess_actionability(insights)

        return {
            "quality_score": quality_score,
            "relevance_score": relevance_score,
            "actionability_score": actionability_score,
            "insights_count": len(insights),
            "sentiment_distribution": sentiment_data,
            "top_pain_points": social_intel.get("top_pain_points", []),
            "top_desires": social_intel.get("top_desires", []),
            "evaluation_timestamp": datetime.now().isoformat()
        }

    def _assess_latency_performance(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess latency performance across all execution results"""
        if not execution_results:
            return {"average_latency": 0, "max_latency": 0, "latency_violations": 0}

        latencies = [r.get("execution_time", 0) for r in execution_results]
        average_latency = mean(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0

        # Define latency thresholds (seconds)
        latency_thresholds = {
            "warning": 300,  # 5 minutes
            "critical": 600  # 10 minutes
        }

        violations = sum(1 for lat in latencies if lat > latency_thresholds["warning"])

        # Categorize latency performance
        if average_latency < 60:
            performance_rating = "excellent"
        elif average_latency < 180:
            performance_rating = "good"
        elif average_latency < 300:
            performance_rating = "fair"
        else:
            performance_rating = "poor"

        return {
            "average_latency": average_latency,
            "max_latency": max_latency,
            "min_latency": min(latencies) if latencies else 0,
            "latency_violations": violations,
            "performance_rating": performance_rating,
            "thresholds": latency_thresholds,
            "slowest_tasks": sorted(
                [(r.get("task_id"), r.get("execution_time", 0)) for r in execution_results],
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 slowest tasks
        }

    def _filter_social_insights(self, social_evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and prioritize social insights for RAG storage"""
        insights = social_evaluation.get("insights", [])
        filtered_insights = []

        quality_threshold = 0.6
        relevance_threshold = 0.5

        for insight in insights:
            quality = insight.get("confidence_score", 0)
            # Mock relevance calculation - in production, use ML model
            relevance = self._calculate_insight_relevance(insight)

            if quality >= quality_threshold and relevance >= relevance_threshold:
                filtered_insight = {
                    "id": insight.get("id"),
                    "content": insight.get("anonymized_content", ""),
                    "topic": insight.get("topic", ""),
                    "sentiment": insight.get("sentiment", ""),
                    "pain_points": insight.get("pain_points", []),
                    "desires": insight.get("desires", []),
                    "quality_score": quality,
                    "relevance_score": relevance,
                    "priority": "high" if quality > 0.8 and relevance > 0.7 else "medium",
                    "filtered_at": datetime.now().isoformat()
                }
                filtered_insights.append(filtered_insight)

        # Sort by priority and quality
        filtered_insights.sort(key=lambda x: (x["priority"] == "high", x["quality_score"]), reverse=True)

        return filtered_insights[:50]  # Limit to top 50 insights

    def _assess_social_data_quality(self, insights: List[Dict[str, Any]]) -> float:
        """Assess quality of social intelligence data"""
        if not insights:
            return 0.0

        quality_scores = []
        for insight in insights:
            score = 0.0
            if insight.get("confidence_score", 0) > 0.5:
                score += 0.3
            if insight.get("pain_points"):
                score += 0.3
            if insight.get("desires"):
                score += 0.2
            if len(insight.get("anonymized_content", "")) > 50:
                score += 0.2
            quality_scores.append(min(score, 1.0))

        return mean(quality_scores) if quality_scores else 0.0

    def _assess_social_relevance(self, insights: List[Dict[str, Any]], sentiment_data: Dict[str, float]) -> float:
        """Assess relevance of social intelligence to business goals"""
        if not insights:
            return 0.0

        # Check for business-relevant topics
        business_topics = ["sales", "marketing", "pricing", "support", "product"]
        relevant_insights = 0

        for insight in insights:
            topic = insight.get("topic", "").lower()
            if any(bt in topic for bt in business_topics):
                relevant_insights += 1

        topic_relevance = relevant_insights / len(insights) if insights else 0

        # Check sentiment balance (not too negative)
        negative_sentiment = sentiment_data.get("negative", 0)
        sentiment_relevance = max(0, 1 - negative_sentiment * 2)  # Penalize high negativity

        return (topic_relevance + sentiment_relevance) / 2

    def _assess_actionability(self, insights: List[Dict[str, Any]]) -> float:
        """Assess how actionable the social insights are"""
        if not insights:
            return 0.0

        actionable_count = 0
        for insight in insights:
            # Check for specific, actionable elements
            has_pain_points = len(insight.get("pain_points", [])) > 0
            has_desires = len(insight.get("desires", [])) > 0
            has_specific_content = len(insight.get("anonymized_content", "")) > 100

            if (has_pain_points or has_desires) and has_specific_content:
                actionable_count += 1

        return actionable_count / len(insights) if insights else 0.0

    def _calculate_insight_relevance(self, insight: Dict[str, Any]) -> float:
        """Calculate relevance score for a single insight"""
        relevance = 0.0

        # Business topic relevance
        topic = insight.get("topic", "").lower()
        business_keywords = ["sales", "revenue", "customers", "pricing", "support", "product"]
        if any(keyword in topic for keyword in business_keywords):
            relevance += 0.4

        # Content specificity
        content = insight.get("anonymized_content", "")
        if len(content) > 100:
            relevance += 0.3
        elif len(content) > 50:
            relevance += 0.2

        # Actionable elements
        if insight.get("pain_points") or insight.get("desires"):
            relevance += 0.3

        return min(relevance, 1.0)

    async def _analyze_outcomes(self, execution_results: List[Dict[str, Any]]) -> List[OutcomeAnalysis]:
        """Analyze individual execution outcomes"""
        analyses = []

        for result in execution_results:
            task_id = result.get("task_id")
            agent_cluster = result.get("agent_cluster")
            success = result.get("success", False)
            execution_time = result.get("execution_time", 0)
            error = result.get("error")

            # Extract metrics from result
            metrics = self._extract_metrics_from_result(result)

            for metric_name, value in metrics.items():
                # Determine expected range for this metric
                expected_range = self._get_expected_range(agent_cluster, metric_name)

                # Calculate deviation and anomaly score
                deviation = self._calculate_deviation(value, expected_range)
                anomaly_score = self._calculate_anomaly_score(deviation, metric_name)

                # Calculate quality score
                quality_score = self._calculate_quality_score(
                    agent_cluster, metric_name, value, success, execution_time
                )

                analysis = OutcomeAnalysis(
                    outcome_id=f"{task_id}_{metric_name}",
                    task_id=task_id,
                    agent_cluster=agent_cluster,
                    metric=metric_name,
                    value=value,
                    expected_range=expected_range,
                    deviation=deviation,
                    anomaly_score=anomaly_score,
                    quality_score=quality_score,
                    timestamp=datetime.now()
                )

                analyses.append(analysis)

        logger.debug(f"Analyzed {len(analyses)} outcome metrics")
        return analyses

    def _extract_metrics_from_result(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Extract measurable metrics from execution result"""
        metrics = {}

        # Success rate
        metrics["success_rate"] = 1.0 if result.get("success", False) else 0.0

        # Execution time
        execution_time = result.get("execution_time", 0)
        metrics["execution_time"] = execution_time

        # Error rate (inverse of success)
        metrics["error_rate"] = 0.0 if result.get("success", False) else 1.0

        # Extract additional metrics from output if available
        output = result.get("output", {})
        if isinstance(output, dict):
            if "quality_score" in output:
                metrics["quality_score"] = output["quality_score"]
            if "confidence" in output:
                metrics["confidence"] = output["confidence"]
            if "efficiency" in output:
                metrics["efficiency"] = output["efficiency"]

        return metrics

    def _get_expected_range(self, agent_cluster: str, metric: str) -> Tuple[float, float]:
        """Get expected value range for a metric"""
        # These would be learned from historical data
        # For now, use static expectations
        expectations = {
            "brain": {
                "success_rate": (0.7, 0.95),
                "execution_time": (5, 120),
                "error_rate": (0.0, 0.3),
                "quality_score": (0.6, 1.0),
                "confidence": (0.5, 1.0)
            },
            "crewai": {
                "success_rate": (0.8, 0.98),
                "execution_time": (10, 300),
                "error_rate": (0.0, 0.2),
                "quality_score": (0.7, 1.0),
                "confidence": (0.6, 1.0)
            },
            "rex": {
                "success_rate": (0.85, 0.99),
                "execution_time": (1, 60),
                "error_rate": (0.0, 0.15),
                "quality_score": (0.8, 1.0),
                "confidence": (0.7, 1.0)
            },
            "services": {
                "success_rate": (0.75, 0.95),
                "execution_time": (30, 600),
                "error_rate": (0.0, 0.25),
                "quality_score": (0.65, 1.0),
                "confidence": (0.5, 1.0)
            }
        }

        cluster_expectations = expectations.get(agent_cluster, expectations["crewai"])
        return cluster_expectations.get(metric, (0.0, 1.0))

    def _calculate_deviation(self, value: float, expected_range: Tuple[float, float]) -> float:
        """Calculate how much a value deviates from expected range"""
        min_val, max_val = expected_range
        range_center = (min_val + max_val) / 2
        range_size = max_val - min_val

        if range_size == 0:
            return 0.0

        return abs(value - range_center) / (range_size / 2)

    def _calculate_anomaly_score(self, deviation: float, metric: str) -> float:
        """Calculate anomaly score based on deviation"""
        # Higher deviation = higher anomaly score
        # Different metrics have different sensitivity
        sensitivity = {
            "success_rate": 2.0,
            "error_rate": 2.0,
            "execution_time": 1.5,
            "quality_score": 1.0,
            "confidence": 1.0
        }.get(metric, 1.0)

        # Sigmoid function to normalize anomaly score between 0 and 1
        anomaly_score = 1 / (1 + 2.718 ** (-sensitivity * (deviation - 1)))
        return min(anomaly_score, 1.0)

    def _calculate_quality_score(self, agent_cluster: str, metric: str, value: float,
                               success: bool, execution_time: float) -> float:
        """Calculate overall quality score for an outcome"""
        base_score = value

        # Adjust for success/failure
        if not success:
            base_score *= 0.3  # Significant penalty for failure

        # Adjust for execution time (faster is better, but not too fast)
        if execution_time > 0:
            optimal_time = self._get_optimal_execution_time(agent_cluster, metric)
            time_ratio = execution_time / optimal_time
            if time_ratio < 0.5:  # Too fast might indicate low quality
                base_score *= 0.9
            elif time_ratio > 2.0:  # Too slow
                base_score *= 0.8

        return max(0.0, min(base_score, 1.0))

    def _get_optimal_execution_time(self, agent_cluster: str, metric: str) -> float:
        """Get optimal execution time for agent/metric combination"""
        optimal_times = {
            "brain": {"default": 30},
            "crewai": {"default": 60},
            "rex": {"default": 10},
            "services": {"default": 120}
        }
        return optimal_times.get(agent_cluster, {}).get(metric, optimal_times[agent_cluster]["default"])

    def _aggregate_performance_metrics(self, analyses: List[OutcomeAnalysis]) -> List[PerformanceMetrics]:
        """Aggregate performance metrics by agent cluster"""
        cluster_groups = {}
        now = datetime.now()
        time_window = timedelta(hours=1)  # 1-hour window

        # Group analyses by cluster
        for analysis in analyses:
            if analysis.agent_cluster not in cluster_groups:
                cluster_groups[analysis.agent_cluster] = []
            cluster_groups[analysis.agent_cluster].append(analysis)

        metrics = []
        for cluster, cluster_analyses in cluster_groups.items():
            # Calculate aggregate metrics
            total_outcomes = len(cluster_analyses)
            success_rate = mean(a.value for a in cluster_analyses if a.metric == "success_rate") if any(a.metric == "success_rate" for a in cluster_analyses) else 0
            average_quality = mean(a.quality_score for a in cluster_analyses)
            average_response_time = mean(a.value for a in cluster_analyses if a.metric == "execution_time") if any(a.metric == "execution_time" for a in cluster_analyses) else 0
            anomaly_rate = mean(a.anomaly_score for a in cluster_analyses)

            # Determine trend (would compare with historical data)
            trend_direction = self._calculate_trend(cluster, success_rate, average_quality)

            # Calculate confidence in metrics
            confidence_score = self._calculate_confidence_score(total_outcomes, anomaly_rate)

            metric = PerformanceMetrics(
                agent_cluster=cluster,
                time_range=(now - time_window, now),
                total_outcomes=total_outcomes,
                success_rate=success_rate,
                average_quality=average_quality,
                average_response_time=average_response_time,
                anomaly_rate=anomaly_rate,
                trend_direction=trend_direction,
                confidence_score=confidence_score
            )

            metrics.append(metric)

        return metrics

    def _calculate_trend(self, cluster: str, current_success: float, current_quality: float) -> str:
        """Calculate performance trend for an agent cluster"""
        # In a real implementation, this would compare with historical data
        # For now, return "stable"
        return "stable"

    def _calculate_confidence_score(self, sample_size: int, anomaly_rate: float) -> float:
        """Calculate confidence score in performance metrics"""
        # Higher sample size and lower anomaly rate = higher confidence
        size_confidence = min(sample_size / 10, 1.0)  # Max confidence at 10 samples
        anomaly_confidence = 1.0 - anomaly_rate

        return (size_confidence + anomaly_confidence) / 2

    def _detect_anomalies(self, analyses: List[OutcomeAnalysis], metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Detect anomalies in performance"""
        anomalies = []

        # Check for metric anomalies
        for analysis in analyses:
            if analysis.anomaly_score > 0.7:  # High anomaly threshold
                anomalies.append({
                    "type": "metric_anomaly",
                    "severity": "high" if analysis.anomaly_score > 0.9 else "medium",
                    "description": f"Anomalous {analysis.metric} value for {analysis.agent_cluster}",
                    "details": {
                        "task_id": analysis.task_id,
                        "metric": analysis.metric,
                        "value": analysis.value,
                        "expected_range": analysis.expected_range,
                        "anomaly_score": analysis.anomaly_score
                    },
                    "detected_at": analysis.timestamp.isoformat()
                })

        # Check for cluster-level anomalies
        for metric in metrics:
            if metric.anomaly_rate > self.anomaly_thresholds["anomaly_rate_threshold"]:
                anomalies.append({
                    "type": "cluster_anomaly",
                    "severity": "high",
                    "description": f"High anomaly rate in {metric.agent_cluster} cluster",
                    "details": {
                        "cluster": metric.agent_cluster,
                        "anomaly_rate": metric.anomaly_rate,
                        "threshold": self.anomaly_thresholds["anomaly_rate_threshold"]
                    },
                    "detected_at": datetime.now().isoformat()
                })

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def _assess_execution_quality(self, analyses: List[OutcomeAnalysis], metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Assess overall execution quality"""
        if not analyses:
            return {"overall_score": 0, "assessment": "no_data"}

        # Calculate weighted quality score
        total_weight = 0
        weighted_score = 0

        for analysis in analyses:
            weight = self._get_metric_weight(analysis.metric)
            weighted_score += analysis.quality_score * weight
            total_weight += weight

        overall_score = weighted_score / total_weight if total_weight > 0 else 0

        # Determine assessment
        if overall_score >= 0.8:
            assessment = "excellent"
        elif overall_score >= 0.6:
            assessment = "good"
        elif overall_score >= 0.4:
            assessment = "fair"
        else:
            assessment = "poor"

        return {
            "overall_score": overall_score,
            "assessment": assessment,
            "metrics_count": len(analyses),
            "clusters_evaluated": len(set(a.agent_cluster for a in analyses))
        }

    def _get_metric_weight(self, metric: str) -> float:
        """Get weight for a metric in quality calculation"""
        weights = {
            "success_rate": 3.0,
            "quality_score": 2.0,
            "error_rate": 2.0,
            "execution_time": 1.0,
            "confidence": 1.5
        }
        return weights.get(metric, 1.0)

    def _generate_learning_signals(self, analyses: List[OutcomeAnalysis],
                                 metrics: List[PerformanceMetrics],
                                 anomalies: List[Dict[str, Any]],
                                 quality_assessment: Dict[str, Any]) -> List[LearningSignal]:
        """Generate learning signals for system improvement"""
        signals = []

        # Signal 1: Agent preference adjustments
        for metric in metrics:
            if metric.success_rate > 0.9 and metric.confidence_score > 0.8:
                signals.append(LearningSignal(
                    signal_type="agent_preference",
                    target=metric.agent_cluster,
                    action="increase_weight",
                    value=0.1,  # 10% increase in preference
                    confidence=metric.confidence_score,
                    reasoning=f"High performance cluster: {metric.success_rate:.2%} success rate",
                    generated_at=datetime.now()
                ))

        # Signal 2: Routing rule updates
        for anomaly in anomalies:
            if anomaly["type"] == "cluster_anomaly":
                cluster = anomaly["details"]["cluster"]
                signals.append(LearningSignal(
                    signal_type="routing_rule",
                    target=f"{cluster}_load_balancing",
                    action="add_rule",
                    value={"condition": "high_load", "action": "reduce_priority"},
                    confidence=0.8,
                    reasoning=f"High anomaly rate in {cluster} cluster indicates overload",
                    generated_at=datetime.now()
                ))

        # Signal 3: Parameter optimizations
        if quality_assessment["overall_score"] < 0.7:
            signals.append(LearningSignal(
                signal_type="parameter_adjustment",
                target="execution_timeouts",
                action="increase_value",
                value=30,  # Add 30 seconds to timeouts
                confidence=0.7,
                reasoning=f"Low quality score suggests timing issues",
                generated_at=datetime.now()
            ))

        logger.info(f"Generated {len(signals)} learning signals")
        return signals

    def _generate_recommendations(self, metrics: List[PerformanceMetrics],
                                anomalies: List[Dict[str, Any]],
                                signals: List[LearningSignal]) -> List[str]:
        """Generate human-readable improvement recommendations"""
        recommendations = []

        # Performance-based recommendations
        for metric in metrics:
            if metric.success_rate < 0.8:
                recommendations.append(f"Improve {metric.agent_cluster} success rate (currently {metric.success_rate:.1%})")
            if metric.average_response_time > 120:
                recommendations.append(f"Optimize {metric.agent_cluster} response time (currently {metric.average_response_time:.1f}s)")

        # Anomaly-based recommendations
        if anomalies:
            recommendations.append(f"Address {len(anomalies)} detected anomalies")

        # Learning-based recommendations
        if signals:
            recommendations.append(f"Apply {len(signals)} generated learning signals")

        return recommendations

    def _update_performance_history(self, metrics: List[PerformanceMetrics]):
        """Update performance history for trend analysis"""
        for metric in metrics:
            cluster = metric.agent_cluster
            if cluster not in self.performance_history:
                self.performance_history[cluster] = []
            self.performance_history[cluster].append(metric)

            # Keep only last 100 metrics per cluster
            if len(self.performance_history[cluster]) > 100:
                self.performance_history[cluster] = self.performance_history[cluster][-100:]

    async def get_performance_history(self, cluster: str, hours: int = 24) -> List[PerformanceMetrics]:
        """Get performance history for an agent cluster"""
        if cluster not in self.performance_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.performance_history[cluster] if m.time_range[1] > cutoff_time]

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get aggregated learning insights"""
        return {
            "total_signals": len(self.learning_signals),
            "recent_signals": [s.__dict__ for s in self.learning_signals[-10:]],  # Last 10 signals
            "performance_trends": {
                cluster: len(history) for cluster, history in self.performance_history.items()
            },
            "generated_at": datetime.now().isoformat()
        }

    async def _calculate_roi(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Return on Investment for agents"""
        agent_type = input_data.get('agent_type')
        time_period = input_data.get('time_period', 'last_30_days')

        if not agent_type:
            raise ValueError("agent_type is required for ROI calculation")

        logger.info(f"Calculating ROI for {agent_type} over {time_period}")

        # Get performance data for the agent
        performance_data = await self._get_agent_performance_data(agent_type, time_period)

        # Calculate operational costs
        operational_costs = self._calculate_operational_costs(performance_data)

        # Calculate revenue attribution
        revenue_attribution = await self._calculate_revenue_attribution(agent_type, time_period)

        # Calculate quality and efficiency scores
        quality_metrics = self._calculate_quality_metrics(performance_data)
        efficiency_metrics = self._calculate_efficiency_metrics(performance_data)

        # Calculate business impact
        business_impact = await self._calculate_business_impact(agent_type, performance_data)

        # Calculate ROI
        total_cost = sum(operational_costs.values())
        total_revenue = sum(revenue_attribution.values())
        roi_percentage = (total_revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0

        # Generate insights and recommendations
        key_contributions = self._identify_key_contributions(agent_type, performance_data, revenue_attribution)
        improvement_opportunities = self._identify_improvement_opportunities(performance_data, quality_metrics)

        roi_report = AgentROI(
            agent_type=agent_type,
            time_period=time_period,
            total_cost=total_cost,
            revenue_attributed=total_revenue,
            roi_percentage=roi_percentage,
            tasks_completed=performance_data.get('total_tasks', 0),
            success_rate=performance_data.get('success_rate', 0),
            average_response_time=performance_data.get('avg_response_time', 0),
            quality_score=quality_metrics.get('overall_quality', 0),
            efficiency_score=efficiency_metrics.get('overall_efficiency', 0),
            business_impact_score=business_impact.get('overall_impact', 0),
            key_contributions=key_contributions,
            improvement_opportunities=improvement_opportunities,
            calculated_at=datetime.now()
        )

        self.roi_reports.append(roi_report)

        logger.info(f"ROI calculated for {agent_type}: {roi_percentage:.1f}% ROI")

        return {
            "roi_report": roi_report.__dict__,
            "detailed_metrics": {
                "operational_costs": operational_costs,
                "revenue_sources": revenue_attribution,
                "quality_metrics": quality_metrics,
                "efficiency_metrics": efficiency_metrics,
                "business_impact": business_impact
            }
        }

    async def _get_roi_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get ROI report for an agent or all agents"""
        agent_type = input_data.get('agent_type')
        time_period = input_data.get('time_period', 'last_30_days')

        if agent_type:
            # Get specific agent ROI
            reports = [r for r in self.roi_reports
                      if r.agent_type == agent_type and r.time_period == time_period]
            if reports:
                latest_report = max(reports, key=lambda r: r.calculated_at)
                return {"roi_report": latest_report.__dict__}
            else:
                return {"error": f"No ROI report found for {agent_type} in {time_period}"}
        else:
            # Get summary of all agents
            agent_summaries = {}
            for report in self.roi_reports:
                if report.time_period == time_period:
                    agent_summaries[report.agent_type] = {
                        "roi_percentage": report.roi_percentage,
                        "total_cost": report.total_cost,
                        "revenue_attributed": report.revenue_attributed,
                        "tasks_completed": report.tasks_completed,
                        "success_rate": report.success_rate,
                        "calculated_at": report.calculated_at.isoformat()
                    }

            return {
                "time_period": time_period,
                "agent_summaries": agent_summaries,
                "total_agents": len(agent_summaries),
                "generated_at": datetime.now().isoformat()
            }

    async def _get_agent_performance_data(self, agent_type: str, time_period: str) -> Dict[str, Any]:
        """Get performance data for an agent over a time period"""
        # Convert time period to hours
        period_hours = self._parse_time_period(time_period)

        # Get performance history
        history = await self.get_performance_history(agent_type, period_hours)

        if not history:
            return {"total_tasks": 0, "success_rate": 0, "avg_response_time": 0}

        # Aggregate performance data
        total_tasks = sum(h.total_outcomes for h in history)
        success_rates = [h.success_rate for h in history if h.success_rate > 0]
        response_times = [h.average_response_time for h in history if h.average_response_time > 0]

        return {
            "total_tasks": total_tasks,
            "success_rate": mean(success_rates) if success_rates else 0,
            "avg_response_time": mean(response_times) if response_times else 0,
            "avg_quality": mean([h.average_quality for h in history if h.average_quality > 0]) if history else 0,
            "anomaly_rate": mean([h.anomaly_rate for h in history if h.anomaly_rate >= 0]) if history else 0,
            "performance_history": [h.__dict__ for h in history]
        }

    def _calculate_operational_costs(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate operational costs for agent execution"""
        total_tasks = performance_data.get('total_tasks', 0)
        avg_response_time = performance_data.get('avg_response_time', 0)

        # API call costs
        api_costs = total_tasks * self.cost_per_api_call

        # Compute costs (based on execution time)
        compute_costs = total_tasks * avg_response_time * self.cost_per_compute_second

        # Storage costs (estimate based on tasks)
        storage_costs = total_tasks * 0.001  # $0.001 per task for data storage

        return {
            "api_calls": api_costs,
            "compute": compute_costs,
            "storage": storage_costs,
            "total": api_costs + compute_costs + storage_costs
        }

    async def _calculate_revenue_attribution(self, agent_type: str, time_period: str) -> Dict[str, float]:
        """Calculate revenue attributed to agent performance"""
        # This is a simplified attribution model
        # In production, this would integrate with actual revenue data

        performance_data = await self._get_agent_performance_data(agent_type, time_period)
        success_rate = performance_data.get('success_rate', 0)
        total_tasks = performance_data.get('total_tasks', 0)

        # Revenue attribution based on agent type and performance
        base_revenue_per_task = {
            "brain": 50.0,      # Content generation leads to conversions
            "crewai": 75.0,     # Outreach and meeting booking
            "rex": 100.0,       # Real-time decisions drive revenue
            "services": 200.0,  # Revival and forecasting services
            "social_listening": 25.0  # Intelligence improves targeting
        }.get(agent_type, 25.0)

        # Adjust for success rate
        effective_revenue = base_revenue_per_task * success_rate * total_tasks

        # Attribution windows (different agents have different revenue lag times)
        attribution_windows = {
            "brain": {"immediate": 0.3, "short_term": 0.5, "long_term": 0.2},
            "crewai": {"immediate": 0.6, "short_term": 0.3, "long_term": 0.1},
            "rex": {"immediate": 0.8, "short_term": 0.15, "long_term": 0.05},
            "services": {"immediate": 0.2, "short_term": 0.4, "long_term": 0.4},
            "social_listening": {"immediate": 0.1, "short_term": 0.3, "long_term": 0.6}
        }

        window = attribution_windows.get(agent_type, {"immediate": 0.4, "short_term": 0.4, "long_term": 0.2})

        return {
            "immediate_revenue": effective_revenue * window["immediate"],
            "short_term_revenue": effective_revenue * window["short_term"],
            "long_term_revenue": effective_revenue * window["long_term"],
            "total_attributed": effective_revenue
        }

    def _calculate_quality_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics"""
        success_rate = performance_data.get('success_rate', 0)
        avg_quality = performance_data.get('avg_quality', 0)
        anomaly_rate = performance_data.get('anomaly_rate', 0)

        # Overall quality score (weighted combination)
        overall_quality = (
            success_rate * 0.4 +
            avg_quality * 0.4 +
            (1 - anomaly_rate) * 0.2  # Invert anomaly rate
        )

        return {
            "success_rate": success_rate,
            "average_quality": avg_quality,
            "anomaly_rate": anomaly_rate,
            "overall_quality": overall_quality
        }

    def _calculate_efficiency_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate efficiency metrics"""
        avg_response_time = performance_data.get('avg_response_time', 0)
        total_tasks = performance_data.get('total_tasks', 0)

        # Throughput (tasks per hour)
        time_period_hours = 24  # Assuming daily calculation
        throughput = total_tasks / time_period_hours if time_period_hours > 0 else 0

        # Efficiency score (higher throughput + lower response time = better)
        # Normalize response time (lower is better, so invert)
        response_time_score = max(0, 1 - (avg_response_time / 300))  # Assume 5min is baseline
        throughput_score = min(1.0, throughput / 10)  # Assume 10 tasks/hour is excellent

        overall_efficiency = (response_time_score + throughput_score) / 2

        return {
            "average_response_time": avg_response_time,
            "throughput_tasks_per_hour": throughput,
            "response_time_score": response_time_score,
            "throughput_score": throughput_score,
            "overall_efficiency": overall_efficiency
        }

    async def _calculate_business_impact(self, agent_type: str, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate business impact metrics"""
        success_rate = performance_data.get('success_rate', 0)
        total_tasks = performance_data.get('total_tasks', 0)

        # Business impact varies by agent type
        impact_multipliers = {
            "brain": {"conversion_impact": 0.7, "retention_impact": 0.2, "expansion_impact": 0.1},
            "crewai": {"conversion_impact": 0.8, "retention_impact": 0.1, "expansion_impact": 0.1},
            "rex": {"conversion_impact": 0.9, "retention_impact": 0.05, "expansion_impact": 0.05},
            "services": {"conversion_impact": 0.5, "retention_impact": 0.3, "expansion_impact": 0.2},
            "social_listening": {"conversion_impact": 0.6, "retention_impact": 0.3, "expansion_impact": 0.1}
        }

        multipliers = impact_multipliers.get(agent_type, {"conversion_impact": 0.5, "retention_impact": 0.3, "expansion_impact": 0.2})

        # Calculate impact scores
        conversion_impact = success_rate * multipliers["conversion_impact"] * total_tasks
        retention_impact = success_rate * multipliers["retention_impact"] * total_tasks
        expansion_impact = success_rate * multipliers["expansion_impact"] * total_tasks

        overall_impact = (conversion_impact + retention_impact + expansion_impact) / total_tasks if total_tasks > 0 else 0

        return {
            "conversion_impact": conversion_impact,
            "retention_impact": retention_impact,
            "expansion_impact": expansion_impact,
            "overall_impact": overall_impact
        }

    def _identify_key_contributions(self, agent_type: str, performance_data: Dict[str, Any],
                                  revenue_attribution: Dict[str, float]) -> List[str]:
        """Identify key contributions of the agent"""
        contributions = []
        success_rate = performance_data.get('success_rate', 0)
        total_tasks = performance_data.get('total_tasks', 0)
        total_revenue = revenue_attribution.get('total_attributed', 0)

        if success_rate > 0.9:
            contributions.append(f"Exceptional {success_rate:.1%} success rate across {total_tasks} tasks")

        if total_revenue > 1000:
            contributions.append(f"Generated ${total_revenue:.0f} in attributed revenue")

        # Agent-specific contributions
        if agent_type == "brain":
            contributions.append("High-quality content generation and strategic insights")
        elif agent_type == "crewai":
            contributions.append("Effective lead outreach and meeting coordination")
        elif agent_type == "rex":
            contributions.append("Real-time decision optimization and resource allocation")
        elif agent_type == "services":
            contributions.append("Predictive analytics and customer lifecycle management")
        elif agent_type == "social_listening":
            contributions.append("Market intelligence and trend analysis")

        return contributions[:5]  # Limit to top 5

    def _identify_improvement_opportunities(self, performance_data: Dict[str, Any],
                                          quality_metrics: Dict[str, float]) -> List[str]:
        """Identify improvement opportunities"""
        opportunities = []
        success_rate = performance_data.get('success_rate', 0)
        avg_response_time = performance_data.get('avg_response_time', 0)
        anomaly_rate = performance_data.get('anomaly_rate', 0)

        if success_rate < 0.8:
            opportunities.append(f"Improve success rate (currently {success_rate:.1%})")

        if avg_response_time > 120:
            opportunities.append(f"Reduce response time (currently {avg_response_time:.1f}s)")

        if anomaly_rate > 0.1:
            opportunities.append(f"Reduce anomaly rate (currently {anomaly_rate:.1%})")

        if quality_metrics.get('overall_quality', 0) < 0.7:
            opportunities.append("Enhance output quality and consistency")

        return opportunities[:5]  # Limit to top 5

    def _parse_time_period(self, time_period: str) -> int:
        """Parse time period string to hours"""
        period_map = {
            "last_hour": 1,
            "last_6_hours": 6,
            "last_24_hours": 24,
            "last_7_days": 168,
            "last_30_days": 720,
            "last_90_days": 2160
        }
        return period_map.get(time_period, 720)  # Default to 30 days

    async def _calculate_crew_roi(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Return on Investment for a CrewAI crew composition"""
        crew_type = input_data.get('crew_type')
        crew_id = input_data.get('crew_id')
        time_period = input_data.get('time_period', 'last_30_days')

        if not crew_type:
            raise ValueError("crew_type is required for crew ROI calculation")

        logger.info(f"Calculating ROI for crew {crew_type} ({crew_id or 'all'}) over {time_period}")

        # Get crew performance data
        crew_performance = await self._get_crew_performance_data(crew_type, crew_id, time_period)

        # Get crew template for expected metrics
        template = self.crew_templates.get(crew_type)
        if not template:
            raise ValueError(f"Unknown crew type: {crew_type}")

        # Calculate operational costs (distributed across agents in crew)
        operational_costs = self._calculate_crew_operational_costs(crew_performance, template)

        # Calculate revenue attribution based on crew type
        revenue_attribution = await self._calculate_crew_revenue_attribution(crew_type, crew_performance, template)

        # Calculate quality and efficiency scores
        quality_metrics = self._calculate_crew_quality_metrics(crew_performance)
        efficiency_metrics = self._calculate_crew_efficiency_metrics(crew_performance)

        # Calculate business impact
        business_impact = await self._calculate_crew_business_impact(crew_type, crew_performance)

        # Calculate ROI
        total_cost = sum(operational_costs.values())
        total_revenue = sum(revenue_attribution.values())
        roi_percentage = (total_revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0

        crew_roi_report = CrewROI(
            crew_type=crew_type,
            crew_id=crew_id or "aggregated",
            time_period=time_period,
            total_cost=total_cost,
            revenue_attributed=total_revenue,
            roi_percentage=roi_percentage,
            tasks_completed=crew_performance.get('total_tasks', 0),
            success_rate=crew_performance.get('success_rate', 0),
            average_response_time=crew_performance.get('avg_response_time', 0),
            quality_score=quality_metrics.get('overall_quality', 0),
            efficiency_score=efficiency_metrics.get('overall_efficiency', 0),
            business_impact_score=business_impact.get('overall_impact', 0),
            agent_composition=template.agent_composition,
            key_contributions=self._identify_crew_contributions(crew_type, crew_performance, revenue_attribution),
            improvement_opportunities=self._identify_crew_improvements(crew_performance, quality_metrics),
            calculated_at=datetime.now()
        )

        self.crew_roi_reports.append(crew_roi_report)

        logger.info(f"Crew ROI calculated for {crew_type}: {roi_percentage:.1f}% ROI")

        return {
            "crew_roi_report": crew_roi_report.__dict__,
            "crew_template": template.__dict__,
            "detailed_metrics": {
                "operational_costs": operational_costs,
                "revenue_sources": revenue_attribution,
                "quality_metrics": quality_metrics,
                "efficiency_metrics": efficiency_metrics,
                "business_impact": business_impact
            }
        }

    async def _get_crew_roi_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get crew ROI report"""
        crew_type = input_data.get('crew_type')
        crew_id = input_data.get('crew_id')
        time_period = input_data.get('time_period', 'last_30_days')

        if crew_type:
            # Get specific crew type ROI
            reports = [r for r in self.crew_roi_reports
                      if r.crew_type == crew_type and r.time_period == time_period]
            if reports:
                latest_report = max(reports, key=lambda r: r.calculated_at)
                return {"crew_roi_report": latest_report.__dict__}
            else:
                return {"error": f"No crew ROI report found for {crew_type} in {time_period}"}
        else:
            # Get summary of all crew types
            crew_summaries = {}
            for report in self.crew_roi_reports:
                if report.time_period == time_period:
                    crew_summaries[report.crew_type] = {
                        "roi_percentage": report.roi_percentage,
                        "total_cost": report.total_cost,
                        "revenue_attributed": report.revenue_attributed,
                        "tasks_completed": report.tasks_completed,
                        "success_rate": report.success_rate,
                        "agent_composition": report.agent_composition,
                        "calculated_at": report.calculated_at.isoformat()
                    }

            return {
                "time_period": time_period,
                "crew_summaries": crew_summaries,
                "total_crews": len(crew_summaries),
                "generated_at": datetime.now().isoformat()
            }

    def _get_crew_templates(self) -> Dict[str, Any]:
        """Get available crew templates"""
        return {
            crew_type: {
                "description": template.description,
                "agent_composition": template.agent_composition,
                "typical_use_case": template.typical_use_case,
                "expected_roi_range": template.expected_roi_range,
                "average_cost_per_task": template.average_cost_per_task,
                "average_revenue_per_task": template.average_revenue_per_task
            }
            for crew_type, template in self.crew_templates.items()
        }

    async def _get_crew_performance_data(self, crew_type: str, crew_id: Optional[str], time_period: str) -> Dict[str, Any]:
        """Get performance data for a crew composition"""
        # In practice, this would query execution results tagged with crew_type and crew_id
        # For now, simulate based on crew type characteristics

        period_hours = self._parse_time_period(time_period)
        template = self.crew_templates.get(crew_type)

        if not template:
            return {"total_tasks": 0, "success_rate": 0, "avg_response_time": 0}

        # Simulate performance based on crew type (in production, use actual execution data)
        base_performance = {
            "cold_outreach": {"success_rate": 0.87, "avg_response_time": 45, "tasks_per_hour": 80},
            "lead_revival": {"success_rate": 0.82, "avg_response_time": 60, "tasks_per_hour": 60},
            "objection_handling": {"success_rate": 0.89, "avg_response_time": 30, "tasks_per_hour": 120},
            "conversion_optimization": {"success_rate": 0.91, "avg_response_time": 90, "tasks_per_hour": 40},
            "retention_management": {"success_rate": 0.85, "avg_response_time": 120, "tasks_per_hour": 30}
        }

        perf = base_performance.get(crew_type, {"success_rate": 0.8, "avg_response_time": 60, "tasks_per_hour": 60})

        # Calculate total tasks based on time period
        total_tasks = int(perf["tasks_per_hour"] * (period_hours / 24) * 24)  # 24 is typical working hours per day

        return {
            "total_tasks": total_tasks,
            "success_rate": perf["success_rate"],
            "avg_response_time": perf["avg_response_time"],
            "avg_quality": 0.88,  # Assume high quality for crew operations
            "anomaly_rate": 0.02,  # Low anomaly rate for coordinated crews
            "performance_history": []  # Would contain actual execution data
        }

    def _calculate_crew_operational_costs(self, crew_performance: Dict[str, Any], template: CrewTemplate) -> Dict[str, float]:
        """Calculate operational costs for crew execution"""
        total_tasks = crew_performance.get('total_tasks', 0)
        avg_response_time = crew_performance.get('avg_response_time', 0)

        # Base costs per task (CrewAI framework overhead)
        crewai_overhead = total_tasks * 0.50  # $0.50 per task for CrewAI orchestration

        # Agent-specific costs (distributed across crew composition)
        agent_costs = 0
        for agent_type, role in template.agent_composition.items():
            # Each agent in crew contributes to cost
            agent_tasks = total_tasks * (1.0 / len(template.agent_composition))  # Distribute across agents
            agent_costs += agent_tasks * self._get_agent_cost_per_task(agent_type)

        # Compute costs based on response time
        compute_costs = total_tasks * avg_response_time * self.cost_per_compute_second

        return {
            "crewai_orchestration": crewai_overhead,
            "agent_operations": agent_costs,
            "compute_resources": compute_costs,
            "total": crewai_overhead + agent_costs + compute_costs
        }

    def _get_agent_cost_per_task(self, agent_type: str) -> float:
        """Get cost per task for an agent type"""
        cost_map = {
            "planner": 0.05,
            "executor": 0.08,
            "critic": 0.06,
            "brain": 0.15,
            "rex": 0.10,
            "services": 0.12
        }
        return cost_map.get(agent_type, 0.10)

    async def _calculate_crew_revenue_attribution(self, crew_type: str, crew_performance: Dict[str, Any], template: CrewTemplate) -> Dict[str, float]:
        """Calculate revenue attributed to crew performance"""
        success_rate = crew_performance.get('success_rate', 0)
        total_tasks = crew_performance.get('total_tasks', 0)

        # Crew-type specific revenue attribution
        revenue_models = {
            "cold_outreach": {
                "meetings_booked": 150.0,  # Revenue per meeting booked
                "leads_generated": 25.0,   # Revenue per qualified lead
                "attribution_window": {"immediate": 0.4, "short_term": 0.4, "long_term": 0.2}
            },
            "lead_revival": {
                "reactivations": 200.0,    # Revenue per reactivation
                "meetings_from_revival": 175.0,
                "attribution_window": {"immediate": 0.3, "short_term": 0.5, "long_term": 0.2}
            },
            "objection_handling": {
                "objections_resolved": 125.0,
                "meetings_saved": 150.0,
                "attribution_window": {"immediate": 0.6, "short_term": 0.3, "long_term": 0.1}
            },
            "conversion_optimization": {
                "conversion_improvement": 500.0,  # Revenue from conversion lift
                "ab_test_value": 300.0,
                "attribution_window": {"immediate": 0.2, "short_term": 0.6, "long_term": 0.2}
            },
            "retention_management": {
                "churn_prevention": 750.0,  # Revenue from retained customers
                "expansion_revenue": 400.0,
                "attribution_window": {"immediate": 0.1, "short_term": 0.3, "long_term": 0.6}
            }
        }

        model = revenue_models.get(crew_type, {
            "default_revenue": 100.0,
            "attribution_window": {"immediate": 0.4, "short_term": 0.4, "long_term": 0.2}
        })

        # Calculate effective revenue based on success rate
        base_revenue_per_task = template.average_revenue_per_task
        effective_revenue = base_revenue_per_task * success_rate * total_tasks

        # Apply attribution windows
        window = model.get("attribution_window", {"immediate": 0.4, "short_term": 0.4, "long_term": 0.2})

        return {
            "immediate_revenue": effective_revenue * window["immediate"],
            "short_term_revenue": effective_revenue * window["short_term"],
            "long_term_revenue": effective_revenue * window["long_term"],
            "total_attributed": effective_revenue
        }

    def _calculate_crew_quality_metrics(self, crew_performance: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for crew performance"""
        success_rate = crew_performance.get('success_rate', 0)
        avg_quality = crew_performance.get('avg_quality', 0)
        anomaly_rate = crew_performance.get('anomaly_rate', 0)

        # Crew quality considers coordination effectiveness
        coordination_bonus = 0.05  # Crews are more effective than individual agents
        overall_quality = min(1.0, (success_rate * 0.4 + avg_quality * 0.4 + (1 - anomaly_rate) * 0.2) + coordination_bonus)

        return {
            "success_rate": success_rate,
            "average_quality": avg_quality,
            "anomaly_rate": anomaly_rate,
            "coordination_effectiveness": coordination_bonus,
            "overall_quality": overall_quality
        }

    def _calculate_crew_efficiency_metrics(self, crew_performance: Dict[str, Any]) -> Dict[str, float]:
        """Calculate efficiency metrics for crew performance"""
        avg_response_time = crew_performance.get('avg_response_time', 0)
        total_tasks = crew_performance.get('total_tasks', 0)

        # Crews are more efficient due to parallel processing
        crew_efficiency_bonus = 0.15  # 15% efficiency boost from crew coordination

        # Throughput calculation
        time_period_hours = 24  # Assuming daily calculation
        throughput = total_tasks / time_period_hours if time_period_hours > 0 else 0

        # Efficiency score with crew coordination bonus
        response_time_score = max(0, 1 - (avg_response_time / 300))  # Lower time = higher score
        throughput_score = min(1.0, throughput / 100)  # Higher throughput = higher score

        overall_efficiency = min(1.0, (response_time_score + throughput_score) / 2 + crew_efficiency_bonus)

        return {
            "average_response_time": avg_response_time,
            "throughput_tasks_per_hour": throughput,
            "response_time_score": response_time_score,
            "throughput_score": throughput_score,
            "crew_coordination_bonus": crew_efficiency_bonus,
            "overall_efficiency": overall_efficiency
        }

    async def _calculate_crew_business_impact(self, crew_type: str, crew_performance: Dict[str, Any]) -> Dict[str, float]:
        """Calculate business impact for crew type"""
        success_rate = crew_performance.get('success_rate', 0)
        total_tasks = crew_performance.get('total_tasks', 0)

        # Business impact varies by crew type
        impact_multipliers = {
            "cold_outreach": {"conversion_impact": 0.8, "retention_impact": 0.1, "expansion_impact": 0.1},
            "lead_revival": {"conversion_impact": 0.6, "retention_impact": 0.3, "expansion_impact": 0.1},
            "objection_handling": {"conversion_impact": 0.7, "retention_impact": 0.2, "expansion_impact": 0.1},
            "conversion_optimization": {"conversion_impact": 0.9, "retention_impact": 0.05, "expansion_impact": 0.05},
            "retention_management": {"conversion_impact": 0.3, "retention_impact": 0.5, "expansion_impact": 0.2}
        }

        multipliers = impact_multipliers.get(crew_type, {"conversion_impact": 0.5, "retention_impact": 0.3, "expansion_impact": 0.2})

        # Calculate impact scores
        conversion_impact = success_rate * multipliers["conversion_impact"] * total_tasks
        retention_impact = success_rate * multipliers["retention_impact"] * total_tasks
        expansion_impact = success_rate * multipliers["expansion_impact"] * total_tasks

        overall_impact = (conversion_impact + retention_impact + expansion_impact) / total_tasks if total_tasks > 0 else 0

        return {
            "conversion_impact": conversion_impact,
            "retention_impact": retention_impact,
            "expansion_impact": expansion_impact,
            "overall_impact": overall_impact
        }

    def _identify_crew_contributions(self, crew_type: str, crew_performance: Dict[str, Any], revenue_attribution: Dict[str, float]) -> List[str]:
        """Identify key contributions of the crew"""
        contributions = []
        success_rate = crew_performance.get('success_rate', 0)
        total_tasks = crew_performance.get('total_tasks', 0)
        total_revenue = revenue_attribution.get('total_attributed', 0)

        if success_rate > 0.85:
            contributions.append(f"Exceptional {success_rate:.1%} success rate across {total_tasks} coordinated tasks")

        if total_revenue > 5000:
            contributions.append(f"Generated ${total_revenue:,.0f} in attributed revenue through crew orchestration")

        # Crew-type specific contributions
        crew_contributions = {
            "cold_outreach": ["Efficient multi-channel lead generation", "Coordinated campaign execution"],
            "lead_revival": ["Personalized reactivation sequences", "Strategic dormant lead targeting"],
            "objection_handling": ["Intelligent objection resolution", "Contextual response generation"],
            "conversion_optimization": ["Data-driven conversion improvements", "A/B testing optimization"],
            "retention_management": ["Proactive churn prevention", "Customer lifetime value optimization"]
        }

        contributions.extend(crew_contributions.get(crew_type, ["Effective crew coordination", "Multi-agent collaboration"]))

        return contributions[:5]

    def _identify_crew_improvements(self, crew_performance: Dict[str, Any], quality_metrics: Dict[str, float]) -> List[str]:
        """Identify improvement opportunities for crew"""
        opportunities = []
        success_rate = crew_performance.get('success_rate', 0)
        avg_response_time = crew_performance.get('avg_response_time', 0)
        anomaly_rate = crew_performance.get('anomaly_rate', 0)

        if success_rate < 0.80:
            opportunities.append("Improve crew success rate through better agent coordination")

        if avg_response_time > 120:
            opportunities.append("Optimize crew response time through parallel processing improvements")

        if anomaly_rate > 0.05:
            opportunities.append("Reduce crew anomaly rate through better error handling")

        if quality_metrics.get('overall_quality', 0) < 0.85:
            opportunities.append("Enhance crew output quality through better agent specialization")

        opportunities.append("Consider crew composition optimization for specific use cases")

        return opportunities[:5]