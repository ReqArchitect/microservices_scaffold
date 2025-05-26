from flask import Flask
from .models import db
from .routes import bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing_service.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    return app
