"""
Error Handling & Retry Logic

Implements retry logic, circuit breakers, and error recovery for all agents.
"""

from typing import Callable, Any, Optional, Dict
from functools import wraps
import time
import logging
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error types for classification."""
    TRANSIENT = "transient"  # Retryable (network, rate limit)
    PERMANENT = "permanent"  # Don't retry (validation, auth)
    UNKNOWN = "unknown"  # Default to retry


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker pattern for external dependencies."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN. Too many failures.")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (datetime.utcnow() - self.last_failure_time).total_seconds() >= self.timeout
    
    def _on_success(self):
        """Reset on successful call."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Increment failure count and open circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures. "
                f"Will retry after {self.timeout} seconds."
            )


def classify_error(error: Exception) -> ErrorType:
    """Classify error as transient or permanent."""
    error_name = type(error).__name__
    error_str = str(error).lower()
    
    # Transient errors (retryable)
    transient_indicators = [
        "timeout", "connection", "network", "rate limit", "429", "503", "502",
        "temporary", "unavailable", "retry", "throttle", "quota"
    ]
    
    if any(indicator in error_str for indicator in transient_indicators):
        return ErrorType.TRANSIENT
    
    # Permanent errors (don't retry)
    permanent_indicators = [
        "validation", "invalid", "not found", "404", "401", "403", "400",
        "unauthorized", "forbidden", "malformed", "syntax"
    ]
    
    if any(indicator in error_str for indicator in permanent_indicators):
        return ErrorType.PERMANENT
    
    return ErrorType.UNKNOWN


def retry(
    max_attempts: int = 3,
    backoff: str = "exponential",
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    circuit_breaker: Optional[CircuitBreaker] = None
):
    """
    Retry decorator with exponential backoff and circuit breaker support.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff: Backoff strategy ("exponential", "linear", "fixed")
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        circuit_breaker: Optional circuit breaker instance
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    # Use circuit breaker if provided
                    if circuit_breaker:
                        return circuit_breaker.call(func, *args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                
                except Exception as e:
                    last_error = e
                    error_type = classify_error(e)
                    
                    # Don't retry permanent errors
                    if error_type == ErrorType.PERMANENT:
                        logger.error(f"Permanent error in {func.__name__}: {e}")
                        raise e
                    
                    # Don't retry on last attempt
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"Max attempts ({max_attempts}) reached for {func.__name__}. "
                            f"Last error: {e}"
                        )
                        raise e
                    
                    # Calculate delay
                    if backoff == "exponential":
                        delay = min(initial_delay * (2 ** attempt), max_delay)
                    elif backoff == "linear":
                        delay = min(initial_delay * (attempt + 1), max_delay)
                    else:  # fixed
                        delay = initial_delay
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_error
        
        return wrapper
    return decorator


def graceful_degradation(fallback_value: Any = None, fallback_func: Optional[Callable] = None):
    """
    Graceful degradation decorator.
    
    If function fails, return fallback value or call fallback function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                return fallback_value
        
        return wrapper
    return decorator









