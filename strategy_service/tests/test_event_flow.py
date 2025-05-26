import pytest
import json
from app.models import Capability, CourseOfAction, OutboxEvent
from app.events.handlers import handle_business_case_event, handle_initiative_event
from common_utils.outbox import OutboxEvent

def test_complete_event_flow(app, client):
    """Test the complete event flow between services"""
    with app.app_context():
        # 1. Create a capability with context IDs
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
        
        # Verify capability event was created
        capability_event = OutboxEvent.query.filter_by(
            event_type="CapabilityCreated",
            aggregate_type="Capability",
            aggregate_id=str(capability.id)
        ).first()
        
        assert capability_event is not None
        assert json.loads(capability_event.payload)['business_context_id'] == 100
        assert json.loads(capability_event.payload)['initiative_context_id'] == 200
        
        # 2. Create a course of action linked to the capability
        coa = CourseOfAction(
            title="Test CoA",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            capability_context_id=capability.id,
            initiative_context_id=200
        )
        db.session.add(coa)
        db.session.commit()
        
        # Verify CoA event was created
        coa_event = OutboxEvent.query.filter_by(
            event_type="CourseOfActionCreated",
            aggregate_type="CourseOfAction",
            aggregate_id=str(coa.id)
        ).first()
        
        assert coa_event is not None
        assert json.loads(coa_event.payload)['capability_context_id'] == capability.id
        assert json.loads(coa_event.payload)['initiative_context_id'] == 200
        
        # 3. Simulate receiving a business case event
        business_case_event = OutboxEvent(
            event_type="BusinessCaseUpdated",
            aggregate_type="BusinessCase",
            aggregate_id="100",
            payload=json.dumps({
                "id": 100,
                "status": "approved"
            })
        )
        
        handle_business_case_event(business_case_event)
        
        # Verify capability update event was created
        capability_update_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_type="Capability"
        ).first()
        
        assert capability_update_event is not None
        assert json.loads(capability_update_event.payload)['business_context_id'] == 100
        
        # 4. Simulate receiving an initiative event
        initiative_event = OutboxEvent(
            event_type="InitiativeUpdated",
            aggregate_type="Initiative",
            aggregate_id="200",
            payload=json.dumps({
                "id": 200,
                "status": "approved"
            })
        )
        
        handle_initiative_event(initiative_event)
        
        # Verify capability and CoA update events were created
        capability_initiative_event = OutboxEvent.query.filter_by(
            event_type="CapabilityContextUpdated",
            aggregate_id=str(capability.id)
        ).first()
        
        coa_initiative_event = OutboxEvent.query.filter_by(
            event_type="CourseOfActionContextUpdated",
            aggregate_id=str(coa.id)
        ).first()
        
        assert capability_initiative_event is not None
        assert coa_initiative_event is not None
        assert json.loads(capability_initiative_event.payload)['initiative_context_id'] == 200
        assert json.loads(coa_initiative_event.payload)['initiative_context_id'] == 200
