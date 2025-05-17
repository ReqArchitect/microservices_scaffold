import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app, db
from app.models import User, Role, Permission

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
    user = User(
        email='test@example.com',
        password='password123',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_admin(app):
    """Create test admin user."""
    role = Role(name='admin', description='Administrator')
    db.session.add(role)
    db.session.commit()
    
    user = User(
        email='admin@example.com',
        password='password123',
        is_active=True,
        role_id=role.id
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers."""
    response = client.post('/api/v1/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'} 