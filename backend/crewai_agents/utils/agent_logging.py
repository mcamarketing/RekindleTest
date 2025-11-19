"""
Agent Execution Logging Utility

Automatically logs all agent executions to the database for observability.
Now includes monitoring integration.
"""

from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional
import json
import time
import logging

logger = logging.getLogger(__name__)

# Import monitoring (circular import handled)
try:
    from .monitoring import get_monitor, AgentMetric
except ImportError:
    # Fallback if monitoring not available
    get_monitor = None
    AgentMetric = None


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize data for logging (remove sensitive information)."""
    sanitized = {}
    sensitive_keys = ["password", "token", "api_key", "secret", "key"]
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        elif isinstance(value, str) and len(value) > 500:
            sanitized[key] = value[:500] + "..."
        else:
            sanitized[key] = value
    
    return sanitized


def log_agent_execution(agent_name: Optional[str] = None):
    """
    Decorator to automatically log agent executions.
    
    Now includes:
    - Monitoring integration
    - Performance metrics
    - Error tracking
    
    Usage:
        @log_agent_execution(agent_name="ResearcherAgent")
        def my_agent_function(self, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = None
            start_time = time.time()
            start_datetime = datetime.utcnow()
            error = None
            result = None
            
            # Sanitize inputs for logging
            sanitized_kwargs = sanitize_for_logging(kwargs)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log execution (would integrate with database)
                execution_log = {
                    "agent_name": agent_name or func.__name__,
                    "function_name": func.__name__,
                    "start_time": start_datetime.isoformat(),
                    "duration_seconds": execution_time,
                    "success": True,
                    "error": None,
                    "result_summary": str(result)[:500] if result else None
                }
                logger.info(f"[AGENT_LOG] {json.dumps(execution_log)}")
                
                # Record metric for monitoring
                if get_monitor and AgentMetric:
                    monitor = get_monitor()
                    metric = AgentMetric(
                        agent_name=agent_name or func.__name__,
                        execution_time=execution_time,
                        success=True,
                        error=None,
                        timestamp=start_datetime,
                        input_size=len(str(sanitized_kwargs)),
                        output_size=len(str(result)) if result else None
                    )
                    monitor.record_metric(metric)
                
                return result
            except Exception as e:
                error = str(e)
                execution_time = time.time() - start_time
                
                # Log error
                execution_log = {
                    "agent_name": agent_name or func.__name__,
                    "function_name": func.__name__,
                    "start_time": start_datetime.isoformat(),
                    "duration_seconds": execution_time,
                    "success": False,
                    "error": error,
                    "result_summary": None
                }
                logger.error(f"[AGENT_LOG] {json.dumps(execution_log)}", exc_info=True)
                
                # Record metric for monitoring
                if get_monitor and AgentMetric:
                    monitor = get_monitor()
                    metric = AgentMetric(
                        agent_name=agent_name or func.__name__,
                        execution_time=execution_time,
                        success=False,
                        error=error,
                        timestamp=start_datetime,
                        input_size=len(str(sanitized_kwargs))
                    )
                    monitor.record_metric(metric)
                
                raise
        
        return wrapper
    return decorator


def log_agent_metric(agent_name: str, metric_name: str, value: float, metadata: Optional[Dict] = None):
    """Log a metric for an agent."""
    metric = {
        "agent_name": agent_name,
        "metric_name": metric_name,
        "value": value,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    logger.info(f"[AGENT_METRIC] {json.dumps(metric)}")
