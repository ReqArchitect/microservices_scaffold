from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    tenant_id = db.Column(db.Integer, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True) 