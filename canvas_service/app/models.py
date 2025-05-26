import uuid
from common_utils.outbox import OutboxMixin
# DB models

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BusinessModelCanvas(db.Model):
    __tablename__ = 'business_model_canvas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    justification = db.Column(db.Text)
    expected_benefits = db.Column(db.Text)
    risk_assessment = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    key_partners = db.relationship('KeyPartner', backref='canvas', cascade='all, delete-orphan')
    key_activities = db.relationship('KeyActivity', backref='canvas', cascade='all, delete-orphan')
    key_resources = db.relationship('KeyResource', backref='canvas', cascade='all, delete-orphan')
    value_propositions = db.relationship('ValueProposition', backref='canvas', cascade='all, delete-orphan')
    customer_segments = db.relationship('CustomerSegment', backref='canvas', cascade='all, delete-orphan')
    channels = db.relationship('Channel', backref='canvas', cascade='all, delete-orphan')
    customer_relationships = db.relationship('CustomerRelationship', backref='canvas', cascade='all, delete-orphan')
    revenue_streams = db.relationship('RevenueStream', backref='canvas', cascade='all, delete-orphan')
    cost_structures = db.relationship('CostStructure', backref='canvas', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'description': self.description,
            'justification': self.justification,
            'expected_benefits': self.expected_benefits,
            'risk_assessment': self.risk_assessment,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class KeyPartner(db.Model):
    __tablename__ = 'key_partner'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    partner_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'partner_type': self.partner_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class KeyActivity(db.Model):
    __tablename__ = 'key_activity'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'activity_type': self.activity_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class KeyResource(db.Model):
    __tablename__ = 'key_resource'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'resource_type': self.resource_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ValueProposition(db.Model):
    __tablename__ = 'value_proposition'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    value_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'value_type': self.value_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerSegment(db.Model):
    __tablename__ = 'customer_segment'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    demographic_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'demographic_info': self.demographic_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Channel(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    channel_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'channel_type': self.channel_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerRelationship(db.Model):
    __tablename__ = 'customer_relationship'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    relationship_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'relationship_type': self.relationship_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RevenueStream(db.Model):
    __tablename__ = 'revenue_stream'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    revenue_model = db.Column(db.String(100))
    amount = db.Column(db.Numeric(12,2))
    currency = db.Column(db.String(3))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'revenue_model': self.revenue_model,
            'amount': float(self.amount) if self.amount is not None else None,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CostStructure(db.Model):
    __tablename__ = 'cost_structure'
    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(db.Integer, db.ForeignKey('business_model_canvas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cost_type = db.Column(db.String(100))
    amount = db.Column(db.Numeric(12,2))
    currency = db.Column(db.String(3))
    frequency = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'canvas_id': self.canvas_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'cost_type': self.cost_type,
            'amount': float(self.amount) if self.amount is not None else None,
            'currency': self.currency,
            'frequency': self.frequency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Outbox Event model for cross-service data consistency
class OutboxEvent(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = db.Column(db.String(100), nullable=False, index=True)
    aggregate_type = db.Column(db.String(100), nullable=False)
    aggregate_id = db.Column(db.String(36), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    error = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)

    @classmethod
    def create_event(cls, session, event_type, aggregate_type, aggregate_id, payload):
        """Create a new outbox event"""
        import json
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=json.dumps(payload)
        )
        session.add(event)
        return event
