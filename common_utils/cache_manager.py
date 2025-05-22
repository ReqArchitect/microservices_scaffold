"""
Centralized caching utilities for ReqArchitect microservices.
"""
from functools import wraps
from typing import Any, Optional, Dict, List, Union
from flask import Flask
from flask_caching import Cache
import json
from datetime import datetime

class CacheManager:
    """Centralized cache management for ReqArchitect microservices."""
    
    def __init__(self, app: Flask = None):
        self.cache = Cache()
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize cache with Flask app."""
        config = {
            'CACHE_TYPE': app.config.get('CACHE_TYPE', 'redis'),
            'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'CACHE_KEY_PREFIX': app.config.get('CACHE_KEY_PREFIX', f'{app.name}_'),
            'CACHE_OPTIONS': {
                'socket_timeout': app.config.get('REDIS_SOCKET_TIMEOUT', 5),
                'socket_connect_timeout': app.config.get('REDIS_SOCKET_TIMEOUT', 5),
                'retry_on_timeout': True,
                'max_connections': app.config.get('REDIS_MAX_CONNECTIONS', 10)
            }
        }
        self.cache.init_app(app, config=config)
    
    def cached(self, key: str = None, timeout: int = None, unless: bool = False,
              force_update: bool = False, version: Optional[int] = None):
        """
        Cache decorator that caches the return value of functions.
        
        Args:
            key: Cache key. If None, uses function name and arguments
            timeout: Cache timeout in seconds
            unless: Skip caching when True
            force_update: Force update cache even if key exists
            version: Cache version for versioning support
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if callable(unless) and unless() or unless:
                    return f(*args, **kwargs)
                
                cache_key = key
                if cache_key is None:
                    # Generate key from function name and arguments
                    cache_key = f"{f.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
                    if version is not None:
                        cache_key = f"{cache_key}:v{version}"
                
                if not force_update:
                    rv = self.cache.get(cache_key)
                    if rv is not None:
                        return rv
                
                rv = f(*args, **kwargs)
                self.cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator
    
    def memoize(self, timeout: int = None, version: Optional[int] = None):
        """
        Memoization decorator for caching function return values.
        Takes function arguments into account.
        """
        def memoize_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                cache_key = f"memo:{f.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
                if version is not None:
                    cache_key = f"{cache_key}:v{version}"
                
                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, timeout=timeout)
                return rv
            return wrapper
        return memoize_decorator
    
    def cache_multi(self, keys: List[str], timeout: int = None) -> Dict[str, Any]:
        """Get multiple cache keys at once."""
        return self.cache.get_many(*keys)
    
    def cache_set_multi(self, mapping: Dict[str, Any], timeout: int = None) -> bool:
        """Set multiple cache keys at once."""
        return self.cache.set_many(mapping, timeout=timeout)
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        keys = self.cache.delete_pattern(pattern)
        return len(keys)
    
    def invalidate_version(self, version: int, pattern: str = None):
        """Invalidate all keys of a specific version."""
        if pattern:
            pattern = f"*{pattern}*:v{version}"
        else:
            pattern = f"*:v{version}"
        return self.delete_pattern(pattern)
    
    def get_metric(self, metric_name: str) -> Dict[str, Any]:
        """Get cache metrics."""
        info = self.cache.get_backend_info()
        if metric_name in info:
            return info[metric_name]
        return None
    
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor cache health metrics."""
        metrics = self.cache.get_backend_info()
        return {
            'status': 'healthy' if metrics.get('last_save_time') else 'unhealthy',
            'used_memory': metrics.get('used_memory_human', 'unknown'),
            'hit_ratio': metrics.get('keyspace_hits', 0) / (
                metrics.get('keyspace_hits', 0) + metrics.get('keyspace_misses', 1)
            ),
            'connected_clients': metrics.get('connected_clients', 0),
            'last_save_time': datetime.fromtimestamp(
                metrics.get('last_save_time', 0)
            ).isoformat()
        }
