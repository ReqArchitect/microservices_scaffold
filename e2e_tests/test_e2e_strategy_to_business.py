import os
import requests
import pytest
import jwt
import datetime
import pytz

print(f"[E2E TEST] JWT_SECRET_KEY in test: {os.environ.get('JWT_SECRET_KEY')}")

STRATEGY_URL = os.environ.get('STRATEGY_URL', 'http://localhost:5001/api/capabilities')
BUSINESS_URL = os.environ.get('BUSINESS_URL', 'http://localhost:5002/api/business_actors')

@pytest.fixture
def jwt_token():
    """Fixture to generate a valid JWT token for E2E tests with correct exp and iat using timezone-aware UTC."""
    secret = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    print(f"[E2E TEST] jwt_token fixture using secret: {secret}")
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'sub': '1',
        'tenant_id': 1,
        'iat': int(now.timestamp()),
        'exp': int((now + datetime.timedelta(hours=1)).timestamp())
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

@pytest.fixture(autouse=True)
def cleanup_business_actors(jwt_token):
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    resp = requests.get(BUSINESS_URL, headers=headers)
    if resp.status_code == 200:
        actors = resp.json()
        for actor in actors:
            if actor.get('name') == 'E2E Capability':
                requests.delete(f"{BUSINESS_URL}/{actor['id']}", headers=headers)
    yield
    resp = requests.get(BUSINESS_URL, headers=headers)
    if resp.status_code == 200:
        actors = resp.json()
        for actor in actors:
            if actor.get('name') == 'E2E Capability':
                requests.delete(f"{BUSINESS_URL}/{actor['id']}", headers=headers)

def test_strategy_to_business_e2e(jwt_token):
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    cap_payload = {
        'title': 'E2E Capability',
        'description': 'E2E test capability'
    }
    cap_resp = requests.post(STRATEGY_URL, json=cap_payload, headers=headers)
    assert cap_resp.status_code == 201, f"Strategy service failed: {cap_resp.text}"
    cap_id = cap_resp.json()['id']
    business_resp = requests.get(BUSINESS_URL, headers=headers)
    assert business_resp.status_code == 200, f"Business layer service failed: {business_resp.text}"
    actors = business_resp.json()
    found = any(a['name'] == 'E2E Capability' and a['description'] == 'E2E test capability' for a in actors)
    assert found, "BusinessActor not created from Capability!"
    bad_payload = {'title': 'Missing Description'}
    bad_resp = requests.post(STRATEGY_URL, json=bad_payload, headers=headers)
    assert bad_resp.status_code in (400, 422), "Should fail with missing fields"
    bad_headers = headers.copy()
    bad_headers['Authorization'] = 'Bearer invalid.jwt.token'
    resp = requests.post(STRATEGY_URL, json=cap_payload, headers=bad_headers)
    assert resp.status_code in (401, 422), "Should fail with invalid JWT"
    resp = requests.post(STRATEGY_URL, json=cap_payload)
    assert resp.status_code in (401, 422), "Should fail with no JWT"
    resp = requests.get(BUSINESS_URL, headers=bad_headers)
    assert resp.status_code in (401, 422), "Should fail with invalid JWT on business layer"
    resp = requests.get(BUSINESS_URL)
    assert resp.status_code in (401, 422), "Should fail with no JWT on business layer"
    dup_resp = requests.post(STRATEGY_URL, json=cap_payload, headers=headers)
    assert dup_resp.status_code in (201, 409, 400), "Duplicate capability should be handled"
    for actor in actors:
        if actor.get('name') == 'E2E Capability':
            del_resp = requests.delete(f"{BUSINESS_URL}/{actor['id']}", headers=headers)
            assert del_resp.status_code in (200, 204, 404), "BusinessActor deletion should succeed or be idempotent"
    non_existent_id = 999999
    del_resp = requests.delete(f"{BUSINESS_URL}/{non_existent_id}", headers=headers)
    assert del_resp.status_code in (404, 400), "Deleting non-existent BusinessActor should return 404 or 400"
    update_payload = {'title': ''}
    update_url = f"{STRATEGY_URL}/{cap_id}"
    update_resp = requests.put(update_url, json=update_payload, headers=headers)
    assert update_resp.status_code in (400, 404, 422), "Updating with invalid data should fail"
    non_existent_cap_id = 999999
    update_url = f"{STRATEGY_URL}/{non_existent_cap_id}"
    update_resp = requests.put(update_url, json=cap_payload, headers=headers)
    assert update_resp.status_code in (404, 400), "Updating non-existent Capability should return 404 or 400"
    get_url = f"{STRATEGY_URL}/{non_existent_cap_id}"
    get_resp = requests.get(get_url, headers=headers)
    assert get_resp.status_code in (404, 400), "Getting non-existent Capability should return 404 or 400"
    get_url = f"{BUSINESS_URL}/{non_existent_id}"
    get_resp = requests.get(get_url, headers=headers)
    assert get_resp.status_code in (404, 400), "Getting non-existent BusinessActor should return 404 or 400"
