from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SearchQuery(db.Model):
    __tablename__ = 'search_queries'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    tenant_id = db.Column(db.Integer, nullable=True)
    results = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 