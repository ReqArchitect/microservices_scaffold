import pytest
from flask import json
from app.auth import ROLES, get_user_permissions
import logging
from datetime import datetime

def test_admin_permissions():
    """Test that admin role has all permissions."""
    permissions = get_user_permissions('admin')
    assert permissions['initiatives'] == ['create', 'read', 'update', 'delete']
    assert permissions['users'] == ['create', 'read', 'update', 'delete']
    assert permissions['reports'] == ['create', 'read', 'update', 'delete']

def test_manager_permissions():
    """Test that manager role has appropriate permissions."""
    permissions = get_user_permissions('manager')
    assert permissions['initiatives'] == ['create', 'read', 'update']
    assert permissions['users'] == ['read']
    assert permissions['reports'] == ['create', 'read']

def test_user_permissions():
    """Test that regular user role has limited permissions."""
    permissions = get_user_permissions('user')
    assert permissions['initiatives'] == ['read']
    assert permissions['users'] == ['read']
    assert permissions['reports'] == ['read']

def test_create_initiative_permission(client, create_token, create_headers, test_tenant_id):
    """Test initiative creation with different roles."""
    # Test with admin role
    headers = create_headers(create_token(1, test_tenant_id, 'admin'), role='admin')
    response = client.post(
        '/api/initiatives',
        headers=headers,
        json={
            'title': 'Test Initiative',
            'description': 'Test Description',
            'strategic_objective': 'Test Objective'
        }
    )
    assert response.status_code == 201

    # Test with manager role
    headers = create_headers(create_token(1, test_tenant_id, 'manager'), role='manager')
    response = client.post(
        '/api/initiatives',
        headers=headers,
        json={
            'title': 'Test Initiative',
            'description': 'Test Description',
            'strategic_objective': 'Test Objective'
        }
    )
    assert response.status_code == 201

    # Test with user role (should be denied)
    headers = create_headers(create_token(1, test_tenant_id, 'user'), role='user')
    response = client.post(
        '/api/initiatives',
        headers=headers,
        json={
            'title': 'Test Initiative',
            'description': 'Test Description',
            'strategic_objective': 'Test Objective'
        }
    )
    assert response.status_code == 403

def test_read_initiative_permission(client, auth_headers, sample_initiative):
    """Test initiative reading with different roles."""
    # Test with admin role
    headers = auth_headers.copy()
    headers['X-User-Role'] = 'admin'
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 200

    # Test with manager role
    headers['X-User-Role'] = 'manager'
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 200

    # Test with user role
    headers['X-User-Role'] = 'user'
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 200

def test_update_initiative_permission(client, create_token, create_headers, sample_initiative, test_tenant_id):
    """Test initiative update with different roles."""
    # Test with admin role
    headers = create_headers(create_token(1, test_tenant_id, 'admin'), role='admin')
    response = client.put(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers,
        json={'title': 'Updated Title'}
    )
    assert response.status_code == 200

    # Test with manager role
    headers = create_headers(create_token(1, test_tenant_id, 'manager'), role='manager')
    response = client.put(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers,
        json={'title': 'Updated Title 2'}
    )
    assert response.status_code == 200

    # Test with user role
    headers = create_headers(create_token(1, test_tenant_id, 'user'), role='user')
    response = client.put(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers,
        json={'title': 'Updated Title 3'}
    )
    assert response.status_code == 403

def test_delete_initiative_permission(client, create_token, create_headers, sample_initiative, test_tenant_id):
    """Test initiative deletion with different roles."""
    # Test with admin role
    headers = create_headers(create_token(1, test_tenant_id, 'admin'), role='admin')
    response = client.delete(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 204

    # Test with manager role
    headers = create_headers(create_token(1, test_tenant_id, 'manager'), role='manager')
    response = client.delete(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 403

    # Test with user role
    headers = create_headers(create_token(1, test_tenant_id, 'user'), role='user')
    response = client.delete(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 403

def test_tenant_access_control(client, create_token, create_headers, sample_initiative, test_tenant_id):
    """Test that users can only access initiatives within their tenant."""
    # Test with same tenant
    headers = create_headers(create_token(1, test_tenant_id, 'admin'), role='admin')
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 200

    # Test with different tenant (simulate cross-tenant user)
    headers = create_headers('admin_token_tenant2', role='admin')
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 404

def test_audit_logging(client, auth_headers, sample_initiative, caplog):
    """Test that audit logs are created for write operations."""
    headers = auth_headers.copy()
    headers['X-User-Role'] = 'admin'
    user_id = 1  # From test_user_id fixture
    tenant_id = 1  # From test_tenant_id fixture

    # Configure caplog to capture logs
    caplog.set_level(logging.INFO)

    # Test create logging
    create_data = {
        'title': 'Test Initiative',
        'description': 'Test Description',
        'strategic_objective': 'Test Objective'
    }
    response = client.post(
        '/api/initiatives',
        headers=headers,
        json=create_data
    )
    assert response.status_code == 201
    initiative_id = response.json['initiative']['id']
    
    # Verify create log
    create_log = next(
        (log for log in caplog.records 
         if log.message.startswith('Auth Event: initiative_created')),
        None
    )
    assert create_log is not None
    assert f'User: {user_id}' in create_log.message
    assert f'Tenant: {tenant_id}' in create_log.message
    assert f'initiative_id: {initiative_id}' in create_log.message

    # Test update logging
    update_data = {'title': 'Updated Title'}
    response = client.put(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200
    
    # Verify update log
    update_log = next(
        (log for log in caplog.records 
         if log.message.startswith('Auth Event: initiative_updated')),
        None
    )
    assert update_log is not None
    assert f'User: {user_id}' in update_log.message
    assert f'Tenant: {tenant_id}' in update_log.message
    assert f'initiative_id: {sample_initiative.id}' in update_log.message
    assert 'changes' in update_log.message
    assert 'Updated Title' in update_log.message

    # Test delete logging
    response = client.delete(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 204
    
    # Verify delete log
    delete_log = next(
        (log for log in caplog.records
         if log.message.startswith('Auth Event: initiative_deleted')),
        None
    )
    if delete_log is None:
        print('Captured logs:')
        for log in caplog.records:
            print(log.message)
    assert delete_log is not None

def test_audit_logging_unauthorized_attempts(client, create_token, create_headers, sample_initiative, test_tenant_id, caplog):
    """Test that unauthorized access attempts are logged."""
    # Use user_token to simulate a regular user
    headers = create_headers(create_token(1, test_tenant_id, 'user'), role='user')
    caplog.set_level(logging.WARNING)

    # Test unauthorized update attempt
    response = client.put(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers,
        json={'title': 'Unauthorized Update'}
    )
    assert response.status_code == 403
    
    # Verify unauthorized access log
    unauthorized_log = next(
        (log for log in caplog.records 
         if 'Unauthorized action' in log.message),
        None
    )
    assert unauthorized_log is not None
    assert 'user' in unauthorized_log.message
    assert 'put' in unauthorized_log.message
    assert 'initiatives' in unauthorized_log.message

def test_audit_logging_cross_tenant_access(client, create_headers, sample_initiative, caplog):
    """Test that cross-tenant access attempts are logged."""
    # Use admin_token_tenant2 to simulate a user from a different tenant
    headers = create_headers('admin_token_tenant2', role='admin')
    caplog.set_level(logging.WARNING)

    # Test cross-tenant access attempt
    response = client.get(
        f'/api/initiatives/{sample_initiative.id}',
        headers=headers
    )
    assert response.status_code == 404
    
    # Verify cross-tenant access log
    cross_tenant_log = next(
        (log for log in caplog.records 
         if 'Cross-tenant access attempt' in log.message),
        None
    )
    assert cross_tenant_log is not None
    assert 'initiative_tenant' in cross_tenant_log.message
    assert str(sample_initiative.tenant_id) in cross_tenant_log.message 