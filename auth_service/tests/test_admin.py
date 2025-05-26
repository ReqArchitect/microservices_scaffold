import pytest
from app.models import User, Tenant, UserActivity

def test_list_users(client, auth_headers):
    """Test listing users."""
    response = client.get('/v1/admin/users', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert 'total' in data
    assert 'pages' in data
    assert 'current_page' in data
    assert len(data['users']) > 0

def test_list_users_unauthorized(client):
    """Test listing users without authorization."""
    response = client.get('/v1/admin/users')
    assert response.status_code == 401

def test_get_user(client, auth_headers):
    """Test getting user details."""
    # First get a user ID
    user = User.query.filter_by(email='user@test.com').first()
    
    response = client.get(f'/v1/admin/users/{user.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'user@test.com'
    assert data['role'] == 'user'

def test_update_user(client, auth_headers):
    """Test updating user details."""
    user = User.query.filter_by(email='user@test.com').first()
    
    response = client.put(f'/v1/admin/users/{user.id}', headers=auth_headers, json={
        'full_name': 'Updated User',
        'is_active': False
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['full_name'] == 'Updated User'
    assert data['is_active'] is False
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        user_id=user.id,
        action='admin_update_user'
    ).first()
    assert activity is not None
    assert 'updated_fields' in activity.details
    assert 'full_name' in activity.details['updated_fields']
    assert 'is_active' in activity.details['updated_fields']

def test_delete_user(client, auth_headers):
    """Test deleting a user."""
    user = User.query.filter_by(email='user@test.com').first()
    
    response = client.delete(f'/v1/admin/users/{user.id}', headers=auth_headers)
    assert response.status_code == 200
    
    # Check if user was deleted
    deleted_user = User.query.get(user.id)
    assert deleted_user is None
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        action='admin_delete_user',
        details={'target_user_id': user.id}
    ).first()
    assert activity is not None

def test_list_tenants(client, auth_headers):
    """Test listing tenants."""
    response = client.get('/v1/admin/tenants', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'tenants' in data
    assert 'total' in data
    assert 'pages' in data
    assert 'current_page' in data
    assert len(data['tenants']) > 0

def test_create_tenant(client, auth_headers):
    """Test creating a new tenant."""
    response = client.post('/v1/admin/tenants', headers=auth_headers, json={
        'name': 'New Tenant',
        'is_active': True,
        'settings': {
            'max_users': 50,
            'allowed_roles': ['user']
        }
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'New Tenant'
    assert data['is_active'] is True
    assert 'settings' in data
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        action='create_tenant',
        details={'tenant_name': 'New Tenant'}
    ).first()
    assert activity is not None

def test_get_tenant(client, auth_headers):
    """Test getting tenant details."""
    tenant = Tenant.query.filter_by(name='Test Tenant').first()
    
    response = client.get(f'/v1/admin/tenants/{tenant.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Test Tenant'
    assert data['is_active'] is True

def test_update_tenant(client, auth_headers):
    """Test updating tenant details."""
    tenant = Tenant.query.filter_by(name='Test Tenant').first()
    
    response = client.put(f'/v1/admin/tenants/{tenant.id}', headers=auth_headers, json={
        'name': 'Updated Tenant',
        'settings': {
            'max_users': 200,
            'allowed_roles': ['user', 'tenant_admin']
        }
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Tenant'
    assert 'settings' in data
    assert data['settings']['max_users'] == 200
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        action='update_tenant',
        details={'tenant_id': tenant.id}
    ).first()
    assert activity is not None
    assert 'updated_fields' in activity.details
    assert 'name' in activity.details['updated_fields']
    assert 'settings' in activity.details['updated_fields']

def test_delete_tenant(client, auth_headers):
    """Test deleting a tenant."""
    tenant = Tenant.query.filter_by(name='Test Tenant').first()
    
    response = client.delete(f'/v1/admin/tenants/{tenant.id}', headers=auth_headers)
    assert response.status_code == 200
    
    # Check if tenant was deleted
    deleted_tenant = Tenant.query.get(tenant.id)
    assert deleted_tenant is None
    
    # Check if activity was logged
    activity = UserActivity.query.filter_by(
        action='delete_tenant',
        details={'tenant_id': tenant.id}
    ).first()
    assert activity is not None 