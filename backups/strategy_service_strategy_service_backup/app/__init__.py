from flask import Flask
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
