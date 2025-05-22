import pytest
from datetime import date

@pytest.fixture
def sample_initiative(client, auth_headers):
    data = {
        'title': 'Test Initiative',
        'description': 'A test initiative',
        'strategic_objective': 'Growth',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'status': 'draft',
        'priority': 'medium',
        'progress': 0,
        'tags': ['test', 'growth']
    }
    response = client.post('/api/initiatives', headers=auth_headers, json=data)
    return response.get_json()['initiative']

def test_create_initiative(client, auth_headers):
    data = {
        'title': 'New Initiative',
        'description': 'Description',
        'strategic_objective': 'Objective',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'status': 'active',
        'priority': 'high',
        'progress': 10,
        'tags': ['alpha', 'beta']
    }
    response = client.post('/api/initiatives', headers=auth_headers, json=data)
    assert response.status_code == 201
    resp = response.get_json()['initiative']
    assert resp['title'] == data['title']
    assert resp['tenant_id'] == 1
    assert resp['owner_id'] == 1
    assert 'id' in resp

def test_required_fields(client, auth_headers):
    response = client.post('/api/initiatives', headers=auth_headers, json={})
    assert response.status_code == 400
    assert 'Title is required' in response.get_json()['error']

def test_list_initiatives(client, auth_headers, sample_initiative):
    response = client.get('/api/initiatives', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()['items']
    assert any(i['title'] == 'Test Initiative' for i in items)

def test_get_initiative(client, auth_headers, sample_initiative):
    initiative_id = sample_initiative['id']
    response = client.get(f'/api/initiatives/{initiative_id}', headers=auth_headers)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['id'] == initiative_id
    assert resp['title'] == 'Test Initiative'

def test_update_initiative(client, auth_headers, sample_initiative):
    initiative_id = sample_initiative['id']
    update = {'title': 'Updated Title', 'progress': 50}
    response = client.put(f'/api/initiatives/{initiative_id}', headers=auth_headers, json=update)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['title'] == 'Updated Title'
    assert resp['progress'] == 50

def test_delete_initiative(client, auth_headers, sample_initiative):
    initiative_id = sample_initiative['id']
    response = client.delete(f'/api/initiatives/{initiative_id}', headers=auth_headers)
    assert response.status_code == 204
    # Should not be found after delete
    response = client.get(f'/api/initiatives/{initiative_id}', headers=auth_headers)
    assert response.status_code == 404

def test_tenant_isolation(client, auth_headers, another_auth_headers, sample_initiative):
    # User from another tenant should not see or access the initiative
    initiative_id = sample_initiative['id']
    response = client.get(f'/api/initiatives/{initiative_id}', headers=another_auth_headers)
    assert response.status_code == 404
    response = client.put(f'/api/initiatives/{initiative_id}', headers=another_auth_headers, json={'title': 'Hacked'})
    assert response.status_code == 404
    response = client.delete(f'/api/initiatives/{initiative_id}', headers=another_auth_headers)
    assert response.status_code == 404

def test_list_is_tenant_scoped(client, auth_headers, another_auth_headers, sample_initiative):
    # Create an initiative for another tenant
    data = {'title': 'Other Tenant Initiative', 'description': 'desc', 'strategic_objective': 'obj'}
    response = client.post('/api/initiatives', headers=another_auth_headers, json=data)
    assert response.status_code == 201
    # List for tenant 1
    response = client.get('/api/initiatives', headers=auth_headers)
    items = response.get_json()['items']
    assert all(i['tenant_id'] == 1 for i in items)
    # List for tenant 2
    response = client.get('/api/initiatives', headers=another_auth_headers)
    items = response.get_json()['items']
    assert all(i['tenant_id'] == 2 for i in items)

def test_add_initiative_member(client, auth_headers, sample_initiative):
    initiative_id = sample_initiative['id']
    data = {'user_id': 2, 'role': 'member'}
    response = client.post(f'/api/initiatives/{initiative_id}/members', headers=auth_headers, json=data)
    assert response.status_code == 201
    resp = response.get_json()
    assert resp['user_id'] == 2
    assert resp['role'] == 'member' 