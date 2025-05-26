import pytest
from app.models import ApplicationComponent, ApplicationService, ApplicationInterface, OutboxEvent
from app import db
import json

def test_application_component_context_ids(app, client):
    """Test that ApplicationComponent properly handles context IDs"""
    with app.app_context():
        component = ApplicationComponent(
            name="Test Component",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            capability_context_id=100
        )
        db.session.add(component)
        db.session.commit()
        
        # Verify context ID is stored
        assert component.capability_context_id == 100
        
        # Verify to_dict includes context ID
        data = component.to_dict()
        assert data['capability_context_id'] == 100

def test_application_service_context_ids(app, client):
    """Test that ApplicationService properly handles context IDs"""
    with app.app_context():
        service = ApplicationService(
            name="Test Service",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            capability_context_id=100
        )
        db.session.add(service)
        db.session.commit()
        
        # Verify context ID is stored
        assert service.capability_context_id == 100
        
        # Verify to_dict includes context ID
        data = service.to_dict()
        assert data['capability_context_id'] == 100

def test_application_interface_context_ids(app, client):
    """Test that ApplicationInterface properly handles context IDs"""
    with app.app_context():
        interface = ApplicationInterface(
            name="Test Interface",
            description="Test Description",
            user_id=1,
            tenant_id=1,
            course_of_action_context_id=200
        )
        db.session.add(interface)
        db.session.commit()
        
        # Verify context ID is stored
        assert interface.course_of_action_context_id == 200
        
        # Verify to_dict includes context ID
        data = interface.to_dict()
        assert data['course_of_action_context_id'] == 200
