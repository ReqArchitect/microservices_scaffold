import pytest

def test_create_project_success(client, auth_header_factory):
    headers = auth_header_factory(role='admin')
    resp = client.post('/api/implementation/implementation-projects', json={
        'projectId': 'P1',
        'title': 'Test Project',
        'description': 'desc'
    }, headers=headers)
    assert resp.status_code == 201
    assert 'projectId' in resp.get_json()

def test_create_project_unauthorized(client):
    resp = client.post('/api/implementation/implementation-projects', json={
        'projectId': 'P1',
        'title': 'Test Project',
        'description': 'desc'
    })
    assert resp.status_code == 401

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_create_project_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    resp = client.post('/api/implementation/implementation-projects', json={
        'projectId': 'P1',
        'title': 'Test Project',
        'description': 'desc'
    }, headers=headers)
    assert resp.status_code in (401, 403)

# TODO: Add tests for multi-tenant, invalid input, and audit log emission 