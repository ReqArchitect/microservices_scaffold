def test_create_business_actor(client, auth_header):
    resp = client.post('/api/business_actors', json={
        'name': 'Test Actor',
        'description': 'desc'
    }, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_actors(client, auth_header):
    client.post('/api/business_actors', json={
        'name': 'Test Actor',
        'description': 'desc'
    }, headers=auth_header)
    resp = client.get('/api/business_actors', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_create_business_process(client, auth_header):
    resp = client.post('/api/business_processes', json={
        'name': 'Test Process',
        'description': 'desc'
    }, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_processes(client, auth_header):
    client.post('/api/business_processes', json={
        'name': 'Test Process',
        'description': 'desc'
    }, headers=auth_header)
    resp = client.get('/api/business_processes', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_create_goal(client, auth_header):
    resp = client.post('/api/goals', json={
        'title': 'Test Goal',
        'description': 'desc'
    }, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_goals(client, auth_header):
    client.post('/api/goals', json={
        'title': 'Test Goal',
        'description': 'desc'
    }, headers=auth_header)
    resp = client.get('/api/goals', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_create_objective(client, auth_header):
    resp = client.post('/api/objectives', json={
        'title': 'Test Objective',
        'description': 'desc'
    }, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_objectives(client, auth_header):
    client.post('/api/objectives', json={
        'title': 'Test Objective',
        'description': 'desc'
    }, headers=auth_header)
    resp = client.get('/api/objectives', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
