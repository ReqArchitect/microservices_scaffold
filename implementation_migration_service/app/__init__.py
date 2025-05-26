from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event
from .models import db
from .routes import bp as implementation_bp

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///implementation_migration_service.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    jwt = init_jwt(app)
    oauth = init_oauth(app)
    metrics = init_metrics(app)
    register_error_handlers(app)
    db.init_app(app)
    app.register_blueprint(implementation_bp, url_prefix='/api/implementation')
    with app.app_context():
        db.create_all()
    return app
