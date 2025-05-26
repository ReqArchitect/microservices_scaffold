# App init

from flask import Flask, jsonify
from .extensions import db, migrate, jwt
from .models import BusinessCase
from .routes import business_case_blueprint

from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()




def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or 'config.Config')
    app.config['AUTH_SERVICE_URL'] = 'http://localhost:5001'

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

    app.register_blueprint(business_case_blueprint, url_prefix='/api/business_cases')

    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        return jsonify({'error': 'Invalid or missing JSON in request.'}), 400

    return app
