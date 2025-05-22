from flask import Flask, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os
from prometheus_flask_exporter import PrometheusMetrics
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Import enhanced architecture components
from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI

# Initialize extensions
from app.models import db
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, enabled=False)
swagger = Swagger()
cors = CORS()
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

AUTH_ATTEMPTS = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['type', 'status']
)

USER_ACTIONS = Counter(
    'user_actions_total',
    'Total user actions',
    ['action_type', 'tenant_id', 'role']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Total number of active users',
    ['tenant_id']
)

VERIFIED_USERS = Gauge(
    'verified_users_total',
    'Total number of verified users',
    ['tenant_id']
)

TENANT_COUNT = Gauge(
    'tenants_total',
    'Total number of tenants'
)

DB_OPERATION_LATENCY = Histogram(
    'db_operation_duration_seconds',
    'Database operation latency',
    ['operation']
)

USER_ACTION_LATENCY = Histogram(
    'user_action_duration_seconds',
    'User action latency',
    ['action_type']
)

FAILED_LOGINS = Counter(
    'failed_logins_total',
    'Total failed login attempts',
    ['reason']
)

TOKEN_REFRESHES = Counter(
    'token_refreshes_total',
    'Total token refresh attempts',
    ['status']
)

PASSWORD_RESETS = Counter(
    'password_resets_total',
    'Total password reset attempts',
    ['status']
)

EMAIL_VERIFICATIONS = Counter(
    'email_verifications_total',
    'Total email verification attempts',
    ['status']
)

USER_ROLE_CHANGES = Counter(
    'user_role_changes_total',
    'Total user role changes',
    ['from_role', 'to_role']
)

TENANT_USER_COUNT = Gauge(
    'tenant_user_count',
    'Number of users per tenant',
    ['tenant_id']
)

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == "development":
        app.config.from_object("app.config.DevelopmentConfig")
    elif config_name == "testing":
        app.config.from_object("app.config.TestingConfig")
    else:
        app.config.from_object("app.config.ProductionConfig")

    # Initialize extensions
    db.init_app(app)  # Initialize SQLAlchemy with the app
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure rate limiter based on environment
    if not app.config.get('RATELIMIT_ENABLED', True):
        limiter.enabled = False
    limiter.init_app(app)
    
    swagger.init_app(app)
    cors.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    if app.config.get('TESTING', False):
        # Use StreamHandler for tests to avoid file lock issues
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        file_handler = RotatingFileHandler('logs/user_service.log',
                                         maxBytes=10240,
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('User service startup')

    # Register blueprints
    from app.routes import v1_blueprint
    app.register_blueprint(v1_blueprint)

    # Request monitoring middleware
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint
            ).observe(duration)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=response.status_code
            ).inc()

        return response

    # Database monitoring
    @app.before_request
    def before_db_operation():
        if request.endpoint and 'api' in request.endpoint:
            request.db_start_time = time.time()

    @app.after_request
    def after_db_operation(response):
        if hasattr(request, 'db_start_time'):
            duration = time.time() - request.db_start_time
            DB_OPERATION_LATENCY.labels(
                operation=request.endpoint
            ).observe(duration)
        return response

    # Update metrics periodically
    def update_metrics():
        with app.app_context():
            from app.models import User, Tenant, UserActivity
            
            # Update user metrics
            tenants = Tenant.query.all()
            for tenant in tenants:
                active_count = User.query.filter_by(
                    tenant_id=tenant.id,
                    is_active=True
                ).count()
                verified_count = User.query.filter_by(
                    tenant_id=tenant.id,
                    is_email_verified=True
                ).count()
                total_count = User.query.filter_by(
                    tenant_id=tenant.id
                ).count()
                
                ACTIVE_USERS.labels(tenant_id=tenant.id).set(active_count)
                VERIFIED_USERS.labels(tenant_id=tenant.id).set(verified_count)
                TENANT_USER_COUNT.labels(tenant_id=tenant.id).set(total_count)
            
            TENANT_COUNT.set(len(tenants))
            
            # Update action metrics
            recent_activities = UserActivity.query.filter(
                UserActivity.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).all()
            
            action_counts = defaultdict(lambda: defaultdict(int))
            for activity in recent_activities:
                user = User.query.get(activity.user_id)
                if user:
                    action_counts[activity.action][user.role] += 1
            
            for action, role_counts in action_counts.items():
                for role, count in role_counts.items():
                    USER_ACTIONS.labels(
                        action_type=action,
                        tenant_id=user.tenant_id,
                        role=role
                    ).inc(count)

    if not app.debug and not app.testing:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_metrics, 'interval', minutes=5)
        scheduler.start()

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url}')
        return {"message": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        app.logger.error(f'Request URL: {request.url}')
        app.logger.error(f'Request Method: {request.method}')
        app.logger.error(f'Request Data: {request.get_data()}')
        return {"message": "Internal server error"}, 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f'Unhandled Exception: {e}')
        app.logger.error(f'Request URL: {request.url}')
        app.logger.error(f'Request Method: {request.method}')
        app.logger.error(f'Request Data: {request.get_data()}')
        import traceback
        app.logger.error(f'Traceback: {traceback.format_exc()}')
        return {"message": "Internal server error"}, 500

    return app
