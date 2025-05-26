import pytest
from datetime import datetime, timedelta
import json

@pytest.fixture
def test_tenant_id():
    """Provide a test tenant ID."""
    return 1

@pytest.fixture
def test_user_id():
    """Provide a test user ID."""
    return 1

# Sample real-world initiatives data
REAL_INITIATIVES = [
    {
        "title": "Digital Transformation Initiative",
        "description": "Modernize legacy systems and implement cloud-first strategy",
        "strategic_objective": "Technology Modernization",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "status": "active",
        "priority": "high",
        "progress": 25,
        "tags": ["digital", "cloud", "modernization"]
    },
    {
        "title": "Customer Experience Enhancement",
        "description": "Improve customer satisfaction through digital channels",
        "strategic_objective": "Customer Success",
        "start_date": "2024-02-01",
        "end_date": "2024-08-31",
        "status": "active",
        "priority": "medium",
        "progress": 40,
        "tags": ["customer", "experience", "digital"]
    }
]

def test_create_real_initiatives(client, auth_headers):
    """Test creating initiatives with real-world data."""
    created_initiatives = []

    for initiative_data in REAL_INITIATIVES:
        response = client.post(
            '/api/initiatives',
            headers=auth_headers,
            json=initiative_data
        )
        if response.status_code != 201:
            print(f"Failed to create initiative. Status code: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
            print(f"Request data: {initiative_data}")
        assert response.status_code == 201
        created_initiatives.append(response.get_json()['initiative'])
    
    return created_initiatives

def test_filter_initiatives_by_strategic_objective(client, auth_headers):
    """Test filtering initiatives by strategic objective."""
    # First create the initiatives
    test_create_real_initiatives(client, auth_headers)
    
    # Test filtering by strategic objective
    response = client.get(
        '/api/initiatives?strategic_objective=Technology Modernization',
        headers=auth_headers
    )
    assert response.status_code == 200
    initiatives = response.get_json()['items']
    assert len(initiatives) > 0
    for initiative in initiatives:
        assert initiative['strategic_objective'] == 'Technology Modernization'

def test_filter_initiatives_by_priority(client, auth_headers):
    """Test filtering initiatives by priority."""
    # First create the initiatives
    test_create_real_initiatives(client, auth_headers)
    
    # Test filtering
    response = client.get(
        '/api/initiatives?priority=high',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0
    assert all(item['priority'] == 'high' for item in data['items'])

def test_filter_initiatives_by_tags(client, auth_headers):
    """Test filtering initiatives by tags."""
    # First create the initiatives
    test_create_real_initiatives(client, auth_headers)
    
    # Test filtering
    response = client.get(
        '/api/initiatives?tags=digital',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0
    assert all('digital' in item['tags'] for item in data['items'])

def test_update_initiative_progress(client, auth_headers):
    """Test updating initiative progress."""
    # First create the initiatives
    initiatives = test_create_real_initiatives(client, auth_headers)
    
    # Update progress
    initiative_id = initiatives[0]['id']
    response = client.put(
        f'/api/initiatives/{initiative_id}',
        headers=auth_headers,
        json={'progress': 75}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['progress'] == 75

def test_bulk_status_update(client, auth_headers):
    """Test updating status of multiple initiatives."""
    # First create the initiatives
    initiatives = test_create_real_initiatives(client, auth_headers)
    
    # Update status for all initiatives
    for initiative in initiatives:
        response = client.put(
            f'/api/initiatives/{initiative["id"]}',
            headers=auth_headers,
            json={'status': 'completed'}
        )
        assert response.status_code == 200
    
    # Verify all initiatives are completed
    response = client.get(
        '/api/initiatives?status=completed',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) == len(initiatives)
    assert all(item['status'] == 'completed' for item in data['items'])

def test_initiative_lifecycle(client, auth_headers):
    """Test the complete lifecycle of an initiative."""
    # Create initiative
    initiative_data = REAL_INITIATIVES[0]
    response = client.post(
        '/api/initiatives',
        headers=auth_headers,
        json=initiative_data
    )
    assert response.status_code == 201
    initiative = json.loads(response.data)['initiative']
    # Update progress
    response = client.put(
        f'/api/initiatives/{initiative["id"]}',
        headers=auth_headers,
        json={'progress': 50}
    )
    assert response.status_code == 200
    # Complete initiative
    response = client.put(
        f'/api/initiatives/{initiative["id"]}',
        headers=auth_headers,
        json={'status': 'completed', 'progress': 100}
    )
    assert response.status_code == 200
    # Verify final state
    response = client.get(
        f'/api/initiatives/{initiative["id"]}',
        headers=auth_headers
    )
    assert response.status_code == 200
    final_state = json.loads(response.data)
    assert final_state['status'] == 'completed'
    assert final_state['progress'] == 100

def test_initiative_search(client, auth_headers):
    """Test searching initiatives by various criteria."""
    # First create the initiatives
    test_create_real_initiatives(client, auth_headers)
    
    # Test search by title
    response = client.get(
        '/api/initiatives?search=Digital',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0
    assert any('Digital' in item['title'] for item in data['items'])
    
    # Test search by description
    response = client.get(
        '/api/initiatives?search=customer',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0
    assert any('customer' in item['description'].lower() for item in data['items']) 