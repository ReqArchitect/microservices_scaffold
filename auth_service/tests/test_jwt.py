import pytest
from datetime import datetime, timedelta
from app.auth.jwt import (
    create_tokens,
    validate_token,
    get_user_permissions,
    has_permission,
    permission_required,
    role_required
)
from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity

def test_create_tokens():
    """Test token creation."""
    identity = {
        'id': 1,
        'tenant_id': 1,
        'role': 'user'
    }
    tokens = create_tokens(identity)
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens

def test_create_tokens_missing_fields():
    """Test token creation with missing required fields."""
    identity = {
        'id': 1,
        'role': 'user'
    }
    with pytest.raises(ValueError):
        create_tokens(identity)

def test_get_user_permissions():
    """Test getting user permissions."""
    # Test vendor admin permissions
    vendor_permissions = get_user_permissions('vendor_admin')
    assert 'initiatives' in vendor_permissions
    assert 'users' in vendor_permissions
    assert 'reports' in vendor_permissions
    assert 'create' in vendor_permissions['initiatives']
    assert 'delete' in vendor_permissions['initiatives']

    # Test tenant admin permissions
    tenant_permissions = get_user_permissions('tenant_admin')
    assert 'initiatives' in tenant_permissions
    assert 'users' in tenant_permissions
    assert 'reports' in tenant_permissions
    assert 'create' in tenant_permissions['initiatives']
    assert 'delete' not in tenant_permissions['initiatives']

    # Test regular user permissions
    user_permissions = get_user_permissions('user')
    assert 'initiatives' in user_permissions
    assert 'users' in user_permissions
    assert 'reports' in user_permissions
    assert 'read' in user_permissions['initiatives']
    assert 'create' not in user_permissions['initiatives']

def test_has_permission():
    """Test permission checking."""
    identity = {
        'id': 1,
        'tenant_id': 1,
        'role': 'vendor_admin'
    }
    
    # Test valid permissions
    assert has_permission(identity, 'initiatives', 'create')
    assert has_permission(identity, 'initiatives', 'delete')
    assert has_permission(identity, 'users', 'create')
    
    # Test invalid permissions
    assert not has_permission(identity, 'initiatives', 'invalid_action')
    assert not has_permission(None, 'initiatives', 'create')
    assert not has_permission({}, 'initiatives', 'create')

def test_permission_required_decorator(client, auth_headers):
    """Test permission required decorator."""
    @permission_required('initiatives', 'create')
    def test_endpoint():
        return jsonify({'message': 'success'})
    
    # Test with valid permissions
    response = client.get('/test', headers=auth_headers)
    assert response.status_code == 200
    
    # Test with invalid permissions
    response = client.get('/test')
    assert response.status_code == 401

def test_role_required_decorator(client, auth_headers):
    """Test role required decorator."""
    @role_required('vendor_admin')
    def test_endpoint():
        return jsonify({'message': 'success'})
    
    # Test with valid role
    response = client.get('/test', headers=auth_headers)
    assert response.status_code == 200
    
    # Test with invalid role
    response = client.get('/test')
    assert response.status_code == 401

def test_token_validation(client, auth_headers):
    """Test token validation."""
    # Test valid token
    response = client.get('/v1/auth/me', headers=auth_headers)
    assert response.status_code == 200
    
    # Test invalid token
    response = client.get('/v1/auth/me', headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    
    # Test missing token
    response = client.get('/v1/auth/me')
    assert response.status_code == 401

def test_token_expiration(client, auth_headers):
    """Test token expiration."""
    # Create an expired token
    expired_token = create_access_token(
        identity={'id': 1, 'tenant_id': 1, 'role': 'user'},
        expires_delta=timedelta(seconds=0)
    )
    
    # Test expired token
    response = client.get('/v1/auth/me', headers={'Authorization': f'Bearer {expired_token}'})
    assert response.status_code == 401 