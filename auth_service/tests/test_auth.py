import pytest
from app.models import User, UserActivity

def test_register(client):
    """Test user registration."""
    response = client.post('/v1/auth/register', json={
        'email': 'newuser@test.com',
        'password': 'test123',
        'full_name': 'New User',
        'tenant_id': 1
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert data['user']['email'] == 'newuser@test.com'
    assert data['user']['full_name'] == 'New User'
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        user_id=data['user']['id'],
        action='register'
    ).first()
    assert activity is not None

def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    response = client.post('/v1/auth/register', json={
        'email': 'user@test.com',
        'password': 'test123',
        'full_name': 'Duplicate User',
        'tenant_id': 1
    })
    assert response.status_code == 409
    assert response.get_json()['error'] == 'User already exists'

def test_login(client):
    """Test user login."""
    response = client.post('/v1/auth/login', json={
        'email': 'user@test.com',
        'password': 'test123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    
    # Check if activity was logged
    user = User.query.filter_by(email='user@test.com').first()
    activity = UserActivity.query.filter_by(
        user_id=user.id,
        action='login'
    ).first()
    assert activity is not None

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/v1/auth/login', json={
        'email': 'user@test.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.get_json()['error'] == 'Invalid email or password'

def test_refresh_token(client, auth_headers):
    """Test token refresh."""
    response = client.post('/v1/auth/refresh', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    
    # Check if activity was logged
    user = User.query.filter_by(email='admin@test.com').first()
    activity = UserActivity.query.filter_by(
        user_id=user.id,
        action='token_refresh'
    ).first()
    assert activity is not None

def test_logout(client, auth_headers):
    """Test user logout."""
    response = client.post('/v1/auth/logout', headers=auth_headers)
    assert response.status_code == 200
    
    # Check if activity was logged
    user = User.query.filter_by(email='admin@test.com').first()
    activity = UserActivity.query.filter_by(
        user_id=user.id,
        action='logout'
    ).first()
    assert activity is not None

def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get('/v1/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'admin@test.com'
    assert data['role'] == 'vendor_admin'

def test_update_current_user(client, auth_headers):
    """Test updating current user information."""
    response = client.put('/v1/auth/me', headers=auth_headers, json={
        'full_name': 'Updated Admin',
        'preferences': {'theme': 'dark'}
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['full_name'] == 'Updated Admin'
    assert data['preferences']['theme'] == 'dark'
    
    # Check if activity was logged
    user = User.query.filter_by(email='admin@test.com').first()
    activity = UserActivity.query.filter_by(
        user_id=user.id,
        action='profile_update'
    ).first()
    assert activity is not None
    assert 'updated_fields' in activity.details
    assert 'full_name' in activity.details['updated_fields']
    assert 'preferences' in activity.details['updated_fields'] 