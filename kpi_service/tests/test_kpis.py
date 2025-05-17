import pytest
from app.models import KPI
from app.extensions import db
from flask_jwt_extended import create_access_token, get_jwt

def test_create_kpi(client, business_case):
    token = create_access_token(
        identity='user_1',
        additional_claims={'tenant_id': 'tenant_1'}
    )
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'business_case_id': business_case,
        'title': 'Increase Revenue',
        'metric': 'Revenue',
        'target_value': 100000.0
    }
    response = client.post('/api/kpis/', json=data, headers=headers)
    if response.status_code != 201:
        print('RESPONSE JSON:', response.get_json())
    assert response.status_code == 201

def test_get_kpis(client, business_case):
    token = create_access_token(
        identity='user_1',
        additional_claims={'tenant_id': 'tenant_1'}
    )
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/kpis/', headers=headers)
    assert response.status_code == 200

def test_update_kpi(client, business_case):
    token = create_access_token(
        identity='user_1',
        additional_claims={'tenant_id': 'tenant_1'}
    )
    headers = {'Authorization': f'Bearer {token}'}
    # Create a KPI to update
    kpi = KPI(
        business_case_id=business_case,
        tenant_id='tenant_1',
        owner_id='user_1',
        title='To Update',
        metric='Metric',
        target_value=1.0
    )
    db.session.add(kpi)
    db.session.commit()
    data = {'title': 'Updated Title'}
    response = client.put(f'/api/kpis/{kpi.id}', json=data, headers=headers)
    assert response.status_code == 200

def test_delete_kpi(client, business_case):
    token = create_access_token(
        identity='user_1',
        additional_claims={'tenant_id': 'tenant_1'}
    )
    headers = {'Authorization': f'Bearer {token}'}
    # Create a KPI to delete
    kpi = KPI(
        business_case_id=business_case,
        tenant_id='tenant_1',
        owner_id='user_1',
        title='To Delete',
        metric='Metric',
        target_value=1.0
    )
    db.session.add(kpi)
    db.session.commit()
    response = client.delete(f'/api/kpis/{kpi.id}', headers=headers)
    assert response.status_code == 204