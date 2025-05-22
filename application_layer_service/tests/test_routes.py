def test_create_application_component(client, auth_header):
    resp = client.post('/api/application_components', json={
        'name': 'Test App Component',
        'description': 'desc'
    }, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_application_components(client, auth_header):
    client.post('/api/application_components', json={
        'name': 'Test App Component',
        'description': 'desc'
    }, headers=auth_header)
    resp = client.get('/api/application_components', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
