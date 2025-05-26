from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
import logging
from prometheus_flask_exporter import PrometheusMetrics

# Import enhanced architecture components
from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI

logger = setup_logging()
config = load_config()
engine = get_engine('strategy_service')
Session = get_session(engine)
redis_client = get_redis()

app = Flask(__name__)
jwt = init_jwt(app)
oauth = init_oauth(app)
metrics = init_metrics(app)
register_error_handlers(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()


def create_app(config_object=None):
    app = Flask(__name__)
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    logger.info(f"Starting Strategy Service with API version {app.config.get('API_VERSION')}")

    # Initialize core extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    metrics.init_app(app)
    
    # Initialize enhanced architecture components
    service_registry.init_app(app)
    tracer.init_app(app)
    versioned_api.init_app(app)    # Register health check endpoint
    @app.route('/health')
    @metrics.do_not_track()
    def health_check():
        return {'status': 'healthy', 'service': app.config.get('SERVICE_NAME')}, 200

    # Import routes and register blueprints with versioning
    from .routes_versioned import create_api_blueprint
    
    # Create and register versioned blueprint
    api_version = app.config.get('API_VERSION')
    api_bp = create_api_blueprint(api_version)
    versioned_api.register_version(api_version, api_bp)
    
    # Add swagger documentation
    from .swagger import bp as swagger_bp
    app.register_blueprint(swagger_bp)

    return app
