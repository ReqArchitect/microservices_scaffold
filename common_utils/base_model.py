"""
Base model classes for ReqArchitect microservices
"""
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSON as PostgresJSON

class BaseModelMixin:
    """Base mixin for SQLAlchemy models"""
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Common methods
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def to_json(self):
        """Convert model to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data):
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def get_by_id(cls, id):
        """Get model by ID"""
        return cls.query.get(id)
    
    def save(self, db_session):
        """Save model to database"""
        db_session.add(self)
        db_session.commit()
        return self
    
    def delete(self, db_session):
        """Delete model from database"""
        db_session.delete(self)
        db_session.commit()

class TenantBaseMixin(BaseModelMixin):
    """Base mixin for multi-tenant models"""
    
    # Tenant ID
    tenant_id = Column(String(36), nullable=False, index=True)
    
    @classmethod
    def get_by_id_for_tenant(cls, id, tenant_id):
        """Get model by ID for a specific tenant"""
        return cls.query.filter_by(id=id, tenant_id=tenant_id).first()
    
    @classmethod
    def get_all_for_tenant(cls, tenant_id):
        """Get all models for a specific tenant"""
        return cls.query.filter_by(tenant_id=tenant_id).all()

class VersionedModelMixin(BaseModelMixin):
    """Mixin for versioned models"""
    
    # Version fields
    version = Column(String(20), nullable=False, default="v1")
    is_active = Column(Boolean, nullable=False, default=True)
    replaced_by_id = Column(Integer, nullable=True)
    
    @classmethod
    def get_active_version(cls, id):
        """Get the active version of a model"""
        return cls.query.filter_by(id=id, is_active=True).first()
    
    @classmethod
    def get_all_versions(cls, id):
        """Get all versions of a model, ordered by version"""
        return cls.query.filter_by(id=id).order_by(cls.version).all()
    
    def create_new_version(self, db_session, new_data=None, new_version=None):
        """
        Create a new version of this model
        
        Args:
            db_session: SQLAlchemy database session
            new_data: Dictionary of fields to update in the new version
            new_version: Version string for the new version
            
        Returns:
            New version of the model
        """
        # Create new instance with same data
        data = self.to_dict()
        
        # Remove fields that should not be copied
        for field in ['id', 'created_at', 'updated_at', 'version', 'replaced_by_id']:
            if field in data:
                del data[field]
        
        # Update with new data
        if new_data:
            data.update(new_data)
        
        # Create new instance
        new_instance = type(self)(**data)
        
        # Set version
        if new_version:
            new_instance.version = new_version
        else:
            # Increment version (e.g., v1 -> v2)
            current_version = self.version
            if current_version.startswith('v') and current_version[1:].isdigit():
                version_num = int(current_version[1:])
                new_instance.version = f"v{version_num + 1}"
            else:
                new_instance.version = f"{current_version}_new"
        
        # Set as active, mark current as inactive
        new_instance.is_active = True
        self.is_active = False
        
        # Set replaced_by reference
        db_session.add(new_instance)
        db_session.flush()  # Get ID for new instance
        self.replaced_by_id = new_instance.id
        
        # Save changes
        db_session.add(self)
        db_session.add(new_instance)
        db_session.commit()
        
        return new_instance

class JSONModelMixin:
    """Mixin for models with JSON fields"""
    
    @declared_attr
    def metadata_json(cls):
        """JSON metadata field"""
        return Column(MutableDict.as_mutable(PostgresJSON), nullable=True)
    
    def get_metadata(self, key, default=None):
        """Get a metadata value by key"""
        if not self.metadata_json:
            return default
        return self.metadata_json.get(key, default)
    
    def set_metadata(self, key, value):
        """Set a metadata value by key"""
        if not self.metadata_json:
            self.metadata_json = {}
        self.metadata_json[key] = value
    
    def delete_metadata(self, key):
        """Delete a metadata value by key"""
        if not self.metadata_json:
            return
        if key in self.metadata_json:
            del self.metadata_json[key]
            
    def update_metadata(self, data):
        """Update metadata with dictionary of values"""
        if not self.metadata_json:
            self.metadata_json = {}
        self.metadata_json.update(data)
