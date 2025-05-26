from flask import Flask
from .models import db
from .routes import bp
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_service.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
    db.init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    return app
