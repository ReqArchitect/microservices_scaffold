from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.orm import validates
import re
from . import db  # Import db from __init__.py

class Initiative(db.Model):
    """Initiative model representing strategic initiatives."""
    __tablename__ = 'initiatives'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    strategic_objective = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    progress = db.Column(db.Integer, default=0)  # 0-100
    tenant_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    business_case_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False)
    updated_by = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    tags = db.Column(db.String(255))  # Comma-separated tags

    # Relationships
    members = db.relationship('InitiativeMember', back_populates='initiative', cascade='all, delete-orphan')

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_owner', 'owner_id'),
        Index('idx_dates', 'start_date', 'end_date'),
    )

    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        if len(title) > 120:
            raise ValueError("Title must be less than 120 characters")
        return title.strip()

    @validates('strategic_objective')
    def validate_strategic_objective(self, key, objective):
        if not objective or len(objective.strip()) == 0:
            raise ValueError("Strategic objective cannot be empty")
        if len(objective) > 255:
            raise ValueError("Strategic objective must be less than 255 characters")
        return objective.strip()

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['draft', 'active', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return status

    @validates('priority')
    def validate_priority(self, key, priority):
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority

    @validates('progress')
    def validate_progress(self, key, progress):
        if not isinstance(progress, int):
            raise ValueError("Progress must be an integer")
        if progress < 0 or progress > 100:
            raise ValueError("Progress must be between 0 and 100")
        return progress

    @validates('tags')
    def validate_tags(self, key, tags):
        if tags:
            # Remove any special characters and normalize spaces
            tags = re.sub(r'[^a-zA-Z0-9\s,]', '', tags)
            # Remove duplicate tags and sort them
            unique_tags = sorted(set(tag.strip() for tag in tags.split(',')))
            return ','.join(unique_tags)
        return tags

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'strategic_objective': self.strategic_objective,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'priority': self.priority,
            'progress': self.progress,
            'tenant_id': self.tenant_id,
            'owner_id': self.owner_id,
            'business_case_id': self.business_case_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active,
            'tags': self.tags.split(',') if self.tags else []
        }

class InitiativeMember(db.Model):
    """Initiative member model."""
    __tablename__ = 'initiative_members'

    id = db.Column(db.Integer, primary_key=True)
    initiative_id = db.Column(db.Integer, db.ForeignKey('initiatives.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin or member
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    initiative = db.relationship('Initiative', back_populates='members')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('initiative_id', 'user_id', name='uix_initiative_member'),
    )

    def to_dict(self):
        """Convert member to dictionary."""
        return {
            'id': self.id,
            'initiative_id': self.initiative_id,
            'user_id': self.user_id,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
