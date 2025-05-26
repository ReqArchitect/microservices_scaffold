from flask import Flask
from .routes import bp
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config['OPA_URL'] = os.environ.get('OPA_URL', 'http://localhost:8181/v1/data/validation/allow')
    app.register_blueprint(bp)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(filename='logs/validation_service.log', level=logging.INFO)
    return app
