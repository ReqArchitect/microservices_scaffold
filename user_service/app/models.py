from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Tenant(db.Model):
    __tablename__ = 'tenant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship("User", backref="tenant")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True)
    password_reset_token = db.Column(db.String(100), unique=True)
    preferences = db.Column(db.JSON, default=lambda: json.dumps({}))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="activities")
