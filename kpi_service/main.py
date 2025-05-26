from flask import Flask
from flasgger import Swagger
from app.routes import kpi_blueprint
from app.extensions import db
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
Swagger(app)

# Register blueprints
app.register_blueprint(kpi_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
