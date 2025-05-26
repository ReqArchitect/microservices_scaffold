import os
import requests
import pytest
import dotenv

dotenv.load_dotenv()

SERVICES = {
    'user_service': os.environ.get('USER_SERVICE_URL', 'http://localhost:5000/health'),
    'auth_service': os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001/health'),
    'initiative_service': os.environ.get('INITIATIVE_SERVICE_URL', 'http://localhost:5002/health'),
    'kpi_service': os.environ.get('KPI_SERVICE_URL', 'http://localhost:5003/health'),
    'business_case_service': os.environ.get('BUSINESS_CASE_SERVICE_URL', 'http://localhost:5004/health'),
    'strategy_service': os.environ.get('STRATEGY_SERVICE_URL', 'http://localhost:5005/health'),
}

@pytest.mark.parametrize('service_name, url', SERVICES.items())
def test_service_health(service_name, url):
    resp = requests.get(url)
    assert resp.status_code == 200, f"{service_name} health check failed: {resp.text}"
    # Optionally check for a 'status' field in the response
    try:
        data = resp.json()
        assert data.get('status', '').lower() in ('healthy', 'ok', 'up'), f"{service_name} unhealthy: {data}"
    except Exception:
        # If not JSON, just pass on status code
        pass 