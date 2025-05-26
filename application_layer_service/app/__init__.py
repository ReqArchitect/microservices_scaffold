from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event

# Initialize extensions
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name="development"):
    app = Flask(__name__)
    jwt = init_jwt(app)
    oauth = init_oauth(app)
    metrics = init_metrics(app)
    register_error_handlers(app)
    if config_name:
        app.config.from_object(config_name)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Initialize enhanced architecture components
    metrics.init_app(app)
    service_registry.init_app(app)
    tracer.init_app(app)
    versioned_api.init_app(app)

    # Import routes with versioning
    from .routes_versioned import create_api_blueprint
    
    # Create and register versioned blueprint
    api_version = app.config.get('API_VERSION')
    api_bp = create_api_blueprint(api_version)
    versioned_api.register_version(api_version, api_bp)
    CORS(app)

    from .routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Optionally add Swagger docs
    # from .swagger import bp as swagger_bp
    # app.register_blueprint(swagger_bp)

    return app
