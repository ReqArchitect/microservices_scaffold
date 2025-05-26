import pytest
from app.events.handlers import handle_capability_event, handle_course_of_action_event
from app.models import BusinessActor, BusinessProcess, OutboxEvent
from app import db
import json

def test_capability_event_handler(app, client):
    """Test that capability events are properly handled"""
    with app.app_context():
        # Create a mock capability event
        event = OutboxEvent(
            event_type="CapabilityUpdated",
            aggregate_type="Capability",
            aggregate_id="100",
            payload=json.dumps({
                "id": 100,
                "title": "Test Capability",
                "status": "approved"
            })
        )
        
        # Handle the event
        handle_capability_event(event)
        
        # Verify business event was emitted
        business_event = OutboxEvent.query.filter_by(
            event_type="BusinessCaseCapabilityUpdated",
            aggregate_type="BusinessCase"
        ).first()
        
        assert business_event is not None
        payload = json.loads(business_event.payload)
        assert payload['capability_id'] == 100

def test_course_of_action_event_handler(app, client):
    """Test that course of action events are properly handled"""
    with app.app_context():
        # Create a mock course of action event
        event = OutboxEvent(
            event_type="CourseOfActionUpdated",
            aggregate_type="CourseOfAction",
            aggregate_id="200",
            payload=json.dumps({
                "id": 200,
                "title": "Test CoA",
                "status": "approved"
            })
        )
        
        # Handle the event
        handle_course_of_action_event(event)
        
        # Verify initiative event was emitted
        initiative_event = OutboxEvent.query.filter_by(
            event_type="InitiativeCourseOfActionUpdated",
            aggregate_type="Initiative"
        ).first()
        
        assert initiative_event is not None
        payload = json.loads(initiative_event.payload)
        assert payload['course_of_action_id'] == 200
