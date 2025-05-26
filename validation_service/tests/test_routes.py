import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_validate_allows_by_default(client, monkeypatch):
    # Patch requests.post to simulate OPA allow
    class DummyResponse:
        def json(self):
            return {'result': True}
    monkeypatch.setattr('requests.post', lambda *a, **kw: DummyResponse())
    resp = client.post('/validate', json={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.json['allowed'] is True

def test_create_policy(client, auth_header):
    resp = client.post('/policies', json={'name': 'Test Policy', 'policy_text': 'allow = true'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_policies(client, auth_header):
    client.post('/policies', json={'name': 'Test Policy', 'policy_text': 'allow = true'}, headers=auth_header)
    resp = client.get('/policies', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
