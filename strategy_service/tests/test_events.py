import pytest
from app.events.handlers import handle_business_case_event, handle_initiative_event
from app.models import Capability, CourseOfAction, OutboxEvent
from app import db
import json

def test_business_case_event_handler(app, client):
    """Test that business case events are properly handled"""
    with app.app_context():
        # Create a capability linked to a business case
        capability = Capability(
            title="Test Capability",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            business_context_id=100
        )
        db.session.add(capability)
        db.session.commit()
        
        # Create a mock business case event
        event = OutboxEvent(
            event_type="BusinessCaseUpdated",
            aggregate_type="BusinessCase",
            aggregate_id="100",
            payload=json.dumps({
                "id": 100,
                "status": "approved"
            })
        )
        
        # Handle the event
        handle_business_case_event(event)
        
        # Verify capability event was emitted
        capability_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_type="Capability"
        ).first()
        
        assert capability_event is not None
        payload = json.loads(capability_event.payload)
        assert payload['business_context_id'] == 100

def test_initiative_event_handler(app, client):
    """Test that initiative events are properly handled"""
    with app.app_context():
        # Create a capability and course of action linked to an initiative
        capability = Capability(
            title="Test Capability",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=200
        )
        
        coa = CourseOfAction(
            title="Test CoA",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=200
        )
        
        db.session.add(capability)
        db.session.add(coa)
        db.session.commit()
        
        # Create a mock initiative event
        event = OutboxEvent(
            event_type="InitiativeUpdated",
            aggregate_type="Initiative",
            aggregate_id="200",
            payload=json.dumps({
                "id": 200,
                "status": "approved"
            })
        )
        
        # Handle the event
        handle_initiative_event(event)
        
        # Verify capability and CoA events were emitted
        capability_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_type="Capability"
        ).first()
        
        coa_event = OutboxEvent.query.filter_by(
            event_type="CourseOfActionContextUpdated",
            aggregate_type="CourseOfAction"
        ).first()
        
        assert capability_event is not None
        assert coa_event is not None
        
        cap_payload = json.loads(capability_event.payload)
        coa_payload = json.loads(coa_event.payload)
        
        assert cap_payload['initiative_context_id'] == 200
        assert coa_payload['initiative_context_id'] == 200
