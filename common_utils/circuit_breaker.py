import time
from functools import wraps
from typing import Callable, Any, Optional, Tuple, Type
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class CircuitBreakerError(Exception):
    """Raised when the circuit breaker is open or operation fails."""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for handling service failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default",
        ignore_exceptions: Tuple[Type[Exception], ...] = (),
    ):
        """
        Initialize circuit breaker.
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            name: Name of the circuit breaker
            ignore_exceptions: Tuple of exception types to ignore
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failures = 0
        self.last_failure_time = None
        self.is_open_flag = False
        self.ignore_exceptions = ignore_exceptions

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
            return self.execute(lambda: func(*args, **kwargs))
        return wrapper

    def execute(self, func: Callable, timeout: Optional[int] = None) -> Any:
        """
        Execute a function with circuit breaker protection.
        Args:
            func: The function to execute.
            timeout: Optional timeout in seconds for the function.
        Returns:
            The result of the function if successful.
        Raises:
            CircuitBreakerError if the circuit is open or operation fails.
        """
        if not current_app.config.get('CIRCUIT_BREAKER_ENABLED', True):
            return func()

        if self.is_open():
            logger.warning(f"Circuit breaker {self.name} is open")
            raise CircuitBreakerError(f"Circuit breaker {self.name} is open")

        try:
            if timeout is not None:
                import threading
                result = [None]
                exc = [None]
                def target():
                    try:
                        result[0] = func()
                    except Exception as e:
                        exc[0] = e
                thread = threading.Thread(target=target)
                thread.start()
                thread.join(timeout)
                if thread.is_alive():
                    self._record_failure()
                    raise CircuitBreakerError("Operation timed out")
                if exc[0]:
                    raise exc[0]
                self._reset_failures()
                return result[0]
            else:
                res = func()
                self._reset_failures()
                return res
        except self.ignore_exceptions as e:
            raise
        except Exception as e:
            self._record_failure()
            if self.failures >= self.failure_threshold:
                self.is_open_flag = True
                logger.error(f"Circuit breaker {self.name} opened after {self.failures} failures")
            raise CircuitBreakerError(str(e)) from e

    def _record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

    def _reset_failures(self):
        self.failures = 0
        self.is_open_flag = False
        self.last_failure_time = None

    def is_open(self) -> bool:
        if self.is_open_flag:
            if self.last_failure_time and (time.time() - self.last_failure_time >= self.recovery_timeout):
                # Move to half-open state
                self.is_open_flag = False
                self.failures = 0
                return False
            return True
        return False

    def is_closed(self) -> bool:
        return not self.is_open_flag

    def is_half_open(self) -> bool:
        if self.is_open_flag and self.last_failure_time:
            return (time.time() - self.last_failure_time >= self.recovery_timeout)
        return False

    def reset(self):
        self._reset_failures()

    @property
    def failure_count(self) -> int:
        return self.failures

    @property
    def last_failure_time_value(self):
        return self.last_failure_time

def circuit_breaker(
    failure_threshold: Optional[int] = None,
    recovery_timeout: Optional[int] = None,
    name: Optional[str] = None,
    ignore_exceptions: Tuple[Type[Exception], ...] = (),
) -> Callable:
    """
    Decorator factory for circuit breaker.
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time in seconds before attempting recovery
        name: Name of the circuit breaker
        ignore_exceptions: Tuple of exception types to ignore
    Returns:
        Circuit breaker decorator
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold or current_app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
            recovery_timeout=recovery_timeout or current_app.config.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60),
            name=name or func.__name__,
            ignore_exceptions=ignore_exceptions,
        )
        return breaker(func)
    return decorator 