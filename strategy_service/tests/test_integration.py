"""Integration test for domain event flow between services"""
import pytest
import json
import requests
from datetime import datetime
from app import create_app, db
from app.models import Capability, CourseOfAction, OutboxEvent

def test_capability_creation_event_flow(app, client):
    """Test the complete event flow when creating a capability"""
    with app.app_context():
        # 1. Create a capability with context IDs
        capability_data = {
            "title": "Test Capability",
            "description": "Testing event flow",
            "user_id": 1,
            "tenant_id": 1,
            "business_context_id": 100,
            "initiative_context_id": 200
        }
        
        response = client.post('/api/v1/capabilities', 
                             json=capability_data,
                             headers={'Authorization': 'Bearer test-token'})
        assert response.status_code == 201
        
        # 2. Verify capability was created with context IDs
        capability = Capability.query.first()
        assert capability is not None
        assert capability.business_context_id == 100
        assert capability.initiative_context_id == 200
        
        # 3. Verify outbox event was created
        event = OutboxEvent.query.filter_by(
            event_type='CapabilityCreated',
            aggregate_type='Capability'
        ).first()
        assert event is not None
        
        # 4. Verify event payload contains context IDs
        payload = json.loads(event.payload)
        assert payload['business_context_id'] == 100
        assert payload['initiative_context_id'] == 200

def test_course_of_action_event_flow(app, client):
    """Test the complete event flow when creating a course of action"""
    with app.app_context():
        # 1. Create a course of action with context IDs
        coa_data = {
            "title": "Test Course of Action",
            "description": "Testing event flow",
            "user_id": 1,
            "tenant_id": 1,
            "initiative_context_id": 200,
            "capability_context_id": 300
        }
        
        response = client.post('/api/v1/courses-of-action', 
                             json=coa_data,
                             headers={'Authorization': 'Bearer test-token'})
        assert response.status_code == 201
        
        # 2. Verify course of action was created with context IDs
        coa = CourseOfAction.query.first()
        assert coa is not None
        assert coa.initiative_context_id == 200
        assert coa.capability_context_id == 300
        
        # 3. Verify outbox event was created
        event = OutboxEvent.query.filter_by(
            event_type='CourseOfActionCreated',
            aggregate_type='CourseOfAction'
        ).first()
        assert event is not None
        
        # 4. Verify event payload contains context IDs
        payload = json.loads(event.payload)
        assert payload['initiative_context_id'] == 200
        assert payload['capability_context_id'] == 300

def test_capability_update_propagation(app, client):
    """Test that capability updates propagate through the event system"""
    with app.app_context():
        # 1. Create initial capability
        capability = Capability(
            title="Test Capability",
            description="Initial description",
            user_id=1,
            tenant_id=1,
            business_context_id=100
        )
        db.session.add(capability)
        db.session.commit()
        
        # 2. Update the capability
        update_data = {
            "description": "Updated description",
            "status": "approved"
        }
        
        response = client.patch(f'/api/v1/capabilities/{capability.id}',
                              json=update_data,
                              headers={'Authorization': 'Bearer test-token'})
        assert response.status_code == 200
        
        # 3. Verify update event was created
        update_event = OutboxEvent.query.filter_by(
            event_type='CapabilityUpdated',
            aggregate_type='Capability',
            aggregate_id=str(capability.id)
        ).first()
        
        assert update_event is not None
        payload = json.loads(update_event.payload)
        assert payload['description'] == "Updated description"
        assert payload['status'] == "approved"
        assert payload['business_context_id'] == 100

def test_cross_service_event_handling(app, client):
    """Test that events are properly handled across service boundaries"""
    with app.app_context():
        # 1. Simulate receiving a business case event
        business_case_event = OutboxEvent(
            event_type="BusinessCaseUpdated",
            aggregate_type="BusinessCase",
            aggregate_id="100",
            payload=json.dumps({
                "id": 100,
                "status": "approved",
                "title": "Test Business Case"
            })
        )
        db.session.add(business_case_event)
        
        # 2. Create capability linked to the business case
        capability = Capability(
            title="Test Capability",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            business_context_id=100
        )
        db.session.add(capability)
        db.session.commit()
        
        # 3. Process the event
        from app.events.handlers import handle_business_case_event
        handle_business_case_event(business_case_event)
        
        # 4. Verify capability event was created
        capability_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_type="Capability"
        ).first()
        
        assert capability_event is not None
        payload = json.loads(capability_event.payload)
        assert payload['business_context_id'] == 100

def test_event_handler_chain(app, client):
    """Test the complete chain of event handlers across services"""
    with app.app_context():
        # 1. Create initial capability with business context
        capability = Capability(
            title="Test Capability",
            description="Initial description",
            user_id=1,
            tenant_id=1,
            business_context_id=100
        )
        db.session.add(capability)
        db.session.commit()
        
        # 2. Create course of action linked to capability
        coa = CourseOfAction(
            title="Test CoA",
            description="Initial CoA description",
            user_id=1,
            tenant_id=1,
            capability_context_id=capability.id
        )
        db.session.add(coa)
        db.session.commit()
        
        # 3. Simulate business case update event
        business_case_event = OutboxEvent(
            event_type="BusinessCaseUpdated",
            aggregate_type="BusinessCase",
            aggregate_id="100",
            payload=json.dumps({
                "id": 100,
                "status": "approved",
                "title": "Updated Business Case"
            })
        )
        db.session.add(business_case_event)
        db.session.commit()
        
        # 4. Process the event through business case handler
        from app.events.handlers import handle_business_case_event
        handle_business_case_event(business_case_event)
        
        # 5. Verify capability event was created
        capability_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_type="Capability",
            aggregate_id=str(capability.id)
        ).first()
        
        assert capability_event is not None
        cap_payload = json.loads(capability_event.payload)
        assert cap_payload['business_context_id'] == 100
        
        # 6. Simulate initiative update event
        initiative_event = OutboxEvent(
            event_type="InitiativeUpdated",
            aggregate_type="Initiative",
            aggregate_id="200",
            payload=json.dumps({
                "id": 200,
                "status": "in_progress",
                "title": "Updated Initiative"
            })
        )
        db.session.add(initiative_event)
        db.session.commit()
        
        # 7. Process the event through initiative handler
        from app.events.handlers import handle_initiative_event
        handle_initiative_event(initiative_event)
        
        # 8. Verify course of action event was created
        coa_event = OutboxEvent.query.filter_by(
            event_type="CourseOfActionContextUpdated",
            aggregate_type="CourseOfAction",
            aggregate_id=str(coa.id)
        ).first()
        
        assert coa_event is not None
        coa_payload = json.loads(coa_event.payload)
        assert coa_payload['capability_context_id'] == capability.id
