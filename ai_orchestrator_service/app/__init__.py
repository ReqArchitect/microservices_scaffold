"""
Main application factory for the AI Orchestrator Service
"""
import os
import logging
from common_utils.base_service import BaseService
from config import config
from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event
from .routes import bp as ai_orchestrator_bp

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
        service_name='ai_orchestrator_service',
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
    
    app.register_blueprint(ai_orchestrator_bp, url_prefix='/api/ai_orchestrator')
    
    # Return the application
    return app

# Create and configure the DB at import time 
from config import config as config_dict
config_name = os.environ.get('FLASK_ENV', 'development')
service = BaseService(
    service_name='ai_orchestrator_service',
    config_module=config_dict[config_name],
    enable_auth=True,
    enable_tracing=False,  # Disable tracing during import
    enable_service_registry=False,  # Disable service registry during import
    enable_outbox=False,  # Disable outbox during import
    enable_metrics=False  # Disable metrics during import
)

# Export DB for use in models
db = service.db
