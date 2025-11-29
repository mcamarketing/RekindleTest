"""
ARE REX Analytics Agent Wrapper

Provides real-time analytics, performance tracking, and outcome analysis
for the REX (Real-time Execution) system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Represents a performance metric"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Analytics report for a time period"""
    report_id: str
    time_period: str
    metrics: List[Metric]
    aggregations: Dict[str, Any]
    insights: List[str]
    alerts: List[str]
    generated_at: datetime

@dataclass
class PerformanceTracker:
    """Tracks performance metrics over time"""
    metric_name: str
    window_size: int = 100  # Rolling window size
    values: deque = field(default_factory=lambda: deque(maxlen=100))
    timestamps: deque = field(default_factory=lambda: deque(maxlen=100))

    def add_measurement(self, value: float, timestamp: Optional[datetime] = None):
        """Add a new measurement"""
        if timestamp is None:
            timestamp = datetime.now()

        self.values.append(value)
        self.timestamps.append(timestamp)

    def get_average(self) -> Optional[float]:
        """Get average of recent measurements"""
        return statistics.mean(self.values) if self.values else None

    def get_median(self) -> Optional[float]:
        """Get median of recent measurements"""
        return statistics.median(self.values) if self.values else None

    def get_trend(self) -> str:
        """Get trend direction"""
        if len(self.values) < 2:
            return "insufficient_data"

        recent = list(self.values)[-10:]  # Last 10 measurements
        if len(recent) < 2:
            return "insufficient_data"

        # Simple linear trend
        slope = statistics.linear_regression(range(len(recent)), recent)[0]
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

class RexAnalyticsAgent:
    """ARE REX Analytics Agent - Real-time performance analytics"""

    def __init__(self):
        self.metrics_buffer: List[Metric] = []
        self.trackers: Dict[str, PerformanceTracker] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.analytics_history: List[AnalyticsReport] = []

        # Setup default trackers
        self._setup_default_trackers()

        # Setup default alert thresholds
        self._setup_alert_thresholds()

    def _setup_default_trackers(self):
        """Setup default performance trackers"""
        default_metrics = [
            "execution_time",
            "success_rate",
            "error_rate",
            "throughput",
            "latency",
            "cpu_usage",
            "memory_usage",
            "api_calls",
            "user_satisfaction"
        ]

        for metric in default_metrics:
            self.trackers[metric] = PerformanceTracker(metric)

    def _setup_alert_thresholds(self):
        """Setup default alert thresholds"""
        self.alert_thresholds = {
            "execution_time": {"warning": 300, "critical": 600},  # seconds
            "error_rate": {"warning": 0.05, "critical": 0.15},    # percentage
            "latency": {"warning": 2000, "critical": 5000},       # milliseconds
            "cpu_usage": {"warning": 80, "critical": 95},         # percentage
            "memory_usage": {"warning": 85, "critical": 95}       # percentage
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'analyze')

        logger.info(f"REX Analytics Agent executing action: {action}")

        try:
            if action == 'record_metric':
                return await self._record_metric(input_data)
            elif action == 'generate_report':
                return await self._generate_report(input_data)
            elif action == 'check_alerts':
                return await self._check_alerts(input_data)
            elif action == 'get_performance_summary':
                return self._get_performance_summary()
            elif action == 'analyze_trends':
                return await self._analyze_trends(input_data)
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Analytics execution failed: {e}")
            raise

    async def _record_metric(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a performance metric"""
        metric_name = input_data.get('metric_name')
        value = input_data.get('value')
        tags = input_data.get('tags', {})
        metadata = input_data.get('metadata', {})

        if not metric_name or value is None:
            raise ValueError("metric_name and value are required")

        metric = Metric(
            name=metric_name,
            value=float(value),
            timestamp=datetime.now(),
            tags=tags,
            metadata=metadata
        )

        self.metrics_buffer.append(metric)

        # Update tracker
        if metric_name in self.trackers:
            self.trackers[metric_name].add_measurement(value, metric.timestamp)

        # Check for alerts
        alerts = self._check_metric_alerts(metric)

        logger.debug(f"Recorded metric: {metric_name} = {value}")

        return {
            "status": "recorded",
            "metric": metric.__dict__,
            "alerts_triggered": alerts
        }

    async def _generate_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics report"""
        time_period = input_data.get('time_period', 'last_hour')
        include_trends = input_data.get('include_trends', True)

        # Filter metrics by time period
        cutoff_time = self._get_cutoff_time(time_period)
        relevant_metrics = [
            m for m in self.metrics_buffer
            if m.timestamp >= cutoff_time
        ]

        # Generate aggregations
        aggregations = self._calculate_aggregations(relevant_metrics)

        # Generate insights
        insights = await self._generate_insights(relevant_metrics, aggregations)

        # Check for alerts
        alerts = self._generate_alerts(relevant_metrics, aggregations)

        report = AnalyticsReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            time_period=time_period,
            metrics=relevant_metrics,
            aggregations=aggregations,
            insights=insights,
            alerts=alerts,
            generated_at=datetime.now()
        )

        self.analytics_history.append(report)

        logger.info(f"Generated analytics report for {time_period} with {len(relevant_metrics)} metrics")

        return {
            "status": "generated",
            "report": {
                "report_id": report.report_id,
                "time_period": report.time_period,
                "metrics_count": len(report.metrics),
                "insights": report.insights,
                "alerts": report.alerts,
                "aggregations": report.aggregations
            }
        }

    async def _check_alerts(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for active alerts"""
        check_period = input_data.get('check_period', 'last_5_minutes')

        cutoff_time = self._get_cutoff_time(check_period)
        recent_metrics = [
            m for m in self.metrics_buffer
            if m.timestamp >= cutoff_time
        ]

        alerts = []
        for metric in recent_metrics:
            metric_alerts = self._check_metric_alerts(metric)
            alerts.extend(metric_alerts)

        # Remove duplicates
        unique_alerts = []
        seen = set()
        for alert in alerts:
            alert_key = (alert['metric'], alert['level'], alert['condition'])
            if alert_key not in seen:
                unique_alerts.append(alert)
                seen.add(alert_key)

        return {
            "status": "checked",
            "alerts": unique_alerts,
            "alert_count": len(unique_alerts)
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        summary = {
            "trackers": {},
            "overall_health": "healthy",
            "active_alerts": 0
        }

        for name, tracker in self.trackers.items():
            avg = tracker.get_average()
            trend = tracker.get_trend()

            summary["trackers"][name] = {
                "average": avg,
                "trend": trend,
                "sample_count": len(tracker.values)
            }

            # Check for alerts on this tracker
            if avg is not None and name in self.alert_thresholds:
                thresholds = self.alert_thresholds[name]
                if avg >= thresholds.get("critical", float('inf')):
                    summary["active_alerts"] += 1
                    summary["overall_health"] = "critical"
                elif avg >= thresholds.get("warning", float('inf')):
                    summary["active_alerts"] += 1
                    if summary["overall_health"] == "healthy":
                        summary["overall_health"] = "warning"

        return summary

    async def _analyze_trends(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends"""
        metrics_to_analyze = input_data.get('metrics', list(self.trackers.keys()))
        analysis_period = input_data.get('analysis_period', 'last_day')

        trends = {}
        for metric_name in metrics_to_analyze:
            if metric_name in self.trackers:
                tracker = self.trackers[metric_name]
                trend = tracker.get_trend()
                avg = tracker.get_average()

                # Calculate trend strength
                trend_strength = self._calculate_trend_strength(tracker)

                trends[metric_name] = {
                    "trend": trend,
                    "average": avg,
                    "trend_strength": trend_strength,
                    "data_points": len(tracker.values)
                }

        # Generate trend insights
        insights = self._generate_trend_insights(trends)

        return {
            "status": "analyzed",
            "trends": trends,
            "insights": insights
        }

    def _get_cutoff_time(self, time_period: str) -> datetime:
        """Get cutoff time for filtering metrics"""
        now = datetime.now()

        if time_period == 'last_5_minutes':
            return now - timedelta(minutes=5)
        elif time_period == 'last_hour':
            return now - timedelta(hours=1)
        elif time_period == 'last_day':
            return now - timedelta(days=1)
        elif time_period == 'last_week':
            return now - timedelta(weeks=1)
        else:
            return now - timedelta(hours=1)  # Default to last hour

    def _calculate_aggregations(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Calculate aggregations from metrics"""
        if not metrics:
            return {}

        # Group by metric name
        by_name = defaultdict(list)
        for metric in metrics:
            by_name[metric.name].append(metric.value)

        aggregations = {}
        for name, values in by_name.items():
            aggregations[name] = {
                "count": len(values),
                "average": statistics.mean(values) if values else None,
                "median": statistics.median(values) if values else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "std_dev": statistics.stdev(values) if len(values) > 1 else None
            }

        return aggregations

    async def _generate_insights(self, metrics: List[Metric], aggregations: Dict[str, Any]) -> List[str]:
        """Generate insights from metrics and aggregations"""
        insights = []

        # Analyze execution time
        if "execution_time" in aggregations:
            exec_time = aggregations["execution_time"]
            avg_time = exec_time.get("average")
            if avg_time:
                if avg_time < 60:
                    insights.append("Execution times are within acceptable ranges")
                elif avg_time < 300:
                    insights.append("Execution times are elevated but manageable")
                else:
                    insights.append("Execution times are critically high - optimization needed")

        # Analyze error rates
        if "error_rate" in aggregations:
            error_rate = aggregations["error_rate"]
            avg_error = error_rate.get("average")
            if avg_error and avg_error > 0.1:
                insights.append(f"Error rate of {avg_error:.2%} indicates potential stability issues")

        # Analyze throughput
        if "throughput" in aggregations:
            throughput = aggregations["throughput"]
            avg_throughput = throughput.get("average")
            if avg_throughput:
                insights.append(f"Average throughput: {avg_throughput:.1f} operations per minute")

        return insights

    def _generate_alerts(self, metrics: List[Metric], aggregations: Dict[str, Any]) -> List[str]:
        """Generate alerts based on metrics"""
        alerts = []

        for metric_name, agg in aggregations.items():
            if metric_name in self.alert_thresholds:
                thresholds = self.alert_thresholds[metric_name]
                avg_value = agg.get("average")

                if avg_value is not None:
                    if avg_value >= thresholds.get("critical", float('inf')):
                        alerts.append(f"CRITICAL: {metric_name} at {avg_value:.2f} exceeds critical threshold")
                    elif avg_value >= thresholds.get("warning", float('inf')):
                        alerts.append(f"WARNING: {metric_name} at {avg_value:.2f} exceeds warning threshold")

        return alerts

    def _check_metric_alerts(self, metric: Metric) -> List[Dict[str, Any]]:
        """Check if a metric triggers any alerts"""
        alerts = []

        if metric.name in self.alert_thresholds:
            thresholds = self.alert_thresholds[metric.name]

            if metric.value >= thresholds.get("critical", float('inf')):
                alerts.append({
                    "metric": metric.name,
                    "level": "critical",
                    "value": metric.value,
                    "threshold": thresholds["critical"],
                    "condition": f"value >= {thresholds['critical']}",
                    "timestamp": metric.timestamp.isoformat()
                })
            elif metric.value >= thresholds.get("warning", float('inf')):
                alerts.append({
                    "metric": metric.name,
                    "level": "warning",
                    "value": metric.value,
                    "threshold": thresholds["warning"],
                    "condition": f"value >= {thresholds['warning']}",
                    "timestamp": metric.timestamp.isoformat()
                })

        return alerts

    def _calculate_trend_strength(self, tracker: PerformanceTracker) -> float:
        """Calculate trend strength (0-1)"""
        if len(tracker.values) < 2:
            return 0.0

        # Use coefficient of determination from linear regression
        try:
            x = list(range(len(tracker.values)))
            y = list(tracker.values)
            slope, intercept = statistics.linear_regression(x, y)

            # Calculate R-squared
            y_mean = statistics.mean(y)
            ss_tot = sum((yi - y_mean) ** 2 for yi in y)
            ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))

            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            return min(r_squared, 1.0)

        except Exception:
            return 0.0

    def _generate_trend_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []

        for metric_name, trend_data in trends.items():
            trend = trend_data["trend"]
            strength = trend_data["trend_strength"]

            if trend == "increasing" and strength > 0.5:
                insights.append(f"{metric_name} is trending upward with strong correlation")
            elif trend == "decreasing" and strength > 0.5:
                insights.append(f"{metric_name} is trending downward with strong correlation")
            elif trend == "stable":
                insights.append(f"{metric_name} is stable with no significant trend")

        return insights