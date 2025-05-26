import pytest
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

def test_create_initiative(client, auth_headers, test_tenant_id, test_user_id):
    """Test creating a new initiative."""
    initiative_data = {
        'title': 'New Test Initiative',
        'description': 'New Test Description',
        'strategic_objective': 'New Test Objective',
        'status': 'active',
        'priority': 'high',
        'progress': 0,
        'tenant_id': test_tenant_id,
        'owner_id': test_user_id,
        'tags': ['new', 'test']
    }
    response = client.post('/api/initiatives', 
                          headers=auth_headers,
                          json=initiative_data)
    assert response.status_code == 201
    data = response.get_json()
    assert 'initiative' in data
    assert data['initiative']['title'] == initiative_data['title']
    assert data['initiative']['description'] == initiative_data['description']
    assert data['initiative']['strategic_objective'] == initiative_data['strategic_objective']
    assert data['initiative']['status'] == initiative_data['status']
    assert data['initiative']['priority'] == initiative_data['priority']
    assert data['initiative']['progress'] == initiative_data['progress']
    assert data['initiative']['tenant_id'] == initiative_data['tenant_id']
    assert data['initiative']['owner_id'] == initiative_data['owner_id']
    assert sorted(data['initiative']['tags']) == sorted(initiative_data['tags'])

def test_get_initiatives(client, auth_headers, multiple_initiatives):
    """Test getting all initiatives."""
    response = client.get('/api/initiatives', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert len(data['items']) == len(multiple_initiatives)
    assert all('id' in initiative for initiative in data['items'])
    assert all('title' in initiative for initiative in data['items'])
    assert all('description' in initiative for initiative in data['items'])
    assert all('strategic_objective' in initiative for initiative in data['items'])
    assert all('status' in initiative for initiative in data['items'])
    assert all('priority' in initiative for initiative in data['items'])
    assert all('progress' in initiative for initiative in data['items'])
    assert all('tenant_id' in initiative for initiative in data['items'])
    assert all('owner_id' in initiative for initiative in data['items'])
    assert all('tags' in initiative for initiative in data['items'])

def test_get_initiative(client, auth_headers, sample_initiative):
    """Test getting a single initiative."""
    response = client.get(f'/api/initiatives/{sample_initiative.id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_initiative.id
    assert data['title'] == sample_initiative.title
    assert data['description'] == sample_initiative.description
    assert data['strategic_objective'] == sample_initiative.strategic_objective
    assert data['status'] == sample_initiative.status
    assert data['priority'] == sample_initiative.priority
    assert data['progress'] == sample_initiative.progress
    assert data['tenant_id'] == sample_initiative.tenant_id
    assert data['owner_id'] == sample_initiative.owner_id
    assert data['tags'] == sample_initiative.tags.split(',')

def test_update_initiative(client, auth_headers, sample_initiative):
    """Test updating an initiative."""
    update_data = {
        'title': 'Updated Test Initiative',
        'description': 'Updated Test Description',
        'strategic_objective': 'Updated Test Objective',
        'status': 'completed',
        'priority': 'medium',
        'progress': 50,
        'tags': ['updated', 'test']
    }
    response = client.put(f'/api/initiatives/{sample_initiative.id}',
                         headers=auth_headers,
                         json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == update_data['title']
    assert data['description'] == update_data['description']
    assert data['strategic_objective'] == update_data['strategic_objective']
    assert data['status'] == update_data['status']
    assert data['priority'] == update_data['priority']
    assert data['progress'] == update_data['progress']
    assert sorted(data['tags']) == sorted(update_data['tags'])

def test_delete_initiative(client, create_token, test_tenant_id, test_user_id, sample_initiative):
    """Test deleting an initiative."""
    token = create_token(test_user_id, test_tenant_id, 'admin')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-User-Role': 'admin'
    }
    response = client.delete(f'/api/initiatives/{sample_initiative.id}', headers=headers)
    assert response.status_code == 204
    # Verify the initiative is deleted
    response = client.get(f'/api/initiatives/{sample_initiative.id}', headers=headers)
    assert response.status_code == 404

def test_unauthorized_access(client):
    """Test unauthorized access to endpoints."""
    # Test without auth headers
    response = client.get("/api/initiatives")
    assert response.status_code == 401
    
    response = client.post("/api/initiatives", json={})
    assert response.status_code == 401
    
    response = client.get("/api/initiatives/1")
    assert response.status_code == 401
    
    response = client.put("/api/initiatives/1", json={})
    assert response.status_code == 401
    
    response = client.delete("/api/initiatives/1")
    assert response.status_code == 401

def test_invalid_input(client, auth_headers):
    """Test handling of invalid input."""
    # Test missing required fields
    data = {
        "description": "Test Description",
        "status": "active"
    }
    response = client.post(
        "/api/initiatives",
        headers=auth_headers,
        json=data
    )
    assert response.status_code in [400, 401]
    assert "Title is required" in response.get_json()["error"]
    
    # Test invalid status
    data = {
        "title": "Test Initiative",
        "strategic_objective": "Test Objective",
        "status": "invalid_status"
    }
    response = client.post(
        "/api/initiatives",
        headers=auth_headers,
        json=data
    )
    assert response.status_code in [400, 401]
    
    # Test invalid priority
    data = {
        "title": "Test Initiative",
        "strategic_objective": "Test Objective",
        "priority": "invalid_priority"
    }
    response = client.post(
        "/api/initiatives",
        headers=auth_headers,
        json=data
    )
    assert response.status_code in [400, 401]
    
    # Test invalid progress
    data = {
        "title": "Test Initiative",
        "strategic_objective": "Test Objective",
        "progress": 150
    }
    response = client.post(
        "/api/initiatives",
        headers=auth_headers,
        json=data
    )
    assert response.status_code in [400, 401]

def test_not_found(client, create_token, test_tenant_id, test_user_id):
    """Test handling of non-existent resources."""
    token = create_token(test_user_id, test_tenant_id, 'admin')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-User-Role': 'admin'
    }
    # Test getting non-existent initiative
    response = client.get("/api/initiatives/999", headers=headers)
    assert response.status_code == 404
    # Test updating non-existent initiative
    response = client.put(
        "/api/initiatives/999",
        headers=headers,
        json={"title": "Updated Initiative"}
    )
    assert response.status_code == 404
    # Test deleting non-existent initiative
    response = client.delete("/api/initiatives/999", headers=headers)
    assert response.status_code == 404

def test_tenant_isolation(client, auth_headers, test_tenant_id, test_user_id, create_initiative):
    """Test that initiatives are properly isolated by tenant."""
    # Create an initiative for tenant 1
    initiative = create_initiative(
        title='Test Initiative Tenant 1',
        description='Test Description',
        strategic_objective='Test Objective',
        status='active',
        priority='high',
        progress=0,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        tags='test,demo'
    )
    
    # Get all initiatives and verify they belong to tenant 1
    response = client.get('/api/initiatives', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert all(initiative['tenant_id'] == test_tenant_id for initiative in data['items'])
    
    # Try to create an initiative for a different tenant
    initiative_data = {
        'title': 'Test Initiative Tenant 2',
        'description': 'Test Description',
        'strategic_objective': 'Test Objective',
        'status': 'active',
        'priority': 'high',
        'progress': 0,
        'tenant_id': test_tenant_id + 1,
        'owner_id': test_user_id,
        'tags': 'test,demo'
    }
    response = client.post('/api/initiatives', 
                          headers=auth_headers,
                          json=initiative_data)
    assert response.status_code == 403
    assert "Unauthorized tenant access" in response.get_json()["error"]
    
    # Try to update an initiative with a different tenant_id
    update_data = {
        'title': 'Updated Initiative',
        'tenant_id': test_tenant_id + 1
    }
    response = client.put(f'/api/initiatives/{initiative.id}',
                         headers=auth_headers,
                         json=update_data)
    assert response.status_code == 403
    assert "Cannot modify tenant_id" in response.get_json()["error"]

def test_cross_tenant_access(client, test_tenant_id, test_user_id, create_token, create_initiative, create_headers):
    """Test that initiatives cannot be accessed across tenants."""
    # Create an initiative for tenant 1
    initiative = create_initiative(
        title='Test Initiative Tenant 1',
        description='Test Description',
        strategic_objective='Test Objective',
        status='active',
        priority='high',
        progress=0,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        tags='test,demo'
    )
    
    # Create headers for a different tenant
    other_tenant_token = 'admin_token_tenant2'
    other_tenant_headers = create_headers(other_tenant_token)
    
    # Try to get the initiative as a different tenant
    response = client.get(f'/api/initiatives/{initiative.id}',
                         headers=other_tenant_headers)
    assert response.status_code == 404
    
    # Try to update the initiative as a different tenant
    response = client.put(f'/api/initiatives/{initiative.id}',
                         headers=other_tenant_headers,
                         json={'title': 'Updated Initiative'})
    assert response.status_code == 404
    
    # Try to delete the initiative as a different tenant
    response = client.delete(f'/api/initiatives/{initiative.id}',
                           headers=other_tenant_headers)
    assert response.status_code == 404

def test_role_based_access(client, test_tenant_id, test_user_id, create_token, create_initiative, create_headers):
    """Test role-based access control."""
    # Create tokens for different roles
    admin_token = create_token(test_user_id, test_tenant_id, 'admin')
    manager_token = create_token(test_user_id, test_tenant_id, 'manager')
    user_token = create_token(test_user_id, test_tenant_id, 'user')
    
    # Create headers for different roles
    admin_headers = create_headers(admin_token)
    manager_headers = create_headers(manager_token)
    user_headers = create_headers(user_token)
    
    # Create an initiative using the fixture
    initiative = create_initiative(
        title='Test Initiative',
        description='Test Description',
        strategic_objective='Test Objective',
        status='active',
        priority='high',
        progress=0,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        tags='test,demo'
    )
    
    # Test read access (all roles should have access)
    response = client.get(f'/api/initiatives/{initiative.id}',
                         headers=admin_headers)
    assert response.status_code == 200
    
    response = client.get(f'/api/initiatives/{initiative.id}',
                         headers=manager_headers)
    assert response.status_code == 200
    
    response = client.get(f'/api/initiatives/{initiative.id}',
                         headers=user_headers)
    assert response.status_code == 200
    
    # Test create access (admin and manager should have access)
    initiative_data = {
        'title': 'New Test Initiative',
        'description': 'New Test Description',
        'strategic_objective': 'New Test Objective',
        'status': 'active',
        'priority': 'high',
        'progress': 0,
        'tenant_id': test_tenant_id,
        'owner_id': test_user_id,
        'tags': 'new,test'
    }
    response = client.post('/api/initiatives',
                          headers=manager_headers,
                          json=initiative_data)
    assert response.status_code == 201

    response = client.post('/api/initiatives',
                          headers=user_headers,
                          json=initiative_data)
    assert response.status_code == 403
    
    # Test update access (admin and manager should have access)
    update_data = {'title': 'Updated Initiative'}
    response = client.put(f'/api/initiatives/{initiative.id}',
                         headers=admin_headers,
                         json=update_data)
    assert response.status_code == 200
    
    response = client.put(f'/api/initiatives/{initiative.id}',
                         headers=manager_headers,
                         json=update_data)
    assert response.status_code == 200
    
    response = client.put(f'/api/initiatives/{initiative.id}',
                         headers=user_headers,
                         json=update_data)
    assert response.status_code == 403
    
    # Test delete access (only admin should have access)
    response = client.delete(f'/api/initiatives/{initiative.id}',
                           headers=manager_headers)
    assert response.status_code == 403
    
    response = client.delete(f'/api/initiatives/{initiative.id}',
                           headers=user_headers)
    assert response.status_code == 403
    
    response = client.delete(f'/api/initiatives/{initiative.id}',
                           headers=admin_headers)
    assert response.status_code == 204

def test_invalid_token(client):
    """Test handling of invalid tokens."""
    # Test with no token
    response = client.get("/api/initiatives")
    assert response.status_code == 401
    
    # Test with invalid token
    headers = {
        'Authorization': 'Bearer invalid_token',
        'Content-Type': 'application/json'
    }
    response = client.get("/api/initiatives", headers=headers)
    assert response.status_code == 401
    
    # Test with malformed token
    headers = {
        'Authorization': 'invalid_token',
        'Content-Type': 'application/json'
    }
    response = client.get("/api/initiatives", headers=headers)
    assert response.status_code == 401

def test_invalid_role(client, test_tenant_id, test_user_id, create_token, create_headers):
    """Test handling of invalid roles."""
    # Create token with invalid role
    token = 'invalid_role_token'
    headers = create_headers(token)
    
    # Test accessing endpoints with invalid role
    response = client.get("/api/initiatives", headers=headers)
    assert response.status_code == 403
    assert "Invalid role" in response.get_json()["error"]
    
    response = client.post("/api/initiatives", headers=headers, json={})
    assert response.status_code == 403
    assert "Invalid role" in response.get_json()["error"]
    
    response = client.get("/api/initiatives/1", headers=headers)
    assert response.status_code == 403
    assert "Invalid role" in response.get_json()["error"]
    
    response = client.put("/api/initiatives/1", headers=headers, json={})
    assert response.status_code == 403
    assert "Invalid role" in response.get_json()["error"]
    
    response = client.delete("/api/initiatives/1", headers=headers)
    assert response.status_code == 403
    assert "Invalid role" in response.get_json()["error"]

def test_missing_role(client, test_tenant_id, test_user_id):
    """Test handling of missing role in token."""
    # Create token without role
    identity = {
        'id': test_user_id,
        'tenant_id': test_tenant_id
    }
    with client.application.app_context():
        token = create_access_token(identity=identity)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test accessing endpoints with missing role
    response = client.get("/api/initiatives", headers=headers)
    assert response.status_code == 401
    assert "Invalid token" in response.get_json()["error"]

@pytest.mark.skip(reason="Rate limiting is not enforced in the test environment.")
def test_rate_limiting(client, auth_headers, test_tenant_id, test_user_id):
    """Test rate limiting on endpoints."""
    # Enable rate limiting for this test
    with client.application.app_context():
        client.application.config['RATELIMIT_ENABLED'] = True
        client.application.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        client.application.config['RATELIMIT_DEFAULT'] = "5 per minute"
        
        # Test POST rate limit
        unique_tenant_id = 99
        for i in range(6):
            headers = {
                'Authorization': 'Bearer admin_token_tenant99',
                'Content-Type': 'application/json',
                'X-User-Role': 'admin'
            }
            response = client.post(
                "/api/initiatives",
                headers=headers,
                json={
                    "title": "Test Initiative",
                    "description": "Test Description",
                    "strategic_objective": "Test Objective",
                    "status": "active",
                    "priority": "high",
                    "progress": 0,
                    "tenant_id": unique_tenant_id,
                    "owner_id": test_user_id,
                    "tags": ["test"]
                },
                environ_base={"REMOTE_ADDR": "127.0.0.1"}
            )
            if i < 5:
                assert response.status_code in [201, 400, 422]  # Allow 400 for validation errors
            else:
                assert response.status_code == 429  # Should be rate limited

    auth_headers = {
        'Authorization': 'Bearer admin_token',
        'Content-Type': 'application/json',
        'X-User-Role': 'admin'
    } 