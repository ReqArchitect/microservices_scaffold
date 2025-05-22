import pytest
from datetime import date

@pytest.fixture
def sample_canvas(client, auth_headers):
    data = {
        'title': 'Test Canvas',
        'description': 'A test canvas',
        'justification': 'Testing',
        'expected_benefits': 'Benefits',
        'risk_assessment': 'Low',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/canvas', headers=auth_headers, json=data)
    return response.get_json()['canvas']

def test_create_canvas(client, auth_headers):
    data = {
        'title': 'New Canvas',
        'description': 'Description',
        'justification': 'Justification',
        'expected_benefits': 'Benefits',
        'risk_assessment': 'Risk',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/canvas', headers=auth_headers, json=data)
    assert response.status_code == 201
    resp = response.get_json()['canvas']
    assert resp['title'] == data['title']
    assert resp['user_id'] == 1
    assert resp['tenant_id'] == 1

def test_required_fields_canvas(client, auth_headers):
    response = client.post('/api/canvas', headers=auth_headers, json={})
    assert response.status_code == 400
    assert 'Title is required' in response.get_json()['error']

def test_list_canvases(client, auth_headers, sample_canvas):
    response = client.get('/api/canvas', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()['items']
    assert any(c['title'] == 'Test Canvas' for c in items)

def test_get_canvas(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    response = client.get(f'/api/canvas/{canvas_id}', headers=auth_headers)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['id'] == canvas_id
    assert resp['title'] == 'Test Canvas'

def test_update_canvas(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    update = {'title': 'Updated Canvas', 'risk_assessment': 'Medium'}
    response = client.put(f'/api/canvas/{canvas_id}', headers=auth_headers, json=update)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['title'] == 'Updated Canvas'
    assert resp['risk_assessment'] == 'Medium'

def test_delete_canvas(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    response = client.delete(f'/api/canvas/{canvas_id}', headers=auth_headers)
    assert response.status_code == 204
    # Should not be found after delete
    response = client.get(f'/api/canvas/{canvas_id}', headers=auth_headers)
    assert response.status_code == 404

def test_tenant_isolation_canvas(client, auth_headers, another_auth_headers, sample_canvas):
    # User from another tenant should not see or access the canvas
    canvas_id = sample_canvas['id']
    response = client.get(f'/api/canvas/{canvas_id}', headers=another_auth_headers)
    assert response.status_code == 404
    response = client.put(f'/api/canvas/{canvas_id}', headers=another_auth_headers, json={'title': 'Hacked'})
    assert response.status_code == 404
    response = client.delete(f'/api/canvas/{canvas_id}', headers=another_auth_headers)
    assert response.status_code == 404

def test_list_is_tenant_scoped_canvas(client, auth_headers, another_auth_headers, sample_canvas):
    # Create a canvas for another tenant
    data = {'title': 'Other Tenant Canvas'}
    response = client.post('/api/canvas', headers=another_auth_headers, json=data)
    assert response.status_code == 201
    # List for tenant 1
    response = client.get('/api/canvas', headers=auth_headers)
    items = response.get_json()['items']
    assert all(c['tenant_id'] == 1 for c in items)
    # List for tenant 2
    response = client.get('/api/canvas', headers=another_auth_headers)
    items = response.get_json()['items']
    assert all(c['tenant_id'] == 2 for c in items)

# --- Component CRUD tests (example for KeyPartner, repeat for others) ---
def test_create_key_partner(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    data = {'name': 'Partner 1', 'description': 'Desc', 'partner_type': 'Supplier'}
    response = client.post(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers, json=data)
    assert response.status_code == 201
    partner = response.get_json()['key_partner']
    assert partner['name'] == 'Partner 1'
    assert partner['canvas_id'] == canvas_id

def test_list_key_partners(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    data = {'name': 'Partner 2'}
    client.post(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers, json=data)
    response = client.get(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()['items']
    assert any(p['name'] == 'Partner 2' for p in items)

def test_update_key_partner(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    data = {'name': 'Partner 3'}
    resp = client.post(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers, json=data)
    partner_id = resp.get_json()['key_partner']['id']
    update = {'name': 'Partner 3 Updated'}
    response = client.put(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=auth_headers, json=update)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Partner 3 Updated'

def test_delete_key_partner(client, auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    data = {'name': 'Partner 4'}
    resp = client.post(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers, json=data)
    partner_id = resp.get_json()['key_partner']['id']
    response = client.delete(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=auth_headers)
    assert response.status_code == 204
    # Should not be found after delete
    response = client.get(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=auth_headers)
    assert response.status_code == 404

def test_tenant_isolation_key_partner(client, auth_headers, another_auth_headers, sample_canvas):
    canvas_id = sample_canvas['id']
    data = {'name': 'Partner 5'}
    resp = client.post(f'/api/canvas/{canvas_id}/key_partner', headers=auth_headers, json=data)
    partner_id = resp.get_json()['key_partner']['id']
    # Other tenant should not access
    response = client.get(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=another_auth_headers)
    assert response.status_code == 404
    response = client.put(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=another_auth_headers, json={'name': 'Hacked'})
    assert response.status_code == 404
    response = client.delete(f'/api/canvas/{canvas_id}/key_partner/{partner_id}', headers=another_auth_headers)
    assert response.status_code == 404
# Repeat similar tests for all other component models (KeyActivity, KeyResource, etc.) 