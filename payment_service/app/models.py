from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), nullable=False)
    status = db.Column(db.String(32), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    plan = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), default='active')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True) 