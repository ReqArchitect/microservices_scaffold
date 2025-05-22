"""
Models for the template service
"""
from app import db
from common_utils.base_model import BaseModelMixin, TenantBaseMixin, VersionedModelMixin, JSONModelMixin
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

class TemplateEntity(TenantBaseMixin, VersionedModelMixin, JSONModelMixin, db.Model):
    """
    Example model for Template entity
    """
    __tablename__ = 'template_entities'
    
    # Basic fields
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships (example)
    # parent_id = Column(Integer, ForeignKey('template_entities.id'), nullable=True)
    # children = relationship("TemplateEntity", backref="parent", remote_side=[id])
    
    # Additional fields specific to this entity
    status = Column(String(50), nullable=False, default='draft')
    priority = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<TemplateEntity {self.name}>'
