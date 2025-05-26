import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from strategy_service.app import create_app, db
from strategy_service.config import TestConfig
from flask_jwt_extended import create_access_token
import pytest
import json

@pytest.fixture
def client():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_header():
    app = create_app(TestConfig)
    with app.app_context():
        token = create_access_token(
            identity="1",  # user_id as string
            additional_claims={"tenant_id": 1}
        )
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def verify_event_emission(db_session, event_type, aggregate_type, aggregate_id=None):
    """Helper to verify an event was emitted"""
    from strategy_service.app.models import OutboxEvent
    
    query = OutboxEvent.query.filter_by(
        event_type=event_type,
        aggregate_type=aggregate_type
    )
    
    if aggregate_id:
        query = query.filter_by(aggregate_id=str(aggregate_id))
    
    event = query.first()
    assert event is not None
    return json.loads(event.payload)

def verify_context_propagation(payload, context_id_field, expected_value):
    """Helper to verify context IDs are propagated"""
    assert payload.get(context_id_field) == expected_value
