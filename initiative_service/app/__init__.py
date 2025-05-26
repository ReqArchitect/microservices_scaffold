# app/__init__.py
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_caching import Cache
from prometheus_client import Counter, Histogram, Gauge
from flasgger import Swagger
import logging
from logging.handlers import RotatingFileHandler
import os
import time
from datetime import datetime, timedelta
from .config import DevelopmentConfig, TestingConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics

from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()



# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
cors = CORS()
swagger = Swagger()
metrics = PrometheusMetrics(app=None)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

INITIATIVE_ACTIONS = Counter(
    'initiative_actions_total',
    'Total initiative actions',
    ['action_type', 'tenant_id']
)

ACTIVE_INITIATIVES = Gauge(
    'active_initiatives_total',
    'Total number of active initiatives',
    ['tenant_id']
)

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Configure logging
    logging.basicConfig(level=app.config['LOG_LEVEL'])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

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
    limiter.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    swagger.init_app(app)
    
    if app.config['PROMETHEUS_METRICS_ENABLED']:
        metrics.init_app(app)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/initiative_service.log',
                                         maxBytes=10240,
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Initiative service startup')
    
    # Register blueprints
    from app.routes import initiative_blueprint
    app.register_blueprint(initiative_blueprint, url_prefix='/api/initiatives')
    
    # Request monitoring middleware
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint
            ).observe(time.time() - request.start_time)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint,
            status=response.status_code
        ).inc()
        
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url}')
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f'Unhandled Exception: {str(e)}')
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })

    return app
