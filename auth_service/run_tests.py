import pytest
import sys

if __name__ == '__main__':
    # Run tests with coverage
    sys.exit(pytest.main([
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html',
        'tests/'
    ])) 