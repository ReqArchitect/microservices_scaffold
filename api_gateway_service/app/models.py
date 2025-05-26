from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class APILog(db.Model):
    __tablename__ = 'api_logs'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(16), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    tenant_id = db.Column(db.Integer, nullable=True)
    request_data = db.Column(db.JSON, nullable=True)
    response_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 