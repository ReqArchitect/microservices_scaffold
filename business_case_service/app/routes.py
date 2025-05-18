# API routes

from flask import Blueprint, request, jsonify, current_app
from .models import BusinessCase
from .extensions import db
from .utils.auth_client import auth_required
from datetime import datetime

business_case_blueprint = Blueprint('business_cases', __name__)

# Helper: get tenant_id and user_id from JWT (simulate multi-tenant)
def get_user_and_tenant():
    identity = get_jwt_identity()
    # In a real app, decode identity to get user_id and tenant_id
    if isinstance(identity, dict):
        return identity.get('user_id'), identity.get('tenant_id')
    return identity, request.headers.get('X-Tenant-ID')

@business_case_blueprint.route('', methods=['POST'])
@auth_required(permissions=['create_business_case'], allowed_roles=['admin', 'manager'], enforce_tenant=True)
def create_business_case():
    user = request.user
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
    required_fields = ['title']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field.capitalize()} is required'}), 400
    business_case = BusinessCase(
        user_id=user['id'],
        tenant_id=user['tenant_id'],
        title=data['title'],
        description=data.get('description'),
        justification=data.get('justification'),
        expected_benefits=data.get('expected_benefits'),
        risk_assessment=data.get('risk_assessment'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    )
    db.session.add(business_case)
    db.session.commit()
    return jsonify({'business_case': business_case.to_dict()}), 201

@business_case_blueprint.route('', methods=['GET'])
@auth_required(allowed_roles=['admin', 'manager', 'user'])
def list_business_cases():
    user = request.user
    query = BusinessCase.query.filter_by(tenant_id=user['tenant_id'])
    cases = query.all()
    return jsonify({'items': [c.to_dict() for c in cases]})

@business_case_blueprint.route('/<int:case_id>', methods=['GET'])
@auth_required(allowed_roles=['admin', 'manager', 'user'])
def get_business_case(case_id):
    user = request.user
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != user['tenant_id']:
        return jsonify({'error': 'BusinessCase not found'}), 404
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['PUT'])
@auth_required(allowed_roles=['admin', 'manager'])
def update_business_case(case_id):
    user = request.user
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != user['tenant_id']:
        return jsonify({'error': 'BusinessCase not found'}), 404
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
    for field in ['title', 'description', 'justification', 'expected_benefits', 'risk_assessment', 'start_date', 'end_date']:
        if field in data:
            if field in ['start_date', 'end_date']:
                setattr(case, field, datetime.strptime(data[field], '%Y-%m-%d').date() if data[field] else None)
            else:
                setattr(case, field, data[field])
    db.session.commit()
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['DELETE'])
@auth_required(allowed_roles=['admin'])
def delete_business_case(case_id):
    user = request.user
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != user['tenant_id']:
        return jsonify({'error': 'BusinessCase not found'}), 404
    db.session.delete(case)
    db.session.commit()
    return '', 204
