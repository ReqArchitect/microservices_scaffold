import pytest

def test_add_motivation_success(client, auth_header_factory):
    headers = auth_header_factory(role='admin')
    resp = client.post('/api/motivation/motivation', json={
        'motivation': 'Test motivation'
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['result'] == 'success'

def test_add_motivation_unauthorized(client):
    resp = client.post('/api/motivation/motivation', json={
        'motivation': 'Test motivation'
    })
    assert resp.status_code == 401

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_add_motivation_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    resp = client.post('/api/motivation/motivation', json={
        'motivation': 'Test motivation'
    }, headers=headers)
    assert resp.status_code in (401, 403)

# TODO: Add tests for multi-tenant, invalid input, and audit log emission 