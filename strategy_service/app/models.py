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
    status = db.Column(db.String(50), nullable=False, default='draft')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # References stored by ID without foreign key constraints
    business_context_id = db.Column(db.Integer, nullable=True)  # Reference to Business context
    initiative_context_id = db.Column(db.Integer, nullable=True)  # Reference to Initiative context
      def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'status': self.status,
            'business_context_id': self.business_context_id,
            'initiative_context_id': self.initiative_context_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def approve(self):
        """Approve a capability and emit domain event"""
        self.status = 'approved'
        self.create_outbox_event(
            event_type="CapabilityApproved",
            aggregate_type="Capability",
            aggregate_id=str(self.id),
            payload=self.to_dict()
        )
    
    def update(self, data):
        """Update capability and emit domain event"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.create_outbox_event(
            event_type="CapabilityUpdated",
            aggregate_type="Capability",
            aggregate_id=str(self.id),
            payload=self.to_dict()
        )

class CourseOfAction(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='draft')
    initiative_context_id = db.Column(db.Integer, nullable=True)  # Reference to Initiative context
    capability_context_id = db.Column(db.Integer, nullable=True)  # Reference to Capability context
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
      def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'status': self.status,
            'initiative_context_id': self.initiative_context_id,
            'capability_context_id': self.capability_context_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
