from flask import Flask
from common_utils.logging import setup_logging
from common_utils.db import get_engine, get_session
from common_utils.cache import get_redis
from common_utils.auth import init_jwt, init_oauth, rbac_required
from common_utils.monitoring import init_metrics
from common_utils.errors import register_error_handlers
from common_utils.config import load_config
from common_utils.traceability import log_audit_event
from .routes import bp
import logging
import os

def create_app(config_name="development"):
    app = Flask(__name__)
    jwt = init_jwt(app)
    oauth = init_oauth(app)
    metrics = init_metrics(app)
    register_error_handlers(app)
    app.config['OPA_URL'] = os.environ.get('OPA_URL', 'http://localhost:8181/v1/data/validation/allow')
    app.register_blueprint(bp)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename='logs/validation_service.log', level=logging.INFO)
    return app
