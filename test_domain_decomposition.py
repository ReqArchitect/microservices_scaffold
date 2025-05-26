import os
import sys
import pytest

def run_tests():
    """Run integration tests for domain decomposition"""
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Run strategy service tests
    print("Running Strategy Service Tests...")
    strategy_result = pytest.main(['strategy_service/tests/test_event_flow.py', '-v'])
    
    # Run business layer service tests
    print("\nRunning Business Layer Service Tests...")
    business_result = pytest.main(['business_layer_service/tests/test_events.py', '-v'])
    
    # Run application layer service tests
    print("\nRunning Application Layer Service Tests...")
    app_result = pytest.main(['application_layer_service/tests/test_events.py', '-v'])
    
    return all(result == 0 for result in [strategy_result, business_result, app_result])

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
