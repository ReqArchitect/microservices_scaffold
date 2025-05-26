from common_utils.base_service import BaseService
from .models import db, Node, Device, SystemSoftware, TechnologyService, TechnologyInterface, TechnologyFunction, TechnologyProcess, TechnologyInteraction, TechnologyCollaboration, Artifact, Equipment, Material, Facility, CommunicationPath, DistributionNetwork
from .routes import bp as technology_bp
from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/technology_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = 'technology_layer_service'
    SERVICE_PORT = 5100
    # Add other config as needed

def create_app(config_name="development"):
    app = Flask(__name__)
    jwt = init_jwt(app)
    oauth = init_oauth(app)
    metrics = init_metrics(app)
    register_error_handlers(app)
    service = BaseService(
        service_name='technology_layer_service',
        config_module=Config,
        enable_auth=True,
        enable_tracing=True,
        enable_service_registry=True,
        enable_outbox=True,
        enable_metrics=True
    )
    db.init_app(app)
    # Register blueprints
    app.register_blueprint(technology_bp)
    # Register error handlers
    service.register_error_handlers()
    # Register metrics, tracing, etc. (handled by BaseService)
    return app 