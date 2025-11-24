"""
Real-Time Monitoring & Alerting

Tracks agent performance, health, and alerts on issues.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AgentMetric:
    """Metric for agent execution."""
    agent_name: str
    execution_time: float
    success: bool
    error: Optional[str]
    timestamp: datetime
    input_size: Optional[int] = None
    output_size: Optional[int] = None


@dataclass
class Alert:
    """Alert structure."""
    level: AlertLevel
    agent_name: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class AgentMonitor:
    """
    Real-time monitoring for agents.
    
    Tracks:
    - Execution metrics
    - Success/failure rates
    - Performance trends
    - Anomaly detection
    """
    
    def __init__(self):
        self.metrics: List[AgentMetric] = []
        self.alerts: List[Alert] = []
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.max_metrics = 10000  # Keep last 10k metrics
        self.max_alerts = 1000  # Keep last 1k alerts
    
    def record_metric(self, metric: AgentMetric):
        """Record an agent execution metric."""
        self.metrics.append(metric)
        
        # Trim if too many
        if len(self.metrics) > self.max_metrics:
            self.metrics.pop(0)
        
        # Update agent stats
        agent_name = metric.agent_name
        if agent_name not in self.agent_stats:
            self.agent_stats[agent_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "success_rate": 0.0
            }
        
        stats = self.agent_stats[agent_name]
        stats["total_executions"] += 1
        stats["total_time"] += metric.execution_time
        
        if metric.success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
            # Alert on failures
            if stats["failed_executions"] % 5 == 0:  # Alert every 5 failures
                self.alert(
                    AlertLevel.WARNING,
                    agent_name,
                    f"Agent has {stats['failed_executions']} failures",
                    {"total_executions": stats["total_executions"]}
                )
        
        # Update averages
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
        
        # Check for anomalies
        self._check_anomalies(metric)
    
    def _check_anomalies(self, metric: AgentMetric):
        """Check for performance anomalies."""
        agent_name = metric.agent_name
        stats = self.agent_stats.get(agent_name, {})
        
        if not stats:
            return
        
        avg_time = stats.get("avg_time", 0)
        
        # Alert if execution time is 3x average
        if avg_time > 0 and metric.execution_time > avg_time * 3:
            self.alert(
                AlertLevel.WARNING,
                agent_name,
                f"Execution time anomaly: {metric.execution_time:.2f}s (avg: {avg_time:.2f}s)",
                {"execution_time": metric.execution_time, "avg_time": avg_time}
            )
        
        # Alert if success rate drops below 80%
        success_rate = stats.get("success_rate", 1.0)
        if stats.get("total_executions", 0) > 10 and success_rate < 0.8:
            self.alert(
                AlertLevel.ERROR,
                agent_name,
                f"Low success rate: {success_rate:.1%}",
                {"success_rate": success_rate, "total_executions": stats["total_executions"]}
            )
    
    def alert(self, level: AlertLevel, agent_name: str, message: str, metadata: Dict[str, Any] = None):
        """Create an alert."""
        alert = Alert(
            level=level,
            agent_name=agent_name,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Trim if too many
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
        
        # Log based on level
        log_level = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical
        }.get(level, logger.info)
        
        log_level(f"[{agent_name}] {message}")
        
        # In production, would send to PagerDuty, Slack, etc.
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            # Send critical alerts immediately
            self._send_alert(alert)
    
    def _send_alert(self, alert: Alert):
        """Send alert to external systems (PagerDuty, Slack, etc.)."""
        # Placeholder - would integrate with alerting services
        logger.critical(f"CRITICAL ALERT: {alert.message}")
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get statistics for a specific agent."""
        return self.agent_stats.get(agent_name, {})
    
    def get_recent_alerts(
        self,
        level: Optional[AlertLevel] = None,
        agent_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Alert]:
        """Get recent alerts with optional filters."""
        alerts = self.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if agent_name:
            alerts = [a for a in alerts if a.agent_name == agent_name]
        
        return alerts[-limit:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        total_agents = len(self.agent_stats)
        healthy_agents = sum(
            1 for stats in self.agent_stats.values()
            if stats.get("success_rate", 1.0) >= 0.9
        )
        
        recent_critical_alerts = len([
            a for a in self.alerts[-100:]
            if a.level == AlertLevel.CRITICAL
            and (datetime.utcnow() - a.timestamp).total_seconds() < 3600
        ])
        
        return {
            "status": "healthy" if recent_critical_alerts == 0 else "degraded",
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "recent_critical_alerts": recent_critical_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(
        self,
        agent_name: Optional[str] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance metrics for agents."""
        cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_metrics = [
            m for m in self.metrics
            if m.timestamp >= cutoff
            and (agent_name is None or m.agent_name == agent_name)
        ]
        
        if not recent_metrics:
            return {"error": "No metrics found"}
        
        total = len(recent_metrics)
        successful = sum(1 for m in recent_metrics if m.success)
        avg_time = sum(m.execution_time for m in recent_metrics) / total
        
        return {
            "agent_name": agent_name or "all",
            "time_window_hours": time_window_hours,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total,
            "avg_execution_time": avg_time,
            "min_execution_time": min(m.execution_time for m in recent_metrics),
            "max_execution_time": max(m.execution_time for m in recent_metrics)
        }


# Global instance
_monitor: Optional[AgentMonitor] = None


def get_monitor() -> AgentMonitor:
    """Get or create global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = AgentMonitor()
    return _monitor









