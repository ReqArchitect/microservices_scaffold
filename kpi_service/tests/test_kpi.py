import pytest
from datetime import date

@pytest.fixture
def sample_kpi(client, auth_headers):
    data = {
        'business_case_id': 1,
        'title': 'Test KPI',
        'description': 'A test KPI',
        'metric': 'Revenue',
        'target_value': 100.0,
        'current_value': 10.0,
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/kpis/', headers=auth_headers, json=data)
    return response.get_json()

def test_create_kpi(client, auth_headers):
    data = {
        'business_case_id': 1,
        'title': 'New KPI',
        'description': 'Description',
        'metric': 'Growth',
        'target_value': 200.0,
        'current_value': 20.0,
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/kpis/', headers=auth_headers, json=data)
    assert response.status_code == 201
    resp = response.get_json()
    assert resp['title'] == data['title']
    assert resp['tenant_id'] == '1'
    assert resp['owner_id'] == '1'
    assert 'id' in resp

def test_required_fields(client, auth_headers):
    response = client.post('/api/kpis/', headers=auth_headers, json={})
    assert response.status_code == 500 or response.status_code == 400

def test_list_kpis(client, auth_headers, sample_kpi):
    response = client.get('/api/kpis/', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()
    assert any(k['title'] == 'Test KPI' for k in items)

def test_get_kpi(client, auth_headers, sample_kpi):
    kpi_id = sample_kpi['id']
    response = client.get(f'/api/kpis/', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()
    assert any(k['id'] == kpi_id for k in items)

def test_update_kpi(client, auth_headers, sample_kpi):
    kpi_id = sample_kpi['id']
    update = {'title': 'Updated KPI', 'current_value': 99.0}
    response = client.put(f'/api/kpis/{kpi_id}', headers=auth_headers, json=update)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['title'] == 'Updated KPI'
    assert resp['current_value'] == 99.0

def test_delete_kpi(client, auth_headers, sample_kpi):
    kpi_id = sample_kpi['id']
    response = client.delete(f'/api/kpis/{kpi_id}', headers=auth_headers)
    assert response.status_code == 204
    # Should not be found after delete (list should not include it)
    response = client.get('/api/kpis/', headers=auth_headers)
    items = response.get_json()
    assert not any(k['id'] == kpi_id for k in items)

def test_tenant_isolation(client, auth_headers, another_auth_headers, sample_kpi):
    # User from another tenant should not see or access the KPI
    kpi_id = sample_kpi['id']
    response = client.put(f'/api/kpis/{kpi_id}', headers=another_auth_headers, json={'title': 'Hacked'})
    assert response.status_code == 404 or response.status_code == 403
    response = client.delete(f'/api/kpis/{kpi_id}', headers=another_auth_headers)
    assert response.status_code == 404 or response.status_code == 403
    response = client.get('/api/kpis/', headers=another_auth_headers)
    items = response.get_json()
    assert not any(k['id'] == kpi_id for k in items)

def test_list_is_tenant_scoped(client, auth_headers, another_auth_headers, sample_kpi):
    # Create a KPI for another tenant
    data = {
        'business_case_id': 1,
        'title': 'Other Tenant KPI',
        'metric': 'Metric',
        'target_value': 50.0
    }
    response = client.post('/api/kpis/', headers=another_auth_headers, json=data)
    assert response.status_code == 201
    # List for tenant 1
    response = client.get('/api/kpis/', headers=auth_headers)
    items = response.get_json()
    assert all(k['tenant_id'] == '1' for k in items)
    # List for tenant 2
    response = client.get('/api/kpis/', headers=another_auth_headers)
    items = response.get_json()
    assert all(k['tenant_id'] == '2' for k in items) 