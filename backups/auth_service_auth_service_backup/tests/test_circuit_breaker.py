import pytest
import time
from flask import Flask, jsonify
from common_utils.circuit_breaker import CircuitBreaker

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['CIRCUIT_BREAKER_FAILURE_THRESHOLD'] = 3
    app.config['CIRCUIT_BREAKER_RECOVERY_TIMEOUT'] = 5
    app.config['CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT'] = 2
    return app

@pytest.fixture
def circuit_breaker(app):
    """Create a circuit breaker for testing."""
    return CircuitBreaker(
        failure_threshold=app.config['CIRCUIT_BREAKER_FAILURE_THRESHOLD'],
        recovery_timeout=app.config['CIRCUIT_BREAKER_RECOVERY_TIMEOUT'],
        half_open_timeout=app.config['CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT']
    )

def test_circuit_breaker_closed_state(circuit_breaker):
    """Test circuit breaker in closed state."""
    # Circuit breaker should be closed initially
    assert circuit_breaker.is_closed()
    
    # Execute successful operation
    result = circuit_breaker.execute(lambda: "success")
    assert result == "success"
    
    # Circuit breaker should remain closed
    assert circuit_breaker.is_closed()

def test_circuit_breaker_open_state(circuit_breaker):
    """Test circuit breaker in open state."""
    # Execute failing operations
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    # Circuit breaker should be open
    assert circuit_breaker.is_open()
    
    # Any operation should fail with CircuitBreakerError
    with pytest.raises(CircuitBreakerError):
        circuit_breaker.execute(lambda: "success")

def test_circuit_breaker_half_open_state(circuit_breaker):
    """Test circuit breaker in half-open state."""
    # Open the circuit breaker
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    # Wait for recovery timeout
    time.sleep(5)
    
    # Circuit breaker should be half-open
    assert circuit_breaker.is_half_open()
    
    # Successful operation should close the circuit
    result = circuit_breaker.execute(lambda: "success")
    assert result == "success"
    assert circuit_breaker.is_closed()

def test_circuit_breaker_recovery(circuit_breaker):
    """Test circuit breaker recovery."""
    # Open the circuit breaker
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    # Wait for recovery timeout
    time.sleep(5)
    
    # Failed operation should open the circuit again
    with pytest.raises(CircuitBreakerError):
        circuit_breaker.execute(lambda: 1/0)
    
    assert circuit_breaker.is_open()

def test_circuit_breaker_reset(circuit_breaker):
    """Test circuit breaker reset."""
    # Open the circuit breaker
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    # Reset the circuit breaker
    circuit_breaker.reset()
    
    # Circuit breaker should be closed
    assert circuit_breaker.is_closed()
    
    # Should be able to execute operations
    result = circuit_breaker.execute(lambda: "success")
    assert result == "success"

def test_circuit_breaker_custom_exceptions(circuit_breaker):
    """Test circuit breaker with custom exceptions."""
    # Define custom exception
    class CustomError(Exception):
        pass
    
    # Execute operation that raises custom exception
    with pytest.raises(CustomError):
        def raise_custom_error():
            raise CustomError()
        circuit_breaker.execute(raise_custom_error)
    
    # Circuit breaker should count this as a failure
    assert circuit_breaker.failure_count == 1

def test_circuit_breaker_ignore_exceptions(circuit_breaker):
    """Test circuit breaker with ignored exceptions."""
    # Define ignored exception
    class IgnoredError(Exception):
        pass
    
    # Configure circuit breaker to ignore specific exception
    circuit_breaker.ignore_exceptions = (IgnoredError,)
    
    # Execute operation that raises ignored exception
    with pytest.raises(IgnoredError):
        def raise_ignored_error():
            raise IgnoredError()
        circuit_breaker.execute(raise_ignored_error)
    
    # Circuit breaker should not count this as a failure
    assert circuit_breaker.failure_count == 0

def test_circuit_breaker_timeout(circuit_breaker):
    """Test circuit breaker with operation timeout."""
    # Execute long-running operation
    with pytest.raises(CircuitBreakerError):
        circuit_breaker.execute(
            lambda: time.sleep(10),
            timeout=1
        )
    
    # Circuit breaker should count this as a failure
    assert circuit_breaker.failure_count == 1

def test_circuit_breaker_state_transitions(circuit_breaker):
    """Test circuit breaker state transitions."""
    # Initial state should be closed
    assert circuit_breaker.is_closed()
    
    # Open the circuit breaker
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    assert circuit_breaker.is_open()
    
    # Wait for recovery timeout
    time.sleep(5)
    
    assert circuit_breaker.is_half_open()
    
    # Successful operation should close the circuit
    result = circuit_breaker.execute(lambda: "success")
    assert result == "success"
    assert circuit_breaker.is_closed()

def test_circuit_breaker_metrics(circuit_breaker):
    """Test circuit breaker metrics."""
    # Initial metrics
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.last_failure_time is None
    
    # Record failures
    for _ in range(3):
        with pytest.raises(CircuitBreakerError):
            circuit_breaker.execute(lambda: 1/0)
    
    assert circuit_breaker.failure_count == 3
    assert circuit_breaker.last_failure_time is not None
    
    # Reset metrics
    circuit_breaker.reset()
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.last_failure_time is None

def test_circuit_breaker_concurrent_operations(circuit_breaker):
    """Test circuit breaker with concurrent operations."""
    import threading
    
    def operation():
        try:
            circuit_breaker.execute(lambda: 1/0)
        except CircuitBreakerError:
            pass
    
    # Create multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=operation)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Circuit breaker should be open
    assert circuit_breaker.is_open()
    assert circuit_breaker.failure_count >= 3 