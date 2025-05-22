def test_create_capability(client, auth_header):
    resp = client.post('/api/capabilities', json={
        'title': 'Test Capability',
        'description': 'desc'
    }, headers={**auth_header, 'Accept': 'application/json'})
    print('create_capability response:', resp.status_code, resp.get_json())
    assert resp.status_code == 201, f"Response: {resp.get_json()}"

def test_get_capabilities(client, auth_header):
    resp = client.get('/api/capabilities', headers={**auth_header, 'Accept': 'application/json'})
    print('get_capabilities response:', resp.status_code, resp.get_json())
    assert resp.status_code == 200, f"Response: {resp.get_json()}"

def test_create_course_of_action(client, auth_header):
    resp = client.post('/api/courses_of_action', json={
        'title': 'Test Action',
        'description': 'desc'
    }, headers={**auth_header, 'Accept': 'application/json'})
    print('create_course_of_action response:', resp.status_code, resp.get_json())
    assert resp.status_code == 201, f"Response: {resp.get_json()}"

def test_get_courses_of_action(client, auth_header):
    resp = client.get('/api/courses_of_action', headers={**auth_header, 'Accept': 'application/json'})
    print('get_courses_of_action response:', resp.status_code, resp.get_json())
    assert resp.status_code == 200, f"Response: {resp.get_json()}"
