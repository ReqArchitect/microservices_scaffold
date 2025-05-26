from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SubscriptionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    features = db.Column(db.JSON)

class UserSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    plan_id = db.Column(db.String, db.ForeignKey('subscription_plan.plan_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    payment_method = db.Column(db.String)

class BillingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    plan_id = db.Column(db.String)
    transaction_type = db.Column(db.String)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String)

class CreditUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    feature = db.Column(db.String, nullable=False)
    credits_used = db.Column(db.Integer, nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    invoice_date = db.Column(db.Date)
    amount_due = db.Column(db.Float)
    status = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
