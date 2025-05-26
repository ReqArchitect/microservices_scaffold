"""
Base service components for ReqArchitect microservices
"""
import os
import logging
from flask import Flask, Blueprint, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix

# Import common utilities
from common_utils.service_registry import register_service
from common_utils.tracing import init_tracer
from common_utils.logging import configure_logging
from common_utils.outbox import init_outbox_processor, OutboxEvent
from common_utils.auth import get_user_and_tenant
from common_utils.tenant import tenant_required

logger = logging.getLogger(__name__)

class BaseService:
    """
    Base class for ReqArchitect microservices
    
    This class provides common functionality for all services, including:
    - Flask application setup
    - Database configuration
    - Authentication
    - Service registry
    - Distributed tracing
    - API documentation
    - Health check endpoints
    - Metrics
    """
    def __init__(self, service_name, config_module, enable_auth=True, 
                 enable_tracing=True, enable_service_registry=True,
                 enable_outbox=True, enable_metrics=True):
        self.service_name = service_name
        self.config_module = config_module
        self.enable_auth = enable_auth
        self.enable_tracing = enable_tracing
        self.enable_service_registry = enable_service_registry
        self.enable_outbox = enable_outbox
        self.enable_metrics = enable_metrics
        
        # Initialize Flask app
        self.app = Flask(service_name)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
        
        # Load configuration
        self.app.config.from_object(config_module)
        
        # Initialize components
        self.db = SQLAlchemy(self.app)
        self.migrate = Migrate(self.app, self.db)
        CORS(self.app)
        self.swagger = Swagger(self.app)
        
        # Setup authentication if enabled
        if enable_auth:
            self.jwt = JWTManager(self.app)
            
        # Register base routes
        self._register_base_routes()
        
        # Configure logging
        configure_logging(self.app)
        
        # Initialize tracing if enabled
        if enable_tracing:
            self.tracer = init_tracer(self.app, service_name)
            
        # Initialize metrics if enabled
        if enable_metrics:
            try:
                from prometheus_flask_exporter import PrometheusMetrics
                self.metrics = PrometheusMetrics(self.app)
                self.metrics.info(f'{service_name}_info', f'{service_name} metrics', 
                                 version=os.environ.get('VERSION', 'v1'))
            except ImportError:
                logger.warning("prometheus_flask_exporter not installed. Metrics disabled.")
                
        # Initialize outbox processor if enabled
        if enable_outbox:
            init_outbox_processor(self.app, self.db)
    
    def _register_base_routes(self):
        """Register base routes for the service"""
        @self.app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'service': self.service_name,
                'version': os.environ.get('VERSION', 'v1')
            })
            
        @self.app.route('/metrics')
        def metrics():
            if hasattr(self, 'metrics'):
                return self.metrics.generate_latest()
            return jsonify({'error': 'Metrics not enabled'})
            
    def register_blueprints(self, blueprints):
        """
        Register Flask blueprints with the application
        
        Args:
            blueprints: List of (blueprint, url_prefix) tuples
        """
        for blueprint, url_prefix in blueprints:
            self.app.register_blueprint(blueprint, url_prefix=url_prefix)
            
    def register_versioned_blueprints(self, version_blueprints):
        """
        Register versioned API blueprints
        
        Args:
            version_blueprints: Dict of version -> blueprint mappings
        """
        for version, blueprint in version_blueprints.items():
            url_prefix = f'/api/{version}'
            self.app.register_blueprint(blueprint, url_prefix=url_prefix)
            
    def register_error_handlers(self):
        """Register error handlers for the application"""
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
            
        @self.app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
            
        @self.app.errorhandler(403)
        def forbidden(error):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
            
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
            
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.exception("Internal server error: %s", str(error))
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
            
    def register_tenant_middleware(self):
        """Register tenant middleware for multi-tenant support"""
        @self.app.before_request
        def set_tenant_from_auth():
            if 'Authorization' in request.headers:
                try:
                    _, tenant_id = get_user_and_tenant()
                    if tenant_id:
                        g.tenant = tenant_id
                except Exception as e:
                    logger.warning(f"Error extracting tenant from token: {str(e)}")
            
    def register_with_service_registry(self):
        """Register service with the service registry (Consul)"""
        if self.enable_service_registry:
            try:
                register_service(
                    self.app,
                    self.app.config.get('SERVICE_NAME', self.service_name),
                    self.app.config.get('SERVICE_PORT', 5000)
                )
            except Exception as e:
                logger.error(f"Error registering with service registry: {str(e)}")
                
    def run(self, host='0.0.0.0', port=None, debug=False):
        """Run the Flask application"""
        port = port or self.app.config.get('SERVICE_PORT', 5000)
        
        # Register with service registry before starting
        self.register_with_service_registry()
        
        # Run the application
        self.app.run(host=host, port=port, debug=debug)
        
    def get_app(self):
        """Get the Flask application instance"""
        return self.app
        
    def get_db(self):
        """Get the SQLAlchemy database instance"""
        return self.db
