# app/__init__.py
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
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
from .auth import ROLES, get_user_permissions

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
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

# JWT configuration
@jwt.user_identity_loader
def user_identity_lookup(user):
    """Convert user object or dict to JWT identity."""
    if isinstance(user, dict):
        return {
            'id': user.get('id'),
            'tenant_id': user.get('tenant_id'),
            'role': user.get('role', 'user')
        }
    return {
        'id': getattr(user, 'id', None),
        'tenant_id': getattr(user, 'tenant_id', None),
        'role': getattr(user, 'role', 'user')
    }

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from JWT data."""
    try:
        identity = jwt_data.get("identity")
        app.logger.debug(f"JWT data: {jwt_data}")
        app.logger.debug(f"Identity from JWT: {identity}")
        
        if not isinstance(identity, dict):
            app.logger.error(f"Invalid identity type: {type(identity)}")
            return None
        
        # Ensure required fields are present
        required_fields = ['id', 'tenant_id', 'role']
        missing_fields = [field for field in required_fields if field not in identity]
        if missing_fields:
            app.logger.error(f"Missing required fields in identity: {missing_fields}")
            return None
        
        # Validate role
        role = identity.get('role')
        if role not in ROLES:
            app.logger.error(f"Invalid role in identity: {role}")
            return None
        
        return identity
    except Exception as e:
        app.logger.error(f"Error in user_lookup_callback: {str(e)}")
        return None

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    """Add role-based permissions to JWT claims."""
    try:
        if not isinstance(identity, dict):
            app.logger.error(f"Invalid identity type in claims loader: {type(identity)}")
            return {}
        
        role = identity.get('role', 'user')
        if role not in ROLES:
            app.logger.error(f"Invalid role in claims loader: {role}")
            return {}
        
        permissions = get_user_permissions(role)
        return {
            'permissions': permissions,
            'fresh': True,
            'type': 'access'
        }
    except Exception as e:
        app.logger.error(f"Error in add_claims_to_access_token: {str(e)}")
        return {}

@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    """Handle missing JWT token."""
    return jsonify({"error": "Missing authorization header"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    """Handle invalid JWT token."""
    return jsonify({"error": "Invalid token"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT token."""
    return jsonify({"error": "Token has expired"}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    """Handle non-fresh token when fresh is required."""
    return jsonify({"error": "Fresh token required"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """Handle revoked token."""
    return jsonify({"error": "Token has been revoked"}), 401

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
    jwt.init_app(app)
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
