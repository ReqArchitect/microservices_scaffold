import uuid
import datetime
from common_utils.outbox import OutboxMixin
from sqlalchemy import Column, String, Float, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class BusinessCase(db.Model):
    __tablename__ = 'business_cases'
    id = Column(Integer, primary_key=True)
    # Add any other fields as needed
    kpis = relationship('KPI', back_populates='business_case')

class KPI(db.Model):
    __tablename__ = 'kpis'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)
    business_case_id = Column(Integer, ForeignKey('business_cases.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    metric = Column(String, nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    business_case = relationship('BusinessCase', back_populates='kpis')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'owner_id': self.owner_id,
            'business_case_id': self.business_case_id,
            'title': self.title,
            'description': self.description,
            'metric': self.metric,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'start_date': str(self.start_date) if self.start_date else None,
            'end_date': str(self.end_date) if self.end_date else None
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
