import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_estimate(client):
    resp = client.post('/estimate', json={"usage": 100})
    assert resp.status_code == 200
    assert 'estimate' in resp.json

def test_list_scenarios(client):
    resp = client.get('/scenarios')
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

def test_create_cost_model(client, auth_header):
    resp = client.post('/cost_models', json={'name': 'Test Model'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_cost_models(client, auth_header):
    client.post('/cost_models', json={'name': 'Test Model'}, headers=auth_header)
    resp = client.get('/cost_models', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
