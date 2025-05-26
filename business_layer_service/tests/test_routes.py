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
<<<<<<< HEAD

# --- BusinessCollaboration ---
def test_create_business_collaboration(client, auth_header):
    resp = client.post('/business_collaborations', json={'name': 'Collab', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_collaborations(client, auth_header):
    client.post('/business_collaborations', json={'name': 'Collab', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_collaborations', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessInterface ---
def test_create_business_interface(client, auth_header):
    resp = client.post('/business_interfaces', json={'name': 'Interface', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_interfaces(client, auth_header):
    client.post('/business_interfaces', json={'name': 'Interface', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_interfaces', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessFunction ---
def test_create_business_function(client, auth_header):
    resp = client.post('/business_functions', json={'name': 'Function', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_functions(client, auth_header):
    client.post('/business_functions', json={'name': 'Function', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_functions', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessInteraction ---
def test_create_business_interaction(client, auth_header):
    resp = client.post('/business_interactions', json={'name': 'Interaction', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_interactions(client, auth_header):
    client.post('/business_interactions', json={'name': 'Interaction', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_interactions', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessEvent ---
def test_create_business_event(client, auth_header):
    resp = client.post('/business_events', json={'name': 'Event', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_events(client, auth_header):
    client.post('/business_events', json={'name': 'Event', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_events', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessService ---
def test_create_business_service(client, auth_header):
    resp = client.post('/business_services', json={'name': 'Service', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_services(client, auth_header):
    client.post('/business_services', json={'name': 'Service', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_services', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- BusinessObject ---
def test_create_business_object(client, auth_header):
    resp = client.post('/business_objects', json={'name': 'Object', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_business_objects(client, auth_header):
    client.post('/business_objects', json={'name': 'Object', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/business_objects', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- Contract ---
def test_create_contract(client, auth_header):
    resp = client.post('/contracts', json={'name': 'Contract', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_contracts(client, auth_header):
    client.post('/contracts', json={'name': 'Contract', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/contracts', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

# --- Product ---
def test_create_product(client, auth_header):
    resp = client.post('/products', json={'name': 'Product', 'description': 'desc'}, headers=auth_header)
    assert resp.status_code == 201
    assert 'id' in resp.get_json()

def test_get_products(client, auth_header):
    client.post('/products', json={'name': 'Product', 'description': 'desc'}, headers=auth_header)
    resp = client.get('/products', headers=auth_header)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
