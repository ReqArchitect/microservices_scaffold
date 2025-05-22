# Entry point

from app import create_app
from app.extensions import db, migrate
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
