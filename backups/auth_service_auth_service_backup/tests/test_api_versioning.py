import pytest
from flask import Flask, jsonify
from app.utils.api_versioning import (
    api_version, get_api_version, get_latest_version,
    is_version_deprecated, get_deprecation_date
)

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['API_VERSIONS'] = ['v1', 'v2', 'v3']
    app.config['API_LATEST_VERSION'] = 'v3'
    app.config['API_DEPRECATED_VERSIONS'] = {
        'v1': '2024-12-31',
        'v2': '2025-12-31'
    }
    return app

def test_api_version_decorator(app):
    """Test API version decorator."""
    @app.route('/test')
    @api_version('v1')
    def test_route_v1():
        return jsonify({'version': 'v1'})
    
    @app.route('/test')
    @api_version('v2')
    def test_route_v2():
        return jsonify({'version': 'v2'})
    
    @app.route('/test')
    @api_version('v3')
    def test_route_v3():
        return jsonify({'version': 'v3'})
    
    client = app.test_client()
    
    # Test v1 endpoint
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 200
    assert response.json['version'] == 'v1'
    
    # Test v2 endpoint
    response = client.get('/test', headers={'X-API-Version': 'v2'})
    assert response.status_code == 200
    assert response.json['version'] == 'v2'
    
    # Test v3 endpoint
    response = client.get('/test', headers={'X-API-Version': 'v3'})
    assert response.status_code == 200
    assert response.json['version'] == 'v3'

def test_api_version_header(app):
    """Test API version header."""
    @app.route('/test')
    @api_version('v1')
    def test_route():
        return jsonify({'version': get_api_version()})
    
    client = app.test_client()
    
    # Test with version header
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 200
    assert response.json['version'] == 'v1'
    
    # Test without version header
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json['version'] == 'v1'  # Default version

def test_latest_version(app):
    """Test getting latest API version."""
    @app.route('/test')
    @api_version('v1')
    def test_route():
        return jsonify({'latest_version': get_latest_version()})
    
    client = app.test_client()
    
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json['latest_version'] == 'v3'

def test_deprecated_version(app):
    """Test deprecated version handling."""
    @app.route('/test')
    @api_version('v1')
    def test_route():
        return jsonify({
            'version': get_api_version(),
            'is_deprecated': is_version_deprecated(get_api_version()),
            'deprecation_date': get_deprecation_date(get_api_version())
        })
    
    client = app.test_client()
    
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 200
    assert response.json['version'] == 'v1'
    assert response.json['is_deprecated'] is True
    assert response.json['deprecation_date'] == '2024-12-31'

def test_non_deprecated_version(app):
    """Test non-deprecated version handling."""
    @app.route('/test')
    @api_version('v3')
    def test_route():
        return jsonify({
            'version': get_api_version(),
            'is_deprecated': is_version_deprecated(get_api_version()),
            'deprecation_date': get_deprecation_date(get_api_version())
        })
    
    client = app.test_client()
    
    response = client.get('/test', headers={'X-API-Version': 'v3'})
    assert response.status_code == 200
    assert response.json['version'] == 'v3'
    assert response.json['is_deprecated'] is False
    assert response.json['deprecation_date'] is None

def test_invalid_version(app):
    """Test invalid version handling."""
    @app.route('/test')
    @api_version('v1')
    def test_route():
        return jsonify({'version': get_api_version()})
    
    client = app.test_client()
    
    response = client.get('/test', headers={'X-API-Version': 'invalid'})
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid API version' in response.json['error']

def test_version_migration(app):
    """Test version migration handling."""
    @app.route('/test')
    @api_version('v1')
    def test_route_v1():
        return jsonify({
            'version': 'v1',
            'data': {'old_field': 'value'}
        })
    
    @app.route('/test')
    @api_version('v2')
    def test_route_v2():
        return jsonify({
            'version': 'v2',
            'data': {'new_field': 'value'}
        })
    
    client = app.test_client()
    
    # Test v1 endpoint
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 200
    assert response.json['version'] == 'v1'
    assert 'old_field' in response.json['data']
    
    # Test v2 endpoint
    response = client.get('/test', headers={'X-API-Version': 'v2'})
    assert response.status_code == 200
    assert response.json['version'] == 'v2'
    assert 'new_field' in response.json['data']

def test_version_headers(app):
    """Test version-related headers."""
    @app.route('/test')
    @api_version('v1')
    def test_route():
        return jsonify({'version': get_api_version()})
    
    client = app.test_client()
    
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 200
    assert 'X-API-Version' in response.headers
    assert response.headers['X-API-Version'] == 'v1'
    assert 'X-API-Latest-Version' in response.headers
    assert response.headers['X-API-Latest-Version'] == 'v3'
    assert 'X-API-Deprecated' in response.headers
    assert response.headers['X-API-Deprecated'] == 'true'
    assert 'X-API-Deprecation-Date' in response.headers
    assert response.headers['X-API-Deprecation-Date'] == '2024-12-31'

def test_version_negotiation(app):
    """Test version negotiation."""
    @app.route('/test')
    @api_version('v1')
    def test_route_v1():
        return jsonify({'version': 'v1'})
    
    @app.route('/test')
    @api_version('v2')
    def test_route_v2():
        return jsonify({'version': 'v2'})
    
    @app.route('/test')
    @api_version('v3')
    def test_route_v3():
        return jsonify({'version': 'v3'})
    
    client = app.test_client()
    
    # Test version negotiation with Accept header
    response = client.get('/test', headers={'Accept': 'application/json;version=v2'})
    assert response.status_code == 200
    assert response.json['version'] == 'v2'
    
    # Test version negotiation with query parameter
    response = client.get('/test?version=v3')
    assert response.status_code == 200
    assert response.json['version'] == 'v3'
    
    # Test version negotiation with path parameter
    response = client.get('/v1/test')
    assert response.status_code == 200
    assert response.json['version'] == 'v1'

def test_version_fallback(app):
    """Test version fallback behavior."""
    @app.route('/test')
    @api_version('v1')
    def test_route_v1():
        return jsonify({'version': 'v1'})
    
    @app.route('/test')
    @api_version('v2')
    def test_route_v2():
        return jsonify({'version': 'v2'})
    
    client = app.test_client()
    
    # Test fallback to latest version when requested version is not available
    response = client.get('/test', headers={'X-API-Version': 'v3'})
    assert response.status_code == 200
    assert response.json['version'] == 'v2'  # Falls back to v2 as v3 is not implemented

def test_version_removal(app):
    """Test version removal handling."""
    @app.route('/test')
    @api_version('v1', removed=True)
    def test_route_v1():
        return jsonify({'version': 'v1'})
    
    @app.route('/test')
    @api_version('v2')
    def test_route_v2():
        return jsonify({'version': 'v2'})
    
    client = app.test_client()
    
    # Test removed version
    response = client.get('/test', headers={'X-API-Version': 'v1'})
    assert response.status_code == 410
    assert 'error' in response.json
    assert 'API version has been removed' in response.json['error']
    
    # Test non-removed version
    response = client.get('/test', headers={'X-API-Version': 'v2'})
    assert response.status_code == 200
    assert response.json['version'] == 'v2' 