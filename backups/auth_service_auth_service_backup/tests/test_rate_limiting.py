import pytest
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.rate_limiting import setup_rate_limiting

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    app.config['RATELIMIT_DEFAULT'] = '100/hour'
    app.config['RATELIMIT_HEADERS_ENABLED'] = True
    return app

@pytest.fixture
def limiter(app):
    """Create a rate limiter for testing."""
    return setup_rate_limiting(app)

def test_rate_limit_default(app, limiter):
    """Test default rate limit."""
    @app.route('/test')
    @limiter.limit('100/hour')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests up to the limit
    for _ in range(100):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429
    assert 'X-RateLimit-Limit' in response.headers
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers

def test_rate_limit_by_ip(app, limiter):
    """Test rate limit by IP address."""
    @app.route('/test')
    @limiter.limit('10/minute', key_func=get_remote_address)
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests up to the limit
    for _ in range(10):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429

def test_rate_limit_by_user(app, limiter):
    """Test rate limit by user."""
    @app.route('/test')
    @limiter.limit('5/minute', key_func=lambda: 'user123')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests up to the limit
    for _ in range(5):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429

def test_rate_limit_exempt(app, limiter):
    """Test rate limit exemption."""
    @app.route('/test')
    @limiter.exempt
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make multiple requests
    for _ in range(100):
        response = client.get('/test')
        assert response.status_code == 200

def test_rate_limit_dynamic(app, limiter):
    """Test dynamic rate limit."""
    @app.route('/test')
    @limiter.limit(lambda: '10/minute')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests up to the limit
    for _ in range(10):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429

def test_rate_limit_shared(app, limiter):
    """Test shared rate limit."""
    @app.route('/test1')
    @limiter.limit('10/minute', shared_limit=True)
    def test_route1():
        return jsonify({'message': 'success'})
    
    @app.route('/test2')
    @limiter.limit('10/minute', shared_limit=True)
    def test_route2():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests to first route up to the limit
    for _ in range(10):
        response = client.get('/test1')
        assert response.status_code == 200
    
    # Next request to second route should be rate limited
    response = client.get('/test2')
    assert response.status_code == 429

def test_rate_limit_headers(app, limiter):
    """Test rate limit headers."""
    @app.route('/test')
    @limiter.limit('10/minute')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make a request
    response = client.get('/test')
    assert response.status_code == 200
    assert response.headers['X-RateLimit-Limit'] == '10'
    assert response.headers['X-RateLimit-Remaining'] == '9'
    assert 'X-RateLimit-Reset' in response.headers

def test_rate_limit_error_message(app, limiter):
    """Test rate limit error message."""
    @app.route('/test')
    @limiter.limit('1/minute')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make first request
    response = client.get('/test')
    assert response.status_code == 200
    
    # Make second request
    response = client.get('/test')
    assert response.status_code == 429
    assert 'error' in response.json
    assert 'message' in response.json
    assert 'Too many requests' in response.json['message']

def test_rate_limit_reset(app, limiter):
    """Test rate limit reset."""
    @app.route('/test')
    @limiter.limit('10/minute')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests up to the limit
    for _ in range(10):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429
    
    # Wait for rate limit to reset
    import time
    time.sleep(61)
    
    # Should be able to make requests again
    response = client.get('/test')
    assert response.status_code == 200

def test_rate_limit_by_endpoint(app, limiter):
    """Test rate limit by endpoint."""
    @app.route('/test1')
    @limiter.limit('5/minute')
    def test_route1():
        return jsonify({'message': 'success'})
    
    @app.route('/test2')
    @limiter.limit('10/minute')
    def test_route2():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make requests to first route up to the limit
    for _ in range(5):
        response = client.get('/test1')
        assert response.status_code == 200
    
    # Next request to first route should be rate limited
    response = client.get('/test1')
    assert response.status_code == 429
    
    # Should still be able to make requests to second route
    for _ in range(10):
        response = client.get('/test2')
        assert response.status_code == 200

def test_rate_limit_by_method(app, limiter):
    """Test rate limit by HTTP method."""
    @app.route('/test', methods=['GET', 'POST'])
    @limiter.limit('5/minute', methods=['GET'])
    @limiter.limit('10/minute', methods=['POST'])
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make GET requests up to the limit
    for _ in range(5):
        response = client.get('/test')
        assert response.status_code == 200
    
    # Next GET request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429
    
    # Should still be able to make POST requests
    for _ in range(10):
        response = client.post('/test')
        assert response.status_code == 200 