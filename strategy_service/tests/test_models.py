import pytest
from app.models import Capability, CourseOfAction, OutboxEvent
from app import db
import json

def test_capability_context_ids(app, client):
    """Test that Capability model properly handles context IDs"""
    with app.app_context():
        capability = Capability(
            title="Test Capability",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            business_context_id=100,
            initiative_context_id=200
        )
        db.session.add(capability)
        db.session.commit()
        
        # Verify context IDs are stored
        assert capability.business_context_id == 100
        assert capability.initiative_context_id == 200
        
        # Verify to_dict includes context IDs
        data = capability.to_dict()
        assert data['business_context_id'] == 100
        assert data['initiative_context_id'] == 200

def test_capability_event_emission(app, client):
    """Test that Capability properly emits domain events"""
    with app.app_context():
        capability = Capability(
            title="Test Capability",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            business_context_id=100
        )
        db.session.add(capability)
        db.session.commit()
        
        # Update capability and verify event
        capability.update({'description': 'Updated Description'})
        
        # Check outbox event was created
        event = OutboxEvent.query.filter_by(
            event_type='CapabilityUpdated',
            aggregate_type='Capability',
            aggregate_id=str(capability.id)
        ).first()
        
        assert event is not None
        payload = json.loads(event.payload)
        assert payload['description'] == 'Updated Description'

def test_course_of_action_context_ids(app, client):
    """Test that CourseOfAction model properly handles context IDs"""
    with app.app_context():
        coa = CourseOfAction(
            title="Test CoA",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=200,
            capability_context_id=300
        )
        db.session.add(coa)
        db.session.commit()
        
        # Verify context IDs are stored
        assert coa.initiative_context_id == 200
        assert coa.capability_context_id == 300
        
        # Verify to_dict includes context IDs
        data = coa.to_dict()
        assert data['initiative_context_id'] == 200
        assert data['capability_context_id'] == 300

def test_course_of_action_event_emission(app, client):
    """Test that CourseOfAction properly emits domain events"""
    with app.app_context():
        coa = CourseOfAction(
            title="Test CoA",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=200
        )
        db.session.add(coa)
        db.session.commit()
        
        # Update CoA and verify event
        coa.update({'description': 'Updated Description'})
        
        # Check outbox event was created
        event = OutboxEvent.query.filter_by(
            event_type='CourseOfActionUpdated',
            aggregate_type='CourseOfAction',
            aggregate_id=str(coa.id)
        ).first()
        
        assert event is not None
        payload = json.loads(event.payload)
        assert payload['description'] == 'Updated Description'
