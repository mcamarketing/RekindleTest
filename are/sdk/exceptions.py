"""
ARE SDK Exceptions

Custom exception classes for ARE SDK error handling, including
agent-specific errors, validation errors, and communication errors.
"""


class AREError(Exception):
    """Base exception for all ARE SDK errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "ARE_ERROR"
        self.details = details or {}
        self.timestamp = None  # Will be set by client

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class AgentUnavailableError(AREError):
    """Raised when an agent is not available or unreachable"""

    def __init__(self, agent_type: str, message: str = None, details: dict = None):
        message = message or f"Agent '{agent_type}' is currently unavailable"
        super().__init__(message, "AGENT_UNAVAILABLE", details)
        self.agent_type = agent_type


class ValidationError(AREError):
    """Raised when input validation fails"""

    def __init__(self, field: str, value: any, message: str = None, details: dict = None):
        message = message or f"Validation failed for field '{field}' with value '{value}'"
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class TimeoutError(AREError):
    """Raised when an operation times out"""

    def __init__(self, operation: str, timeout_seconds: int, message: str = None, details: dict = None):
        message = message or f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class AuthenticationError(AREError):
    """Raised when authentication fails"""

    def __init__(self, message: str = None, details: dict = None):
        message = message or "Authentication failed"
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(AREError):
    """Raised when authorization fails"""

    def __init__(self, resource: str, action: str, message: str = None, details: dict = None):
        message = message or f"Unauthorized access to '{resource}' for action '{action}'"
        super().__init__(message, "AUTHORIZATION_ERROR", details)
        self.resource = resource
        self.action = action


class RateLimitError(AREError):
    """Raised when rate limit is exceeded"""

    def __init__(self, limit: int, reset_in: int, message: str = None, details: dict = None):
        message = message or f"Rate limit exceeded. Limit: {limit}, resets in {reset_in} seconds"
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.limit = limit
        self.reset_in = reset_in


class ConfigurationError(AREError):
    """Raised when there's a configuration issue"""

    def __init__(self, config_key: str, message: str = None, details: dict = None):
        message = message or f"Configuration error for key '{config_key}'"
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key


class NetworkError(AREError):
    """Raised when network communication fails"""

    def __init__(self, url: str, method: str, message: str = None, details: dict = None):
        message = message or f"Network error for {method} {url}"
        super().__init__(message, "NETWORK_ERROR", details)
        self.url = url
        self.method = method


class AgentExecutionError(AREError):
    """Raised when agent execution fails"""

    def __init__(self, agent_type: str, task_id: str, message: str = None, details: dict = None):
        message = message or f"Agent '{agent_type}' failed to execute task '{task_id}'"
        super().__init__(message, "AGENT_EXECUTION_ERROR", details)
        self.agent_type = agent_type
        self.task_id = task_id


class GoalProcessingError(AREError):
    """Raised when goal processing fails"""

    def __init__(self, goal_id: str, message: str = None, details: dict = None):
        message = message or f"Failed to process goal '{goal_id}'"
        super().__init__(message, "GOAL_PROCESSING_ERROR", details)
        self.goal_id = goal_id


class ResourceExhaustionError(AREError):
    """Raised when system resources are exhausted"""

    def __init__(self, resource_type: str, available: int, required: int, message: str = None, details: dict = None):
        message = message or f"Resource '{resource_type}' exhausted. Available: {available}, Required: {required}"
        super().__init__(message, "RESOURCE_EXHAUSTION_ERROR", details)
        self.resource_type = resource_type
        self.available = available
        self.required = required


class StreamingError(AREError):
    """Raised when streaming operations fail"""

    def __init__(self, stream_id: str, message: str = None, details: dict = None):
        message = message or f"Streaming error for stream '{stream_id}'"
        super().__init__(message, "STREAMING_ERROR", details)
        self.stream_id = stream_id


class SchemaValidationError(ValidationError):
    """Raised when data doesn't match expected schema"""

    def __init__(self, schema_name: str, data: any, errors: list, message: str = None, details: dict = None):
        message = message or f"Schema validation failed for '{schema_name}': {', '.join(errors)}"
        super().__init__("data", data, message, details)
        self.schema_name = schema_name
        self.errors = errors


# Error code constants for consistent error handling
ERROR_CODES = {
    "ARE_ERROR": "ARE_ERROR",
    "AGENT_UNAVAILABLE": "AGENT_UNAVAILABLE",
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "TIMEOUT_ERROR": "TIMEOUT_ERROR",
    "AUTHENTICATION_ERROR": "AUTHENTICATION_ERROR",
    "AUTHORIZATION_ERROR": "AUTHORIZATION_ERROR",
    "RATE_LIMIT_ERROR": "RATE_LIMIT_ERROR",
    "CONFIGURATION_ERROR": "CONFIGURATION_ERROR",
    "NETWORK_ERROR": "NETWORK_ERROR",
    "AGENT_EXECUTION_ERROR": "AGENT_EXECUTION_ERROR",
    "GOAL_PROCESSING_ERROR": "GOAL_PROCESSING_ERROR",
    "RESOURCE_EXHAUSTION_ERROR": "RESOURCE_EXHAUSTION_ERROR",
    "STREAMING_ERROR": "STREAMING_ERROR",
}


def get_error_class(error_code: str) -> type:
    """Get the appropriate exception class for an error code"""
    error_class_map = {
        "AGENT_UNAVAILABLE": AgentUnavailableError,
        "VALIDATION_ERROR": ValidationError,
        "TIMEOUT_ERROR": TimeoutError,
        "AUTHENTICATION_ERROR": AuthenticationError,
        "AUTHORIZATION_ERROR": AuthorizationError,
        "RATE_LIMIT_ERROR": RateLimitError,
        "CONFIGURATION_ERROR": ConfigurationError,
        "NETWORK_ERROR": NetworkError,
        "AGENT_EXECUTION_ERROR": AgentExecutionError,
        "GOAL_PROCESSING_ERROR": GoalProcessingError,
        "RESOURCE_EXHAUSTION_ERROR": ResourceExhaustionError,
        "STREAMING_ERROR": StreamingError,
    }

    return error_class_map.get(error_code, AREError)