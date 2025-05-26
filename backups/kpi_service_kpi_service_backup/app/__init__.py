# App init

from flask import Flask
from .extensions import db
from .routes import kpi_blueprint

def create_app(config_object=None):
    app = Flask(__name__)
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
    db.init_app(app)
    app.register_blueprint(kpi_blueprint)
    return app
