# Data consistency utilities for microservices
import json
import uuid
import datetime
from enum import Enum
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String, DateTime, Boolean, event
from sqlalchemy.orm import Session
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class EventStatus(Enum):
    """Status of an outbox event"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OutboxEvent:
    """Base class for implementing the Outbox pattern"""
    
    @declared_attr
    def __tablename__(cls):
        return "outbox_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_type = Column(String(100), nullable=False)
    aggregate_id = Column(String(36), nullable=False)
    payload = Column(String, nullable=False)
    status = Column(String(20), default=EventStatus.PENDING.value, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    
    @classmethod
    def create_event(cls, session, event_type, aggregate_type, aggregate_id, payload):
        """
        Create a new outbox event
        
        Args:
            session: SQLAlchemy session
            event_type: Type of event (e.g., 'capability_created')
            aggregate_type: Type of aggregate (e.g., 'capability')
            aggregate_id: ID of the aggregate
            payload: Event data (will be JSON serialized)
            
        Returns:
            Created OutboxEvent instance
        """
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=json.dumps(payload)
        )
        session.add(event)
        return event
    
    def mark_as_processing(self, session):
        """Mark event as being processed"""
        self.status = EventStatus.PROCESSING.value
        session.add(self)
        
    def mark_as_completed(self, session):
        """Mark event as completed"""
        self.status = EventStatus.COMPLETED.value
        self.processed_at = datetime.datetime.utcnow()
        session.add(self)
        
    def mark_as_failed(self, session, error=None):
        """Mark event as failed with optional error message"""
        self.status = EventStatus.FAILED.value
        self.error = error
        self.retry_count += 1
        session.add(self)

# SQLAlchemy hooks for automatic outbox event creation
def configure_outbox_hooks(outbox_event_cls):
    """
    Configure SQLAlchemy hooks for automatic outbox event creation
    
    Args:
        outbox_event_cls: OutboxEvent class or subclass
    """
    @event.listens_for(Session, 'before_flush')
    def capture_model_changes(session, context, instances):
        for obj in session.new:
            if hasattr(obj, '__outbox_enabled__') and obj.__outbox_enabled__:
                # New object being inserted
                payload = obj.to_dict() if hasattr(obj, 'to_dict') else {
                    c.name: getattr(obj, c.name) 
                    for c in obj.__table__.columns
                }
                
                aggregate_type = obj.__tablename__
                event_type = f"{aggregate_type}_created"
                
                outbox_event_cls.create_event(
                    session=session,
                    event_type=event_type,
                    aggregate_type=aggregate_type,
                    aggregate_id=str(getattr(obj, 'id')),
                    payload=payload
                )
        
        for obj in session.dirty:
            if hasattr(obj, '__outbox_enabled__') and obj.__outbox_enabled__:
                # Changed attributes
                changed = {}
                for attr in session.attrs:
                    if attr.key != 'id' and attr.history.has_changes():
                        changed[attr.key] = getattr(obj, attr.key)
                
                if changed:
                    payload = {
                        'changes': changed,
                        'full_object': obj.to_dict() if hasattr(obj, 'to_dict') else {
                            c.name: getattr(obj, c.name) 
                            for c in obj.__table__.columns
                        }
                    }
                    
                    aggregate_type = obj.__tablename__
                    event_type = f"{aggregate_type}_updated"
                    
                    outbox_event_cls.create_event(
                        session=session,
                        event_type=event_type,
                        aggregate_type=aggregate_type,
                        aggregate_id=str(getattr(obj, 'id')),
                        payload=payload
                    )
        
        for obj in session.deleted:
            if hasattr(obj, '__outbox_enabled__') and obj.__outbox_enabled__:
                payload = {'id': getattr(obj, 'id')}
                
                aggregate_type = obj.__tablename__
                event_type = f"{aggregate_type}_deleted"
                
                outbox_event_cls.create_event(
                    session=session,
                    event_type=event_type,
                    aggregate_type=aggregate_type,
                    aggregate_id=str(getattr(obj, 'id')),
                    payload=payload
                )

class OutboxMixin:
    """Mixin to enable outbox pattern on a model"""
    __outbox_enabled__ = True

# Outbox processor for background processing of events
class OutboxProcessor:
    """Process outbox events in background"""
    
    def __init__(self, db, outbox_model, handlers=None, max_retries=3):
        """
        Initialize outbox processor
        
        Args:
            db: SQLAlchemy DB instance
            outbox_model: OutboxEvent model class
            handlers: Dict mapping event_type to handler functions
            max_retries: Maximum retry attempts for failed events
        """
        self.db = db
        self.outbox_model = outbox_model
        self.handlers = handlers or {}
        self.max_retries = max_retries
        
    def register_handler(self, event_type, handler):
        """Register a handler for an event type"""
        self.handlers[event_type] = handler
        
    def process_pending_events(self, limit=100):
        """
        Process pending outbox events
        
        Args:
            limit: Maximum number of events to process
            
        Returns:
            Number of successfully processed events
        """
        processed_count = 0
        
        # Get pending events
        events = self.outbox_model.query.filter_by(
            status=EventStatus.PENDING.value
        ).order_by(
            self.outbox_model.created_at
        ).limit(limit).all()
        
        for event in events:
            try:
                # Mark as processing
                event.mark_as_processing(self.db.session)
                self.db.session.commit()
                
                # Process the event
                self._process_event(event)
                
                # Mark as completed
                event.mark_as_completed(self.db.session)
                self.db.session.commit()
                processed_count += 1
                
            except Exception as e:
                self.db.session.rollback()
                logger.error(f"Error processing outbox event {event.id}: {str(e)}")
                
                event.mark_as_failed(self.db.session, str(e))
                self.db.session.commit()
        
        # Also retry failed events with retry_count < max_retries
        failed_events = self.outbox_model.query.filter_by(
            status=EventStatus.FAILED.value
        ).filter(
            self.outbox_model.retry_count < self.max_retries
        ).limit(limit).all()
        
        for event in failed_events:
            try:
                # Mark as processing again
                event.mark_as_processing(self.db.session)
                self.db.session.commit()
                
                # Process the event
                self._process_event(event)
                
                # Mark as completed
                event.mark_as_completed(self.db.session)
                self.db.session.commit()
                processed_count += 1
                
            except Exception as e:
                self.db.session.rollback()
                logger.error(f"Error retrying outbox event {event.id}: {str(e)}")
                
                event.mark_as_failed(self.db.session, str(e))
                self.db.session.commit()
        
        return processed_count
    
    def _process_event(self, event):
        """
        Process a single outbox event
        
        Args:
            event: OutboxEvent instance to process
            
        Raises:
            ValueError: If no handler is registered for the event type
        """
        # Get handler for this event type
        handler = self.handlers.get(event.event_type)
        if not handler:
            raise ValueError(f"No handler registered for event type: {event.event_type}")
        
        # Parse payload
        payload = json.loads(event.payload)
        
        # Call handler
        handler(event.aggregate_id, payload, event)
