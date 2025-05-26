"""
Rate limiting implementation for the API Gateway
"""
from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict
import threading

class RateLimiter:
    """
    Token bucket implementation of rate limiting
    """
    def __init__(self):
        self.buckets = defaultdict(lambda: {'tokens': 0, 'last_updated': time.time()})
        self.lock = threading.Lock()
        
    def acquire(self, key, rate=60, capacity=60):
        """
        Try to acquire a token from the bucket
        
        Args:
            key: The key to rate limit on (e.g., IP, tenant ID)
            rate: Tokens per minute
            capacity: Maximum tokens in bucket
            
        Returns:
            bool: Whether the request should be allowed
        """
        with self.lock:
            now = time.time()
            bucket = self.buckets[key]
            
            # Add new tokens based on time passed
            time_passed = now - bucket['last_updated']
            new_tokens = time_passed * (rate / 60.0)  # Convert rate to tokens per second
            bucket['tokens'] = min(bucket['tokens'] + new_tokens, capacity)
            bucket['last_updated'] = now
            
            # Try to consume a token
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                return True
                
            return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(
    rate_per_minute=60,
    bucket_capacity=60,
    key_func=lambda: request.headers.get('X-Tenant-ID', request.remote_addr)
):
    """
    Rate limiting decorator
    
    Args:
        rate_per_minute: Number of requests allowed per minute
        bucket_capacity: Maximum burst size
        key_func: Function to determine the rate limiting key
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = key_func()
            
            if rate_limiter.acquire(key, rate_per_minute, bucket_capacity):
                return f(*args, **kwargs)
            else:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': '60'  # Simplified - should calculate actual wait time
                }), 429
                
        return wrapped
    return decorator
