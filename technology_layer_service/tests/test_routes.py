import pytest
from technology_layer_service.app import create_app, db
from technology_layer_service.app.models import Node
from flask_jwt_extended import create_access_token
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header():
    # Mock JWT token (adjust as needed for your JWT setup)
    token = create_access_token(identity='testuser')
    return {'Authorization': f'Bearer {token}'}

def test_create_node(client, auth_header):
    resp = client.post('/api/v1/nodes', json={'name': 'Node1', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success']
    assert data['data']['name'] == 'Node1'

def test_list_nodes(client, auth_header):
    client.post('/api/v1/nodes', json={'name': 'Node2', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/api/v1/nodes', headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']
    assert isinstance(data['data'], list)

def test_get_node(client, auth_header):
    post = client.post('/api/v1/nodes', json={'name': 'Node3', 'description': 'desc'}, headers=auth_header)
    node_id = post.get_json()['data']['id']
    resp = client.get(f'/api/v1/nodes/{node_id}', headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']
    assert data['data']['id'] == node_id

def test_update_node(client, auth_header):
    post = client.post('/api/v1/nodes', json={'name': 'Node4', 'description': 'desc'}, headers=auth_header)
    node_id = post.get_json()['data']['id']
    resp = client.put(f'/api/v1/nodes/{node_id}', json={'name': 'Node4-updated'}, headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']
    assert data['data']['name'] == 'Node4-updated'

def test_delete_node(client, auth_header):
    post = client.post('/api/v1/nodes', json={'name': 'Node5', 'description': 'desc'}, headers=auth_header)
    node_id = post.get_json()['data']['id']
    resp = client.delete(f'/api/v1/nodes/{node_id}', headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']
    assert data['data']['deleted'] 