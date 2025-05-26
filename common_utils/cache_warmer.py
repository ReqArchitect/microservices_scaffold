"""
Cache warming and invalidation strategies for ReqArchitect microservices.
"""
from typing import Any, Dict, List, Optional, Set
import logging
from datetime import datetime
from threading import Lock
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class CacheWarmer:
    """Handles cache warming and invalidation strategies."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.warming_lock = Lock()
        self.warming_in_progress: Set[str] = set()
    
    def warm_cache(self, data_loader: callable, key_prefix: str,
                  chunk_size: int = 100) -> bool:
        """
        Warm cache with data in chunks.
        
        Args:
            data_loader: Function that loads data to be cached
            key_prefix: Prefix for cache keys
            chunk_size: Size of chunks to process at once
            
        Returns:
            bool: True if warming was successful
        """
        if key_prefix in self.warming_in_progress:
            logger.warning(f"Cache warming already in progress for {key_prefix}")
            return False
        
        try:
            with self.warming_lock:
                self.warming_in_progress.add(key_prefix)
            
            offset = 0
            while True:
                items = data_loader(offset, chunk_size)
                if not items:
                    break
                
                mapping = {
                    f"{key_prefix}:{item['id']}": item
                    for item in items
                }
                self.cache.cache_set_multi(mapping)
                
                offset += chunk_size
                
            return True
            
        except Exception as e:
            logger.error(f"Error warming cache for {key_prefix}: {str(e)}")
            return False
            
        finally:
            with self.warming_lock:
                self.warming_in_progress.remove(key_prefix)
    
    def invalidate_by_pattern(self, pattern: str,
                            invalidate_dependencies: bool = True) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match cache keys
            invalidate_dependencies: Whether to invalidate dependent caches
            
        Returns:
            Number of invalidated keys
        """
        try:
            count = self.cache.delete_pattern(pattern)
            
            if invalidate_dependencies:
                # Check for known dependencies
                dependency_patterns = self._get_dependency_patterns(pattern)
                for dep_pattern in dependency_patterns:
                    count += self.cache.delete_pattern(dep_pattern)
            
            return count
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {str(e)}")
            return 0
    
    def _get_dependency_patterns(self, pattern: str) -> List[str]:
        """Get patterns for dependent caches."""
        # Map of cache dependencies
        dependencies = {
            'user_*': ['permission_*', 'role_*'],
            'role_*': ['permission_*'],
            'tenant_*': ['user_*', 'role_*'],
            'initiative_*': ['strategy_*', 'metric_*']
        }
        
        for base_pattern, deps in dependencies.items():
            if self._pattern_matches(pattern, base_pattern):
                return deps
        return []
    
    def _pattern_matches(self, key: str, pattern: str) -> bool:
        """Check if a key matches a pattern."""
        if pattern.endswith('*'):
            return key.startswith(pattern[:-1])
        return key == pattern
    
    def preload_static_data(self, static_data_config: Dict[str, Any]) -> None:
        """
        Preload static data into cache.
        
        Args:
            static_data_config: Configuration for static data loading
                {
                    'key_prefix': str,
                    'loader': callable,
                    'chunk_size': int,
                    'ttl': int
                }
        """
        for config in static_data_config:
            try:
                self.warm_cache(
                    data_loader=config['loader'],
                    key_prefix=config['key_prefix'],
                    chunk_size=config.get('chunk_size', 100)
                )
            except Exception as e:
                logger.error(
                    f"Error preloading static data for {config['key_prefix']}: {str(e)}"
                )
    
    def schedule_periodic_refresh(self, refresh_config: List[Dict[str, Any]]) -> None:
        """
        Schedule periodic cache refresh.
        
        Args:
            refresh_config: List of refresh configurations
                [{
                    'pattern': str,
                    'interval': int (seconds),
                    'loader': callable
                }]
        """
        # This would typically be implemented using a task scheduler like Celery
        # For now, we'll just log the configuration
        for config in refresh_config:
            logger.info(
                f"Would schedule refresh for {config['pattern']} "
                f"every {config['interval']} seconds"
            )
