"""
Main application factory for the template service
"""
import os
import logging
from common_utils.base_service import BaseService
from config import config

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """
    Create and configure the Flask application
    
    Args:
        config_name: Configuration to use (development, testing, production)
        
    Returns:
        Configured Flask application
    """
    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    # Create base service
    service = BaseService(
        service_name='template_service',
        config_module=config[config_name],
        enable_auth=True,
        enable_tracing=True,
        enable_service_registry=True,
        enable_outbox=True,
        enable_metrics=True
    )
    
    # Get Flask app
    app = service.app
    db = service.db
    
    # Register error handlers
    service.register_error_handlers()
    
    # Register tenant middleware
    service.register_tenant_middleware()
    
    # Import and register blueprints
    from app.routes_versioned import v1_blueprint
    
    service.register_versioned_blueprints({
        'v1': v1_blueprint
    })
    
    # Return the application
    return app

# Create and configure the DB at import time 
from config import config as config_dict
config_name = os.environ.get('FLASK_ENV', 'development')
service = BaseService(
    service_name='template_service',
    config_module=config_dict[config_name],
    enable_auth=True,
    enable_tracing=False,  # Disable tracing during import
    enable_service_registry=False,  # Disable service registry during import
    enable_outbox=False,  # Disable outbox during import
    enable_metrics=False  # Disable metrics during import
)

# Export DB for use in models
db = service.db
