import pytest
from flask import Flask, jsonify
from prometheus_client import REGISTRY, Counter, Gauge, Histogram
from app.utils.metrics import setup_metrics, record_request, record_error, record_latency

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def metrics(app):
    """Create metrics for testing."""
    return setup_metrics(app)

def test_request_counter(metrics):
    """Test request counter metric."""
    # Record requests
    record_request('GET', '/api/v1/users', 200)
    record_request('POST', '/api/v1/auth/login', 201)
    record_request('GET', '/api/v1/users', 404)
    
    # Get counter value
    counter = REGISTRY.get_sample_value(
        'http_requests_total',
        {'method': 'GET', 'endpoint': '/api/v1/users', 'status': '200'}
    )
    assert counter == 1.0
    
    counter = REGISTRY.get_sample_value(
        'http_requests_total',
        {'method': 'POST', 'endpoint': '/api/v1/auth/login', 'status': '201'}
    )
    assert counter == 1.0
    
    counter = REGISTRY.get_sample_value(
        'http_requests_total',
        {'method': 'GET', 'endpoint': '/api/v1/users', 'status': '404'}
    )
    assert counter == 1.0

def test_error_counter(metrics):
    """Test error counter metric."""
    # Record errors
    record_error('GET', '/api/v1/users', 404, 'Not Found')
    record_error('POST', '/api/v1/auth/login', 400, 'Bad Request')
    
    # Get counter value
    counter = REGISTRY.get_sample_value(
        'http_errors_total',
        {'method': 'GET', 'endpoint': '/api/v1/users', 'status': '404', 'error': 'Not Found'}
    )
    assert counter == 1.0
    
    counter = REGISTRY.get_sample_value(
        'http_errors_total',
        {'method': 'POST', 'endpoint': '/api/v1/auth/login', 'status': '400', 'error': 'Bad Request'}
    )
    assert counter == 1.0

def test_latency_histogram(metrics):
    """Test latency histogram metric."""
    # Record latencies
    record_latency('GET', '/api/v1/users', 0.1)
    record_latency('GET', '/api/v1/users', 0.2)
    record_latency('GET', '/api/v1/users', 0.3)
    
    # Get histogram values
    histogram = REGISTRY.get_sample_value(
        'http_request_duration_seconds_count',
        {'method': 'GET', 'endpoint': '/api/v1/users'}
    )
    assert histogram == 3.0
    
    histogram = REGISTRY.get_sample_value(
        'http_request_duration_seconds_sum',
        {'method': 'GET', 'endpoint': '/api/v1/users'}
    )
    assert histogram == 0.6

def test_custom_counter(metrics):
    """Test custom counter metric."""
    # Create custom counter
    counter = Counter(
        'custom_events_total',
        'Total number of custom events',
        ['event_type']
    )
    
    # Record events
    counter.labels(event_type='login').inc()
    counter.labels(event_type='logout').inc()
    counter.labels(event_type='login').inc()
    
    # Get counter values
    value = REGISTRY.get_sample_value(
        'custom_events_total',
        {'event_type': 'login'}
    )
    assert value == 2.0
    
    value = REGISTRY.get_sample_value(
        'custom_events_total',
        {'event_type': 'logout'}
    )
    assert value == 1.0

def test_custom_gauge(metrics):
    """Test custom gauge metric."""
    # Create custom gauge
    gauge = Gauge(
        'active_users',
        'Number of active users',
        ['tenant']
    )
    
    # Set gauge values
    gauge.labels(tenant='tenant1').set(10)
    gauge.labels(tenant='tenant2').set(20)
    
    # Get gauge values
    value = REGISTRY.get_sample_value(
        'active_users',
        {'tenant': 'tenant1'}
    )
    assert value == 10.0
    
    value = REGISTRY.get_sample_value(
        'active_users',
        {'tenant': 'tenant2'}
    )
    assert value == 20.0

def test_custom_histogram(metrics):
    """Test custom histogram metric."""
    # Create custom histogram
    histogram = Histogram(
        'operation_duration_seconds',
        'Duration of operations',
        ['operation'],
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
    )
    
    # Record durations
    histogram.labels(operation='search').observe(0.2)
    histogram.labels(operation='search').observe(0.4)
    histogram.labels(operation='search').observe(0.6)
    
    # Get histogram values
    count = REGISTRY.get_sample_value(
        'operation_duration_seconds_count',
        {'operation': 'search'}
    )
    assert count == 3.0
    
    sum_value = REGISTRY.get_sample_value(
        'operation_duration_seconds_sum',
        {'operation': 'search'}
    )
    assert sum_value == 1.2

def test_metrics_middleware(app, metrics):
    """Test metrics middleware."""
    @app.route('/test')
    def test_route():
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make request
    response = client.get('/test')
    assert response.status_code == 200
    
    # Check if metrics are recorded
    counter = REGISTRY.get_sample_value(
        'http_requests_total',
        {'method': 'GET', 'endpoint': '/test', 'status': '200'}
    )
    assert counter == 1.0

def test_metrics_error_handling(app, metrics):
    """Test metrics error handling."""
    @app.route('/error')
    def error_route():
        return jsonify({'error': 'Not Found'}), 404
    
    client = app.test_client()
    
    # Make request
    response = client.get('/error')
    assert response.status_code == 404
    
    # Check if error metrics are recorded
    counter = REGISTRY.get_sample_value(
        'http_errors_total',
        {'method': 'GET', 'endpoint': '/error', 'status': '404', 'error': 'Not Found'}
    )
    assert counter == 1.0

def test_metrics_latency_tracking(app, metrics):
    """Test metrics latency tracking."""
    @app.route('/slow')
    def slow_route():
        import time
        time.sleep(0.1)
        return jsonify({'message': 'success'})
    
    client = app.test_client()
    
    # Make request
    response = client.get('/slow')
    assert response.status_code == 200
    
    # Check if latency metrics are recorded
    histogram = REGISTRY.get_sample_value(
        'http_request_duration_seconds_count',
        {'method': 'GET', 'endpoint': '/slow'}
    )
    assert histogram == 1.0

def test_metrics_custom_labels(app, metrics):
    """Test metrics with custom labels."""
    # Create custom counter with multiple labels
    counter = Counter(
        'api_calls_total',
        'Total number of API calls',
        ['method', 'endpoint', 'tenant', 'user']
    )
    
    # Record API calls
    counter.labels(
        method='GET',
        endpoint='/api/v1/users',
        tenant='tenant1',
        user='user1'
    ).inc()
    
    counter.labels(
        method='POST',
        endpoint='/api/v1/auth/login',
        tenant='tenant2',
        user='user2'
    ).inc()
    
    # Get counter values
    value = REGISTRY.get_sample_value(
        'api_calls_total',
        {
            'method': 'GET',
            'endpoint': '/api/v1/users',
            'tenant': 'tenant1',
            'user': 'user1'
        }
    )
    assert value == 1.0
    
    value = REGISTRY.get_sample_value(
        'api_calls_total',
        {
            'method': 'POST',
            'endpoint': '/api/v1/auth/login',
            'tenant': 'tenant2',
            'user': 'user2'
        }
    )
    assert value == 1.0 