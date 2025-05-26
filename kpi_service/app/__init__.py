# App init

from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event
from .extensions import db
from .routes import kpi_blueprint

from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()

setup_logging()
config = load_config()

engine = get_engine('kpi_service')
Session = get_session(engine)
redis_client = get_redis()

def create_app(config_name="development"):
    app = Flask(__name__)
    jwt = init_jwt(app)
    oauth = init_oauth(app)
    metrics = init_metrics(app)
    register_error_handlers(app)

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
    if config:
        app.config.from_object(config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
    db.init_app(app)
    app.register_blueprint(kpi_blueprint)

    return app
