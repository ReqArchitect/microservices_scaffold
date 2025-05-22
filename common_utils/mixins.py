from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean

class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftDeleteMixin(object):
    is_deleted = Column(Boolean, default=False) 