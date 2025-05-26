import pytest
from app.events.handlers import handle_capability_event, handle_course_of_action_event
from app.models import ApplicationComponent, ApplicationService, ApplicationInterface, OutboxEvent
from app import db
import json

def test_capability_event_handler(app, client):
    """Test that capability events are properly handled"""
    with app.app_context():
        # Create components linked to capability
        component = ApplicationComponent(
            name="Test Component",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            capability_context_id=100
        )
        
        service = ApplicationService(
            name="Test Service",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            capability_context_id=100
        )
        
        db.session.add(component)
        db.session.add(service)
        db.session.commit()
        
        # Create mock capability event
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
        
        # Verify component and service events were emitted
        component_event = OutboxEvent.query.filter_by(
            event_type="ApplicationComponentCapabilityUpdated",
            aggregate_type="ApplicationComponent"
        ).first()
        
        service_event = OutboxEvent.query.filter_by(
            event_type="ApplicationServiceCapabilityUpdated",
            aggregate_type="ApplicationService"
        ).first()
        
        assert component_event is not None
        assert service_event is not None
        
        comp_payload = json.loads(component_event.payload)
        svc_payload = json.loads(service_event.payload)
        
        assert comp_payload['capability_context_id'] == 100
        assert svc_payload['capability_context_id'] == 100

def test_course_of_action_event_handler(app, client):
    """Test that course of action events are properly handled"""
    with app.app_context():
        # Create interface linked to course of action
        interface = ApplicationInterface(
            name="Test Interface",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            course_of_action_context_id=200
        )
        db.session.add(interface)
        db.session.commit()
        
        # Create mock course of action event
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
        
        # Verify interface event was emitted
        interface_event = OutboxEvent.query.filter_by(
            event_type="ApplicationInterfaceCourseOfActionUpdated",
            aggregate_type="ApplicationInterface"
        ).first()
        
        assert interface_event is not None
        payload = json.loads(interface_event.payload)
        assert payload['course_of_action_context_id'] == 200
