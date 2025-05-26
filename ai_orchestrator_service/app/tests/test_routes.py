import pytest

def test_generate_code_success(client, auth_header_factory):
    headers = auth_header_factory(role='admin')
    resp = client.post('/api/ai_orchestrator/generate-code', json={
        'prompt': 'Generate code for X'
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['result'] == 'success'

def test_generate_code_unauthorized(client):
    resp = client.post('/api/ai_orchestrator/generate-code', json={
        'prompt': 'Generate code for X'
    })
    assert resp.status_code == 401

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_generate_code_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    resp = client.post('/api/ai_orchestrator/generate-code', json={
        'prompt': 'Generate code for X'
    }, headers=headers)
    assert resp.status_code in (401, 403)

# TODO: Add tests for multi-tenant, invalid input, and audit log emission 