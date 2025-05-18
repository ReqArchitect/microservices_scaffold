# App init

from flask import Flask, jsonify
from .extensions import db, migrate, jwt
from .models import BusinessCase
from .routes import business_case_blueprint


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or 'config.Config')
    app.config['AUTH_SERVICE_URL'] = 'http://localhost:5001'

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(business_case_blueprint, url_prefix='/api/business_cases')

    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        return jsonify({'error': 'Invalid or missing JSON in request.'}), 400

    return app
