"""
Models for the AI Orchestrator Service
"""
from app import db
from common_utils.base_model import BaseModelMixin, TenantBaseMixin, VersionedModelMixin, JSONModelMixin
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime

class AIProvider(BaseModelMixin, JSONModelMixin, db.Model):
    """
    AI Provider configuration
    """
    __tablename__ = 'ai_providers'
    
    name = Column(String(50), nullable=False, unique=True)
    api_type = Column(String(50), nullable=False)  # openai, anthropic, huggingface, etc.
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    default_model = Column(String(50), nullable=True)
    rate_limit = Column(Integer, default=100)  # Requests per minute
    credentials = Column(Text, nullable=True)  # Encrypted credentials
    
    # Relationships
    models = relationship("AIModel", back_populates="provider")
    
    def __repr__(self):
        return f'<AIProvider {self.name}>'

class AIModel(BaseModelMixin, JSONModelMixin, db.Model):
    """
    AI Model configuration
    """
    __tablename__ = 'ai_models'
    
    name = Column(String(50), nullable=False)
    provider_id = Column(Integer, ForeignKey('ai_providers.id'), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(50), nullable=False)  # text, code, image, etc.
    is_enabled = Column(Boolean, default=True)
    capabilities = Column(Text, nullable=True)  # JSON string of capabilities
    context_length = Column(Integer, default=4096)
    version = Column(String(20), nullable=True)
    
    # Cost information
    cost_per_token_input = Column(Float, default=0.0)
    cost_per_token_output = Column(Float, default=0.0)
    
    # Relationships
    provider = relationship("AIProvider", back_populates="models")
    
    def __repr__(self):
        return f'<AIModel {self.name}>'

class AIRequest(TenantBaseMixin, JSONModelMixin, db.Model):
    """
    AI Request record for tracking and billing
    """
    __tablename__ = 'ai_requests'
    
    provider_id = Column(Integer, ForeignKey('ai_providers.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    operation_type = Column(String(50), nullable=False)  # code_generation, semantic_analysis, etc.
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    duration_ms = Column(Integer, default=0)
    status = Column(String(20), default='pending')  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    request_id = Column(String(36), nullable=True, index=True)
    request_data = Column(Text, nullable=True)  # JSON of the request
    response_data = Column(Text, nullable=True)  # JSON of the response
    
    # Relationships
    provider = relationship("AIProvider")
    model = relationship("AIModel")
    
    def __repr__(self):
        return f'<AIRequest {self.id} ({self.operation_type})>'

class TransformationTemplate(TenantBaseMixin, VersionedModelMixin, JSONModelMixin, db.Model):
    """
    Templates for transformations
    """
    __tablename__ = 'transformation_templates'
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    transformation_type = Column(String(50), nullable=False)  # strategy_to_business, business_to_application, etc.
    source_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    prompt_template = Column(Text, nullable=False)  # The template for generating the prompt
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON of default parameters
    
    # Relationships
    model = relationship("AIModel")
    
    def __repr__(self):
        return f'<TransformationTemplate {self.name}>'
