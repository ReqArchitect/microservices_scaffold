import time
from functools import wraps
from typing import Callable, Any, Optional
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker implementation for handling service failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            name: Name of the circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failures = 0
        self.last_failure_time = 0
        self.is_open = False

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to wrap functions with circuit breaker.
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not current_app.config.get('CIRCUIT_BREAKER_ENABLED', True):
                return func(*args, **kwargs)

            if self.is_open:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(f"Circuit breaker {self.name} attempting recovery")
                    self.is_open = False
                    self.failures = 0
                else:
                    logger.warning(f"Circuit breaker {self.name} is open")
                    raise Exception(f"Circuit breaker {self.name} is open")

            try:
                result = func(*args, **kwargs)
                self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= self.failure_threshold:
                    self.is_open = True
                    logger.error(f"Circuit breaker {self.name} opened after {self.failures} failures")
                
                raise

        return wrapper

def circuit_breaker(
    failure_threshold: Optional[int] = None,
    recovery_timeout: Optional[int] = None,
    name: Optional[str] = None
) -> Callable:
    """
    Decorator factory for circuit breaker.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time in seconds before attempting recovery
        name: Name of the circuit breaker
        
    Returns:
        Circuit breaker decorator
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold or current_app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
            recovery_timeout=recovery_timeout or current_app.config.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60),
            name=name or func.__name__
        )
        return breaker(func)
    return decorator 