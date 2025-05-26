import pytest
from app.models import BusinessActor, BusinessProcess, OutboxEvent
from app import db
import json

def test_business_actor_outbox_events(app, client):
    """Test that BusinessActor properly handles outbox events"""
    with app.app_context():
        actor = BusinessActor(
            name="Test Actor",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=100
        )
        db.session.add(actor)
        db.session.commit()
        
        # Verify to_dict includes context ID
        data = actor.to_dict()
        assert data['initiative_context_id'] == 100
        
        # Update actor and verify event
        actor.update({'description': 'Updated Description'})
        
        event = OutboxEvent.query.filter_by(
            event_type='BusinessActorUpdated',
            aggregate_type='BusinessActor',
            aggregate_id=str(actor.id)
        ).first()
        
        assert event is not None
        payload = json.loads(event.payload)
        assert payload['description'] == 'Updated Description'
        assert payload['initiative_context_id'] == 100

def test_business_process_outbox_events(app, client):
    """Test that BusinessProcess properly handles outbox events"""
    with app.app_context():
        process = BusinessProcess(
            name="Test Process",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            initiative_context_id=100,
            kpi_context_id=200
        )
        db.session.add(process)
        db.session.commit()
        
        # Verify to_dict includes context IDs
        data = process.to_dict()
        assert data['initiative_context_id'] == 100
        assert data['kpi_context_id'] == 200
        
        # Update process and verify event
        process.update({'description': 'Updated Description'})
        
        event = OutboxEvent.query.filter_by(
            event_type='BusinessProcessUpdated',
            aggregate_type='BusinessProcess',
            aggregate_id=str(process.id)
        ).first()
        
        assert event is not None
        payload = json.loads(event.payload)
        assert payload['description'] == 'Updated Description'
        assert payload['initiative_context_id'] == 100
        assert payload['kpi_context_id'] == 200
