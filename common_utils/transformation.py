"""
Transformation utilities for the ReqArchitect transformation pipeline
"""
import json
import logging
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declared_attr

logger = logging.getLogger(__name__)

class TransformationMixin:
    """
    Mixin for SQLAlchemy models that are part of the transformation pipeline
    
    This mixin adds fields for tracking the transformation lineage of a model
    """
    @declared_attr
    def source_id(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def source_type(cls):
        return Column(String(50), nullable=True)
    
    @declared_attr
    def transformation_id(cls):
        return Column(String(36), nullable=True)
    
    @declared_attr
    def transformation_timestamp(cls):
        return Column(DateTime, default=datetime.utcnow)
    
    @declared_attr
    def transformation_parameters(cls):
        return Column(JSON, nullable=True)
    
    @declared_attr
    def version(cls):
        return Column(String(20), nullable=True)

class TransformationEvent:
    """Base class for transformation events"""
    def __init__(self, source_id=None, source_type=None, target_id=None, target_type=None, 
                 transformation_type=None, parameters=None, metadata=None):
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.source_type = source_type
        self.target_id = target_id
        self.target_type = target_type
        self.transformation_type = transformation_type
        self.parameters = parameters or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_type': self.source_type,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'transformation_type': self.transformation_type,
            'parameters': self.parameters,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
        
    def to_json(self):
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, data):
        event = cls()
        event.id = data.get('id')
        event.source_id = data.get('source_id')
        event.source_type = data.get('source_type')
        event.target_id = data.get('target_id')
        event.target_type = data.get('target_type')
        event.transformation_type = data.get('transformation_type')
        event.parameters = data.get('parameters', {})
        event.metadata = data.get('metadata', {})
        event.timestamp = data.get('timestamp')
        return event
        
    @classmethod
    def from_json(cls, json_data):
        return cls.from_dict(json.loads(json_data))

class TransformationManager:
    """
    Manager for handling transformations between services
    """
    def __init__(self, db=None):
        self.db = db
        
    def register_transformation(self, source_id, source_type, target_id, target_type, 
                                transformation_type, parameters=None, metadata=None):
        """
        Register a transformation in the system
        
        Args:
            source_id: ID of the source object
            source_type: Type of the source object
            target_id: ID of the target object
            target_type: Type of the target object 
            transformation_type: Type of transformation performed
            parameters: Parameters used in the transformation
            metadata: Additional metadata about the transformation
            
        Returns:
            str: The ID of the transformation
        """
        event = TransformationEvent(
            source_id=source_id,
            source_type=source_type,
            target_id=target_id,
            target_type=target_type,
            transformation_type=transformation_type,
            parameters=parameters,
            metadata=metadata
        )
        
        if hasattr(self.db, 'session'):
            from sqlalchemy import Table, Column, String, Integer, JSON, DateTime, MetaData
            from sqlalchemy.ext.declarative import declarative_base
            
            Base = declarative_base()
            class TransformationEventModel(Base):
                __tablename__ = 'transformation_events'
                
                id = Column(String(36), primary_key=True)
                source_id = Column(Integer, nullable=True)
                source_type = Column(String(50), nullable=True)
                target_id = Column(Integer, nullable=True)
                target_type = Column(String(50), nullable=True)
                transformation_type = Column(String(100), nullable=False)
                parameters = Column(JSON, nullable=True)
                metadata = Column(JSON, nullable=True)
                timestamp = Column(DateTime, nullable=False)
                
            try:
                event_model = TransformationEventModel(
                    id=event.id,
                    source_id=event.source_id,
                    source_type=event.source_type,
                    target_id=event.target_id,
                    target_type=event.target_type,
                    transformation_type=event.transformation_type,
                    parameters=event.parameters,
                    metadata=event.metadata,
                    timestamp=datetime.utcnow()
                )
                self.db.session.add(event_model)
                self.db.session.commit()
            except Exception as e:
                logger.error(f"Error registering transformation: {str(e)}")
                if self.db.session:
                    self.db.session.rollback()
        
        # Always return the event ID regardless of DB success
        return event.id
