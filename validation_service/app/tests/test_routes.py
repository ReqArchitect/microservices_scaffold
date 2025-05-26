import pytest

def test_validate_success(client, auth_header_factory, requests_mock):
    headers = auth_header_factory(role='admin')
    # Mock OPA response
    requests_mock.post('http://localhost:8181/v1/data/validation/allow', json={'result': True})
    resp = client.post('/validate', json={
        'input': 'test'
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['allowed'] is True

def test_validate_unauthorized(client):
    resp = client.post('/validate', json={
        'input': 'test'
    })
    assert resp.status_code == 401

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_validate_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    resp = client.post('/validate', json={
        'input': 'test'
    }, headers=headers)
    assert resp.status_code in (401, 403)

# TODO: Add tests for multi-tenant, invalid input, and audit log emission 