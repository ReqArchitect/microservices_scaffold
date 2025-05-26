from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    channel = db.Column(db.String, nullable=False)
    template_id = db.Column(db.String, nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))

class NotificationTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String, unique=True, nullable=False)
    channel = db.Column(db.String, nullable=False)
    subject = db.Column(db.String)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    email = db.Column(db.Boolean, default=True)
    sms = db.Column(db.Boolean, default=False)
    push = db.Column(db.Boolean, default=True)
    in_app = db.Column(db.Boolean, default=True)
    notifications = db.relationship('Notification', backref='subscription', lazy=True)

class UserNotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'))
    channel = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    response_code = db.Column(db.String)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
