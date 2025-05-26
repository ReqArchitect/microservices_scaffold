from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Integration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    config = db.Column(db.JSON, nullable=True)

class IntegrationEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integration.id'), nullable=False)
    event_type = db.Column(db.String(64), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class IntegrationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integration.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 