from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Integration(db.Model):
    __tablename__ = 'integrations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    config = db.Column(db.JSON, nullable=True)
    tenant_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IntegrationEvent(db.Model):
    __tablename__ = 'integration_events'
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(64), nullable=False)
    payload = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 