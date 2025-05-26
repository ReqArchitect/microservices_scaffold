from . import db
from common_utils.outbox import OutboxMixin
import uuid
import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey

# Outbox Event model for data consistency
class OutboxEvent(db.Model):
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_type = Column(String(100), nullable=False)
    aggregate_id = Column(String(36), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    @classmethod
    def create_event(cls, session, event_type, aggregate_type, aggregate_id, payload):
        """
        Create a new outbox event
        """
        import json
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=json.dumps(payload)
        )
        session.add(event)
        return event

class Capability(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    business_case_id = db.Column(db.Integer, nullable=True)
    initiative_id = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'business_case_id': self.business_case_id,
            'initiative_id': self.initiative_id
        }

class CourseOfAction(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    initiative_id = db.Column(db.Integer, nullable=True)
    capability_id = db.Column(db.Integer, db.ForeignKey('capability.id'), nullable=True)
    capability = db.relationship('Capability', backref='courses_of_action')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'initiative_id': self.initiative_id,
            'capability_id': self.capability_id
        }
