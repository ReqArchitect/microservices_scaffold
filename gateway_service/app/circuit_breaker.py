"""
Circuit breaker implementation for the API Gateway
"""
from functools import wraps
import time
from collections import defaultdict
import threading
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Circuit breaker implementation with three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service considered down, requests fail fast
    - HALF_OPEN: Testing if service is back up
    """
    # Circuit states
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    HALF_OPEN = 'HALF_OPEN'
    
    def __init__(self):
        self.states = defaultdict(lambda: {
            'state': self.CLOSED,
            'failures': 0,
            'last_failure': 0,
            'last_success': time.time()
        })
        self.lock = threading.Lock()
        
        # Configuration
        self.failure_threshold = 5  # Number of failures before opening
        self.reset_timeout = 60  # Seconds before attempting reset
        self.half_open_max_requests = 3  # Max requests in half-open state
        self.half_open_requests = defaultdict(int)
        
    def record_failure(self, service):
        """Record a service failure"""
        with self.lock:
            state_data = self.states[service]
            state_data['failures'] += 1
            state_data['last_failure'] = time.time()
            
            if (state_data['state'] == self.CLOSED and 
                state_data['failures'] >= self.failure_threshold):
                state_data['state'] = self.OPEN
                logger.warning(f"Circuit breaker opened for service: {service}")
                
    def record_success(self, service):
        """Record a service success"""
        with self.lock:
            state_data = self.states[service]
            state_data['failures'] = 0
            state_data['last_success'] = time.time()
            
            if state_data['state'] in [self.OPEN, self.HALF_OPEN]:
                state_data['state'] = self.CLOSED
                self.half_open_requests[service] = 0
                logger.info(f"Circuit breaker closed for service: {service}")
                
    def should_allow_request(self, service):
        """Determine if a request should be allowed"""
        with self.lock:
            state_data = self.states[service]
            now = time.time()
            
            if state_data['state'] == self.CLOSED:
                return True
                
            if state_data['state'] == self.OPEN:
                # Check if enough time has passed to try again
                if now - state_data['last_failure'] >= self.reset_timeout:
                    state_data['state'] = self.HALF_OPEN
                    self.half_open_requests[service] = 0
                    logger.info(f"Circuit breaker half-open for service: {service}")
                    return True
                return False
                
            if state_data['state'] == self.HALF_OPEN:
                # Allow limited requests in half-open state
                if self.half_open_requests[service] < self.half_open_max_requests:
                    self.half_open_requests[service] += 1
                    return True
                return False
                
            return True

# Global circuit breaker instance
circuit_breaker = CircuitBreaker()

def circuit_breaker(service_name):
    """
    Circuit breaker decorator
    
    Args:
        service_name: Name of the service to protect
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not circuit_breaker.should_allow_request(service_name):
                return jsonify({
                    'error': 'Service temporarily unavailable',
                    'retry_after': str(circuit_breaker.reset_timeout)
                }), 503
                
            try:
                result = f(*args, **kwargs)
                
                # Consider certain status codes as failures
                if isinstance(result, tuple):
                    status_code = result[1]
                else:
                    status_code = 200
                    
                if status_code >= 500:
                    circuit_breaker.record_failure(service_name)
                else:
                    circuit_breaker.record_success(service_name)
                    
                return result
                
            except Exception as e:
                circuit_breaker.record_failure(service_name)
                raise
                
        return wrapped
    return decorator
