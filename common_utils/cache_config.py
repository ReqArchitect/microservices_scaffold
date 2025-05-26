"""
Cache configuration settings for ReqArchitect microservices.
"""
from typing import Dict, Any
import os

def get_cache_config(service_name: str) -> Dict[str, Any]:
    """
    Get cache configuration for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Dictionary containing cache configuration
    """
    return {
        'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'redis'),
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300)),
        'CACHE_KEY_PREFIX': f"{service_name}_",
        'CACHE_OPTIONS': {
            'socket_timeout': int(os.environ.get('REDIS_SOCKET_TIMEOUT', 5)),
            'socket_connect_timeout': int(os.environ.get('REDIS_SOCKET_TIMEOUT', 5)),
            'retry_on_timeout': True,
            'max_connections': int(os.environ.get('REDIS_MAX_CONNECTIONS', 10))
        },
        # Cache durations for different types of data
        'CACHE_DURATIONS': {
            'static': 86400,  # 24 hours for static data
            'user': 300,      # 5 minutes for user data
            'config': 3600,   # 1 hour for configuration
            'metrics': 60     # 1 minute for metrics
        },
        # Circuit breaker settings for cache
        'CIRCUIT_BREAKER': {
            'failure_threshold': int(os.environ.get('CACHE_CIRCUIT_BREAKER_THRESHOLD', 5)),
            'recovery_timeout': int(os.environ.get('CACHE_CIRCUIT_BREAKER_TIMEOUT', 30)),
            'reset_timeout': int(os.environ.get('CACHE_CIRCUIT_BREAKER_RESET', 300))
        },
        # Cache pattern invalidation settings
        'INVALIDATION_PATTERNS': {
            'user': 'user_*',
            'config': 'config_*',
            'metrics': 'metrics_*'
        }
    }
