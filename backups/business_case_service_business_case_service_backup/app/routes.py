# API routes

from flask import Blueprint, request, jsonify, current_app
from .models import BusinessCase
from .extensions import db
from .utils.identity import get_identity
from datetime import datetime

business_case_blueprint = Blueprint('business_cases', __name__)

@business_case_blueprint.route('', methods=['POST'])
def create_business_case():
    user_id, tenant_id = get_identity()
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
    required_fields = ['title']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field.capitalize()} is required'}), 400
    business_case = BusinessCase(
        user_id=user_id,
        tenant_id=tenant_id,
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
def list_business_cases():
    _, tenant_id = get_identity()
    query = BusinessCase.query.filter_by(tenant_id=tenant_id)
    cases = query.all()
    return jsonify({'items': [c.to_dict() for c in cases]})

@business_case_blueprint.route('/<int:case_id>', methods=['GET'])
def get_business_case(case_id):
    _, tenant_id = get_identity()
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != tenant_id:
        return jsonify({'error': 'BusinessCase not found'}), 404
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['PUT'])
def update_business_case(case_id):
    _, tenant_id = get_identity()
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != tenant_id:
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
def delete_business_case(case_id):
    _, tenant_id = get_identity()
    case = BusinessCase.query.get(case_id)
    if not case or case.tenant_id != tenant_id:
        return jsonify({'error': 'BusinessCase not found'}), 404
    db.session.delete(case)
    db.session.commit()
    return '', 204
