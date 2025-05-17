import pytest
import time
from flask import Flask, jsonify
from flask_caching import Cache
from app.utils.caching import setup_caching

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    return app

@pytest.fixture
def cache(app):
    """Create a cache for testing."""
    return setup_caching(app)

def test_cache_set_get(app, cache):
    """Test setting and getting cache values."""
    with app.app_context():
        # Set cache value
        cache.set('test_key', 'test_value')
        
        # Get cache value
        value = cache.get('test_key')
        assert value == 'test_value'

def test_cache_delete(app, cache):
    """Test deleting cache values."""
    with app.app_context():
        # Set cache value
        cache.set('test_key', 'test_value')
        
        # Delete cache value
        cache.delete('test_key')
        
        # Get cache value
        value = cache.get('test_key')
        assert value is None

def test_cache_clear(app, cache):
    """Test clearing all cache values."""
    with app.app_context():
        # Set multiple cache values
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        # Clear cache
        cache.clear()
        
        # Check if values are cleared
        assert cache.get('key1') is None
        assert cache.get('key2') is None

def test_cache_timeout(app, cache):
    """Test cache timeout."""
    with app.app_context():
        # Set cache value with timeout
        cache.set('test_key', 'test_value', timeout=1)
        
        # Get cache value immediately
        value = cache.get('test_key')
        assert value == 'test_value'
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Get cache value after timeout
        value = cache.get('test_key')
        assert value is None

def test_cache_decorator(app, cache):
    """Test cache decorator."""
    with app.app_context():
        @app.route('/test')
        @cache.cached(timeout=300)
        def test_route():
            return jsonify({'message': 'success'})
        
        client = app.test_client()
        
        # Make first request
        response1 = client.get('/test')
        assert response1.status_code == 200
        
        # Make second request
        response2 = client.get('/test')
        assert response2.status_code == 200
        
        # Check if responses are cached
        assert response1.data == response2.data

def test_cache_memoize(app, cache):
    """Test cache memoize decorator."""
    with app.app_context():
        @app.route('/test/<int:value>')
        @cache.memoize(timeout=300)
        def test_route(value):
            return jsonify({'message': f'success {value}'})
        
        client = app.test_client()
        
        # Make requests with different values
        response1 = client.get('/test/1')
        response2 = client.get('/test/2')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.data != response2.data

def test_cache_many(app, cache):
    """Test setting and getting multiple cache values."""
    with app.app_context():
        # Set multiple cache values
        cache.set_many({
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        })
        
        # Get multiple cache values
        values = cache.get_many(['key1', 'key2', 'key3'])
        assert values == {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }

def test_cache_delete_many(app, cache):
    """Test deleting multiple cache values."""
    with app.app_context():
        # Set multiple cache values
        cache.set_many({
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        })
        
        # Delete multiple cache values
        cache.delete_many(['key1', 'key2'])
        
        # Check if values are deleted
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') == 'value3'

def test_cache_add(app, cache):
    """Test adding cache values."""
    with app.app_context():
        # Add cache value
        cache.add('test_key', 'test_value')
        
        # Try to add same key again
        cache.add('test_key', 'new_value')
        
        # Check if original value is preserved
        value = cache.get('test_key')
        assert value == 'test_value'

def test_cache_inc_dec(app, cache):
    """Test incrementing and decrementing cache values."""
    with app.app_context():
        # Set initial value
        cache.set('counter', 0)
        
        # Increment value
        cache.inc('counter')
        assert cache.get('counter') == 1
        
        # Decrement value
        cache.dec('counter')
        assert cache.get('counter') == 0

def test_cache_version(app, cache):
    """Test cache versioning."""
    with app.app_context():
        # Set cache value with version
        cache.set('test_key', 'test_value', version=1)
        
        # Get cache value with version
        value = cache.get('test_key', version=1)
        assert value == 'test_value'
        
        # Get cache value with different version
        value = cache.get('test_key', version=2)
        assert value is None

def test_cache_prefix(app, cache):
    """Test cache key prefixing."""
    with app.app_context():
        # Set cache value with prefix
        cache.set('test_key', 'test_value', prefix='test_')
        
        # Get cache value with prefix
        value = cache.get('test_key', prefix='test_')
        assert value == 'test_value'
        
        # Get cache value without prefix
        value = cache.get('test_key')
        assert value is None

def test_cache_has(app, cache):
    """Test checking if cache has key."""
    with app.app_context():
        # Set cache value
        cache.set('test_key', 'test_value')
        
        # Check if key exists
        assert cache.has('test_key')
        assert not cache.has('nonexistent_key')

def test_cache_ttl(app, cache):
    """Test getting cache TTL."""
    with app.app_context():
        # Set cache value with timeout
        cache.set('test_key', 'test_value', timeout=300)
        
        # Get TTL
        ttl = cache.ttl('test_key')
        assert 0 < ttl <= 300 