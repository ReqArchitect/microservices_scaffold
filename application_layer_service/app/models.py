import uuid
import datetime
from common_utils.outbox import OutboxMixin
from . import db

<<<<<<< HEAD
class ApplicationComponent(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
=======
class ApplicationComponent(db.Model):
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
<<<<<<< HEAD
    capability_context_id = db.Column(db.Integer, nullable=True)  # Reference to Capability context
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'capability_context_id': self.capability_context_id
        }
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3

class ApplicationCollaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)

<<<<<<< HEAD
class ApplicationInterface(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
=======
class ApplicationInterface(db.Model):
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
<<<<<<< HEAD
    course_of_action_context_id = db.Column(db.Integer, nullable=True)  # Reference to Course of Action context
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'course_of_action_context_id': self.course_of_action_context_id
        }
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3

class ApplicationFunction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)

class ApplicationInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)

<<<<<<< HEAD
class ApplicationService(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
=======
class ApplicationService(db.Model):
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
<<<<<<< HEAD
    capability_context_id = db.Column(db.Integer, nullable=True)  # Reference to Capability context
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'capability_context_id': self.capability_context_id
        }
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3

class DataObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)


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
