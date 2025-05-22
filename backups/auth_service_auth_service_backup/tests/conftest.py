import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app, db
from app.models import User, Role, Permission, Tenant

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user."""
    # Create a dummy tenant if needed
    tenant = Tenant(name='Test Tenant', is_active=True)
    db.session.add(tenant)
    db.session.commit()
    user = User(
        email='test@example.com',
        full_name='Test User',
        role='user',
        tenant_id=tenant.id,
        is_active=True
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_admin(app, client):
    """Create test admin user via API."""
    # Create a tenant first
    with app.app_context():
        tenant = Tenant(name='Admin Tenant', is_active=True)
        db.session.add(tenant)
        db.session.commit()
        tenant_id = tenant.id
    # Register the admin user via the API
    response = client.post('/api/v1/auth/register', json={
        'email': 'admin@example.com',
        'password': 'password123',
        'full_name': 'Admin User',
        'role': 'tenant_admin',
        'tenant_id': tenant_id
    })
    assert response.status_code == 201, response.get_json()
    # Fetch the user from the DB
    with app.app_context():
        user = User.query.filter_by(email='admin@example.com', tenant_id=tenant_id).first()
        return user

@pytest.fixture
def auth_headers(client, test_admin):
    """Get auth headers for admin user."""
    response = client.post('/api/v1/auth/login', json={
        'email': test_admin.email,
        'password': 'password123',
        'tenant_id': test_admin.tenant_id
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'} 