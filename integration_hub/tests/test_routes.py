import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_integration(client):
    resp = client.post('/integrations', json={"name": "Test Integration"})
    assert resp.status_code == 201
    assert resp.json['status'] == 'registered'

def test_list_integrations(client):
    resp = client.get('/integrations')
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

def test_create_integration(client, auth_header):
    resp = client.post('/integrations', json={'name': 'Test', 'type': 'webhook'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_integrations(client, auth_header):
    client.post('/integrations', json={'name': 'Test', 'type': 'webhook'}, headers=auth_header)
    resp = client.get('/integrations', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
