"""
E2E test: Product Discovery Dashboard elements (KPI, Initiative, Business Case, Business Model Canvas) can be linked to Application Layer elements.
This test simulates the workflow across services using sample data.
"""
import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

BASE_URLS = {
    'kpi': os.getenv('KPI_SERVICE_URL', 'http://localhost:5007/api'),
    'initiative': os.getenv('INITIATIVE_SERVICE_URL', 'http://localhost:5008/api'),
    'business_case': os.getenv('BUSINESS_CASE_SERVICE_URL', 'http://localhost:5009/api'),
    'canvas': os.getenv('CANVAS_SERVICE_URL', 'http://localhost:5010/api'),
    'application': os.getenv('APPLICATION_LAYER_SERVICE_URL', 'http://localhost:5003/api'),
    'auth': os.getenv('AUTH_SERVICE_URL', 'http://localhost:5000/api/v1/auth'),
}

@pytest.fixture(scope="module")
def jwt_token():
    # Adjust credentials as needed for your test environment
    resp = requests.post(f"{BASE_URLS['auth']}/login", json={"email": "testuser@example.com", "password": "testpass", "tenant_id": 1})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_product_discovery_to_application_workflow(jwt_token):
    headers = {"Authorization": f"Bearer {jwt_token}"}

    # 1. Create ApplicationComponent
    app_resp = requests.post(f"{BASE_URLS['application']}/application_components", json={"name": "Test AppComp", "description": "E2E link test"}, headers=headers)
    assert app_resp.status_code == 201
    app_id = app_resp.json()["id"]

    # 2. Create KPI and link to ApplicationComponent (simulate link via API or update)
    kpi_resp = requests.post(f"{BASE_URLS['kpi']}/kpis", json={"name": "Test KPI", "description": "E2E KPI", "application_component_id": app_id}, headers=headers)
    assert kpi_resp.status_code == 201
    kpi_id = kpi_resp.json()["id"]

    # 3. Create Initiative and link to ApplicationComponent
    initiative_resp = requests.post(f"{BASE_URLS['initiative']}/initiatives", json={"name": "Test Initiative", "application_component_id": app_id}, headers=headers)
    assert initiative_resp.status_code == 201
    initiative_id = initiative_resp.json()["id"]

    # 4. Create Business Case and link to ApplicationComponent
    bc_resp = requests.post(f"{BASE_URLS['business_case']}/business_cases", json={"name": "Test BC", "application_component_id": app_id}, headers=headers)
    assert bc_resp.status_code == 201
    bc_id = bc_resp.json()["id"]

    # 5. Create Business Model Canvas and link to ApplicationComponent
    canvas_resp = requests.post(f"{BASE_URLS['canvas']}/canvases", json={"name": "Test Canvas", "application_component_id": app_id}, headers=headers)
    assert canvas_resp.status_code == 201
    canvas_id = canvas_resp.json()["id"]

    # 6. Fetch and assert links exist (example for KPI)
    kpi_get = requests.get(f"{BASE_URLS['kpi']}/kpis/{kpi_id}", headers=headers)
    assert kpi_get.status_code == 200
    assert kpi_get.json().get("application_component_id") == app_id

    # Repeat similar assertions for other entities as needed
