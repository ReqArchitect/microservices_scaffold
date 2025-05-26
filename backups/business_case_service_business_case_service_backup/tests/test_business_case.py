import pytest
from datetime import date

# Fixtures are now provided by conftest.py

@pytest.fixture
def sample_business_case(client, auth_headers):
    data = {
        'title': 'Test Business Case',
        'description': 'A test case',
        'justification': 'Because testing',
        'expected_benefits': 'Quality',
        'risk_assessment': 'Low',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/business_cases', headers=auth_headers, json=data)
    return response.get_json()['business_case']

# All tests below use auth_headers and another_auth_headers

def test_create_business_case(client, auth_headers):
    data = {
        'title': 'New Business Case',
        'description': 'Description',
        'justification': 'Justification',
        'expected_benefits': 'Benefits',
        'risk_assessment': 'Risk',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
    response = client.post('/api/business_cases', headers=auth_headers, json=data)
    assert response.status_code == 201
    resp = response.get_json()['business_case']
    assert resp['title'] == data['title']
    assert resp['user_id'] == 1
    assert resp['tenant_id'] == 1

def test_required_fields(client, auth_headers):
    response = client.post('/api/business_cases', headers=auth_headers, json={})
    assert response.status_code == 400
    assert 'Title is required' in response.get_json()['error']

def test_list_business_cases(client, auth_headers, sample_business_case):
    response = client.get('/api/business_cases', headers=auth_headers)
    assert response.status_code == 200
    items = response.get_json()['items']
    assert any(bc['title'] == 'Test Business Case' for bc in items)

def test_get_business_case(client, auth_headers, sample_business_case):
    case_id = sample_business_case['id']
    response = client.get(f'/api/business_cases/{case_id}', headers=auth_headers)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['id'] == case_id
    assert resp['title'] == 'Test Business Case'

def test_update_business_case(client, auth_headers, sample_business_case):
    case_id = sample_business_case['id']
    update = {'title': 'Updated Title', 'risk_assessment': 'Medium'}
    response = client.put(f'/api/business_cases/{case_id}', headers=auth_headers, json=update)
    assert response.status_code == 200
    resp = response.get_json()
    assert resp['title'] == 'Updated Title'
    assert resp['risk_assessment'] == 'Medium'

def test_delete_business_case(client, auth_headers, sample_business_case):
    case_id = sample_business_case['id']
    response = client.delete(f'/api/business_cases/{case_id}', headers=auth_headers)
    assert response.status_code == 204
    # Should not be found after delete
    response = client.get(f'/api/business_cases/{case_id}', headers=auth_headers)
    assert response.status_code == 404

def test_tenant_isolation(client, auth_headers, another_auth_headers, sample_business_case):
    # User from another tenant should not see or access the business case
    case_id = sample_business_case['id']
    response = client.get(f'/api/business_cases/{case_id}', headers=another_auth_headers)
    assert response.status_code == 404
    response = client.put(f'/api/business_cases/{case_id}', headers=another_auth_headers, json={'title': 'Hacked'})
    assert response.status_code == 404
    response = client.delete(f'/api/business_cases/{case_id}', headers=another_auth_headers)
    assert response.status_code == 404

def test_list_is_tenant_scoped(client, auth_headers, another_auth_headers, sample_business_case):
    # Create a business case for another tenant
    data = {'title': 'Other Tenant Case'}
    response = client.post('/api/business_cases', headers=another_auth_headers, json=data)
    assert response.status_code == 201
    # List for tenant 1
    response = client.get('/api/business_cases', headers=auth_headers)
    items = response.get_json()['items']
    assert all(bc['tenant_id'] == 1 for bc in items)
    # List for tenant 2
    response = client.get('/api/business_cases', headers=another_auth_headers)
    items = response.get_json()['items']
    assert all(bc['tenant_id'] == 2 for bc in items) 