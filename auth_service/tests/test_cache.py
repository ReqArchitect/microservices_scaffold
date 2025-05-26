import pytest
import time
from flask import Flask
from flask_caching import Cache

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'SimpleCache'
    return app

@pytest.fixture
def cache(app):
    """Create a Cache instance for testing."""
    return Cache(app)

def test_cache_set_get(app, cache):
    """Test basic cache set and get operations."""
    with app.app_context():
        # Set value in cache
        cache.set('test_key', 'test_value')
        
        # Get value from cache
        value = cache.get('test_key')
        assert value == 'test_value'
        
        # Get non-existent value
        value = cache.get('non_existent_key')
        assert value is None

def test_cache_timeout(app, cache):
    """Test cache timeout functionality."""
    with app.app_context():
        # Set value with 1 second timeout
        cache.set('test_key', 'test_value', timeout=1)
        
        # Value should be available immediately
        assert cache.get('test_key') == 'test_value'
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Value should be expired
        assert cache.get('test_key') is None

def test_cache_delete(app, cache):
    """Test cache delete operation."""
    with app.app_context():
        # Set value
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Delete value
        cache.delete('test_key')
        assert cache.get('test_key') is None
        
        # Delete non-existent key (should not raise error)
        cache.delete('non_existent_key')

def test_cache_clear(app, cache):
    """Test cache clear operation."""
    with app.app_context():
        # Set multiple values
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Clear cache
        cache.clear()
        
        # All values should be gone
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None

def test_cache_decorator(app, cache):
    """Test cache decorator."""
    with app.app_context():
        call_count = 0
        
        @cache.memoize(timeout=1)
        def test_function(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return f"{arg1}-{arg2}-{call_count}"
        
        # First call should execute function
        result1 = test_function('a', 'b')
        assert call_count == 1
        
        # Second call with same arguments should use cache
        result2 = test_function('a', 'b')
        assert call_count == 1
        assert result1 == result2
        
        # Call with different arguments should execute function
        result3 = test_function('c', 'd')
        assert call_count == 2
        assert result3 != result1

def test_cache_decorator_timeout(app, cache):
    """Test cache decorator timeout."""
    with app.app_context():
        call_count = 0
        
        @cache.memoize(timeout=1)
        def test_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # First call
        result1 = test_function()
        assert call_count == 1
        
        # Second call (cached)
        result2 = test_function()
        assert call_count == 1
        assert result1 == result2
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Should execute function again
        result3 = test_function()
        assert call_count == 2
        assert result3 != result1

def test_cache_decorator_with_args(app, cache):
    """Test cache decorator with different argument types."""
    with app.app_context():
        @cache.memoize()
        def test_function(arg1, arg2, arg3=None):
            return f"{arg1}-{arg2}-{arg3}"
        
        # Test with different argument combinations
        result1 = test_function(1, 'a')
        result2 = test_function(1, 'a')  # Should use cache
        assert result1 == result2
        
        result3 = test_function(1, 'a', arg3='test')
        assert result3 != result1
        
        result4 = test_function(1, 'a', arg3='test')  # Should use cache
        assert result4 == result3

def test_cache_decorator_with_kwargs(app, cache):
    """Test cache decorator with keyword arguments."""
    with app.app_context():
        @cache.memoize()
        def test_function(**kwargs):
            return str(kwargs)
        
        # Test with different keyword arguments
        result1 = test_function(a=1, b=2)
        result2 = test_function(a=1, b=2)  # Should use cache
        assert result1 == result2
        
        result3 = test_function(b=2, a=1)  # Different order, should use cache
        assert result3 == result1
        
        result4 = test_function(a=1, b=3)  # Different value, should not use cache
        assert result4 != result1

def test_cache_decorator_with_objects(app, cache):
    """Test cache decorator with object arguments."""
    with app.app_context():
        class TestObject:
            def __init__(self, value):
                self.value = value
            
            def __eq__(self, other):
                return isinstance(other, TestObject) and self.value == other.value
        
        @cache.memoize()
        def test_function(obj):
            return obj.value
        
        # Test with objects
        obj1 = TestObject(1)
        obj2 = TestObject(1)
        
        result1 = test_function(obj1)
        result2 = test_function(obj2)  # Should use cache
        assert result1 == result2
        
        obj3 = TestObject(2)
        result3 = test_function(obj3)  # Should not use cache
        assert result3 != result1 