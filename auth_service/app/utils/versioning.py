from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime
import logging
from typing import Callable, Any, Optional, Dict, List

logger = logging.getLogger(__name__)

class APIVersion:
    """API version management."""
    
    def __init__(
        self,
        version: str,
        deprecated: bool = False,
        sunset_date: Optional[datetime] = None,
        migration_guide: Optional[str] = None
    ):
        """
        Initialize API version.
        
        Args:
            version: Version string (e.g., 'v1')
            deprecated: Whether version is deprecated
            sunset_date: Date when version will be removed
            migration_guide: URL to migration guide
        """
        self.version = version
        self.deprecated = deprecated
        self.sunset_date = sunset_date
        self.migration_guide = migration_guide

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to handle API versioning.
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if version is deprecated
            if self.deprecated:
                logger.warning(f"Deprecated API version {self.version} accessed")
                response = jsonify({
                    "warning": f"API version {self.version} is deprecated",
                    "migration_guide": self.migration_guide
                })
                if self.sunset_date:
                    response.headers['Sunset'] = self.sunset_date.isoformat()
                return response

            # Check if version is sunset
            if self.sunset_date and datetime.utcnow() >= self.sunset_date:
                logger.error(f"Sunset API version {self.version} accessed")
                return jsonify({
                    "error": f"API version {self.version} is no longer available",
                    "migration_guide": self.migration_guide
                }), 410

            return func(*args, **kwargs)
        return wrapper

def api_version(
    version: str,
    deprecated: bool = False,
    sunset_date: Optional[datetime] = None,
    migration_guide: Optional[str] = None
) -> Callable:
    """
    Decorator factory for API versioning.
    
    Args:
        version: Version string (e.g., 'v1')
        deprecated: Whether version is deprecated
        sunset_date: Date when version will be removed
        migration_guide: URL to migration guide
        
    Returns:
        API version decorator
    """
    def decorator(func: Callable) -> Callable:
        version_obj = APIVersion(
            version=version,
            deprecated=deprecated,
            sunset_date=sunset_date,
            migration_guide=migration_guide
        )
        return version_obj(func)
    return decorator

class VersionManager:
    """Manage API versions and their lifecycle."""
    
    def __init__(self):
        """Initialize version manager."""
        self.versions: Dict[str, APIVersion] = {}
        self.current_version: Optional[str] = None

    def register_version(
        self,
        version: str,
        deprecated: bool = False,
        sunset_date: Optional[datetime] = None,
        migration_guide: Optional[str] = None
    ) -> None:
        """
        Register a new API version.
        
        Args:
            version: Version string (e.g., 'v1')
            deprecated: Whether version is deprecated
            sunset_date: Date when version will be removed
            migration_guide: URL to migration guide
        """
        self.versions[version] = APIVersion(
            version=version,
            deprecated=deprecated,
            sunset_date=sunset_date,
            migration_guide=migration_guide
        )

    def set_current_version(self, version: str) -> None:
        """
        Set the current API version.
        
        Args:
            version: Version string
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not registered")
        self.current_version = version

    def get_version_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered versions.
        
        Returns:
            List of version information dictionaries
        """
        return [{
            'version': v.version,
            'deprecated': v.deprecated,
            'sunset_date': v.sunset_date.isoformat() if v.sunset_date else None,
            'migration_guide': v.migration_guide,
            'current': v.version == self.current_version
        } for v in self.versions.values()]

# Create global version manager instance
version_manager = VersionManager() 