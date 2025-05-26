import pytest

def test_create_application_component(client, auth_header_factory):
    headers = auth_header_factory(role='admin')
    resp = client.post('/api/application_components', json={
        'name': 'Test App Component',
        'description': 'desc'
    }, headers=headers)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_create_application_component_unauthorized(client):
    resp = client.post('/api/application_components', json={
        'name': 'Test App Component',
        'description': 'desc'
    })
    assert resp.status_code == 401

@pytest.mark.parametrize("role", ["admin", "architect"])
def test_get_application_components_rbac(client, auth_header_factory, role):
    headers = auth_header_factory(role=role)
    resp = client.get('/api/application_components', headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_get_application_components_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    resp = client.get('/api/application_components', headers=headers)
    assert resp.status_code in (401, 403)

# Add more tests for multi-tenant, invalid input, etc. as needed
