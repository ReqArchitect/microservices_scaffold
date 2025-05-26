from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    policy_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class ValidationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    input_data = db.Column(db.JSON, nullable=False)
    result = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 