import pytest
import time
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def limiter(app):
    """Create a Limiter instance for testing."""
    return Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

def test_rate_limit_decorator(app, limiter):
    """Test rate limit decorator."""
    @app.route('/test')
    @limiter.limit("5 per minute")
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # Make 5 requests (should succeed)
    for _ in range(5):
        response = client.get('/test')
        assert response.status_code == 200
        assert response.json['message'] == 'success'
    
    # 6th request should fail
    response = client.get('/test')
    assert response.status_code == 429
    assert 'rate limit exceeded' in response.json['error'].lower()

def test_rate_limit_reset(app, limiter):
    """Test rate limit reset after timeout."""
    @app.route('/test')
    @limiter.limit("2 per minute")
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # Make 2 requests
    for _ in range(2):
        response = client.get('/test')
        assert response.status_code == 200
    
    # 3rd request should fail
    response = client.get('/test')
    assert response.status_code == 429
    
    # Wait for 1 minute
    time.sleep(61)
    
    # Should work again
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json['message'] == 'success'

def test_different_rate_limits(app, limiter):
    """Test different rate limits for different endpoints."""
    @app.route('/endpoint1')
    @limiter.limit("3 per minute")
    def endpoint1():
        return {'message': 'endpoint1'}
    
    @app.route('/endpoint2')
    @limiter.limit("2 per minute")
    def endpoint2():
        return {'message': 'endpoint2'}
    
    client = app.test_client()
    
    # Test endpoint1
    for _ in range(3):
        response = client.get('/endpoint1')
        assert response.status_code == 200
        assert response.json['message'] == 'endpoint1'
    
    response = client.get('/endpoint1')
    assert response.status_code == 429
    
    # Test endpoint2 (should still work)
    for _ in range(2):
        response = client.get('/endpoint2')
        assert response.status_code == 200
        assert response.json['message'] == 'endpoint2'
    
    response = client.get('/endpoint2')
    assert response.status_code == 429

def test_rate_limit_by_ip(app, limiter):
    """Test rate limiting by IP address."""
    @app.route('/test')
    @limiter.limit("2 per minute")
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # Simulate requests from different IPs
    headers1 = {'X-Forwarded-For': '192.168.1.1'}
    headers2 = {'X-Forwarded-For': '192.168.1.2'}
    
    # IP 1: 2 requests
    for _ in range(2):
        response = client.get('/test', headers=headers1)
        assert response.status_code == 200
    
    response = client.get('/test', headers=headers1)
    assert response.status_code == 429
    
    # IP 2: should still work
    for _ in range(2):
        response = client.get('/test', headers=headers2)
        assert response.status_code == 200

def test_rate_limit_exempt(app, limiter):
    """Test rate limit exemption."""
    @app.route('/test')
    @limiter.limit("2 per minute", exempt_when=lambda: True)
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # Should work unlimited times
    for _ in range(5):
        response = client.get('/test')
        assert response.status_code == 200
        assert response.json['message'] == 'success'

def test_rate_limit_dynamic(app, limiter):
    """Test dynamic rate limiting."""
    @app.route('/test')
    @limiter.limit(lambda: "3 per minute")
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # Make 3 requests
    for _ in range(3):
        response = client.get('/test')
        assert response.status_code == 200
    
    # 4th request should fail
    response = client.get('/test')
    assert response.status_code == 429

def test_rate_limit_headers(app, limiter):
    """Test rate limit headers in response."""
    @app.route('/test')
    @limiter.limit("2 per minute")
    def test_endpoint():
        return {'message': 'success'}
    
    client = app.test_client()
    
    # First request
    response = client.get('/test')
    assert response.status_code == 200
    assert 'X-RateLimit-Limit' in response.headers
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers
    
    # Second request
    response = client.get('/test')
    assert response.status_code == 200
    assert int(response.headers['X-RateLimit-Remaining']) == 0
    
    # Third request (should fail)
    response = client.get('/test')
    assert response.status_code == 429
    assert 'Retry-After' in response.headers 