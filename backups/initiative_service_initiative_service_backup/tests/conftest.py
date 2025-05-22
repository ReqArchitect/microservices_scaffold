import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade, downgrade
from sqlalchemy import text
import logging
import responses
from flask import current_app

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Initiative, InitiativeMember
from app.auth import ROLES, get_user_permissions

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app('testing')
    app.config.from_object('tests.config')
    print('App JWT_SECRET_KEY:', app.config['JWT_SECRET_KEY'])
    print('App AUTH_SERVICE_URL:', app.config.get('AUTH_SERVICE_URL'))
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(autouse=True)
def cleanup(app):
    """Cleanup fixture that runs after each test."""
    with app.app_context():
        yield
        # Delete all test initiatives
        try:
            Initiative.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
        finally:
            db.session.remove()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_tenant_id():
    """Return a test tenant ID."""
    return 1

@pytest.fixture
def test_user_id():
    """Return a test user ID."""
    return 1

@pytest.fixture
def test_token():
    return 'admin_token'

@pytest.fixture
def auth_headers(test_token):
    return {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json',
        'X-User-Role': 'admin'
    }

@pytest.fixture
def sample_initiative(app, test_tenant_id, test_user_id):
    """Create a sample initiative."""
    initiative = Initiative(
        title='Test Initiative',
        description='Test Description',
        strategic_objective='Test Objective',
        status='active',
        priority='high',
        progress=0,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        created_by=test_user_id,
        updated_by=test_user_id,
        tags='test,demo'
    )
    with app.app_context():
        db.session.add(initiative)
        db.session.commit()
        db.session.refresh(initiative)
    yield initiative
    with app.app_context():
        db.session.delete(initiative)
        db.session.commit()

@pytest.fixture
def multiple_initiatives(app, test_tenant_id, test_user_id):
    """Create multiple initiatives."""
    initiatives = []
    for i in range(5):
        initiative = Initiative(
            title=f'Test Initiative {i}',
            description=f'Test Description {i}',
            strategic_objective=f'Test Objective {i}',
            status='active',
            priority='high',
            progress=0,
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id,
            tags=f'test{i},demo{i}'
        )
        initiatives.append(initiative)
    
    with app.app_context():
        for initiative in initiatives:
            db.session.add(initiative)
        db.session.commit()
        for initiative in initiatives:
            db.session.refresh(initiative)
    
    yield initiatives
    
    with app.app_context():
        for initiative in initiatives:
            db.session.delete(initiative)
        db.session.commit()

@pytest.fixture
def create_token():
    def _create_token(user_id, tenant_id, role='admin'):
        if role == 'admin':
            return 'admin_token'
        elif role == 'manager':
            return 'manager_token'
        elif role == 'user':
            return 'user_token'
        else:
            return 'invalid_token'
    return _create_token

@pytest.fixture
def create_initiative(app, test_tenant_id, test_user_id):
    """Factory fixture to create initiatives."""
    def _create_initiative(**kwargs):
        initiative = Initiative(
            title=kwargs.get('title', 'Test Initiative'),
            description=kwargs.get('description', 'Test Description'),
            strategic_objective=kwargs.get('strategic_objective', 'Test Objective'),
            status=kwargs.get('status', 'active'),
            priority=kwargs.get('priority', 'high'),
            progress=kwargs.get('progress', 0),
            tenant_id=kwargs.get('tenant_id', test_tenant_id),
            owner_id=kwargs.get('owner_id', test_user_id),
            created_by=test_user_id,
            updated_by=test_user_id,
            tags=kwargs.get('tags', 'test,demo')
        )
        with app.app_context():
            db.session.add(initiative)
            db.session.commit()
            db.session.refresh(initiative)
        return initiative
    return _create_initiative

@pytest.fixture
def create_headers():
    """Factory fixture to create headers with different tokens."""
    def _create_headers(token, role='admin'):
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-User-Role': role
        }
    return _create_headers

@pytest.fixture
def test_initiative(app):
    """Create test initiative."""
    initiative = Initiative(
        name='Test Initiative',
        description='Test Description',
        created_by=1
    )
    db.session.add(initiative)
    db.session.commit()
    return initiative

@pytest.fixture
def test_member(app, test_initiative):
    """Create test initiative member."""
    member = InitiativeMember(
        initiative_id=test_initiative.id,
        user_id=1,
        role='admin'
    )
    db.session.add(member)
    db.session.commit()
    return member

@pytest.fixture(autouse=True)
def mock_auth_service_endpoints(app):
    """Mock auth service endpoints for all tests within app context."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock token validation
        def validate_token_callback(request):
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '')
            print(f"[MOCK] validate_token_callback called with token: {token}")
            if token == 'admin_token':
                return (200, {}, '{"id": 1, "email": "test@example.com", "role": "admin", "roles": ["admin"], "tenant_id": 1}')
            elif token == 'manager_token':
                return (200, {}, '{"id": 1, "email": "test@example.com", "role": "manager", "roles": ["manager"], "tenant_id": 1}')
            elif token == 'user_token':
                return (200, {}, '{"id": 1, "email": "test@example.com", "role": "user", "roles": ["user"], "tenant_id": 1}')
            elif token == 'admin_token_tenant2':
                return (200, {}, '{"id": 2, "email": "test2@example.com", "role": "admin", "roles": ["admin"], "tenant_id": 2}')
            elif token == 'admin_token_tenant99':
                return (200, {}, '{"id": 99, "email": "test99@example.com", "role": "admin", "roles": ["admin"], "tenant_id": 99}')
            elif token == 'invalid_role_token':
                return (200, {}, '{"id": 3, "email": "test3@example.com", "role": "invalid_role", "roles": ["invalid_role"], "tenant_id": 1}')
            else:
                return (401, {}, '{"error": "Invalid token"}')
        rsps.add_callback(
            responses.POST,
            f"{app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
            callback=validate_token_callback,
            content_type='application/json',
        )
        # Mock permissions check
        def get_permissions_callback(request):
            token = request.headers.get('Authorization', '')
            print(f"[MOCK] get_permissions_callback called with token: {token}")
            if 'admin_token' in token:
                return (200, {}, '["create_initiative", "update_initiative", "delete_initiative"]')
            elif 'manager_token' in token:
                return (200, {}, '["create_initiative", "update_initiative"]')
            elif 'user_token' in token:
                return (200, {}, '[]')
            else:
                return (200, {}, '[]')
        rsps.add_callback(
            responses.GET,
            f"{app.config['AUTH_SERVICE_URL']}/api/v1/auth/permissions",
            callback=get_permissions_callback,
            content_type='application/json',
        )
        def validate_access_callback(request):
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '')
            print(f"[MOCK] validate_access_callback called with token: {token}")
            if token in ['admin_token', 'manager_token', 'user_token']:
                return (200, {}, '{"has_access": true}')
            else:
                return (200, {}, '{"has_access": false}')
        rsps.add_callback(
            responses.POST,
            f"{app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate-access",
            callback=validate_access_callback,
            content_type='application/json',
        )
        yield rsps 