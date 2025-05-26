from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    tenant_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 