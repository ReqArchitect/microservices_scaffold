# API routes

from flask import Blueprint, request, jsonify, current_app
from .models import BusinessCase
from .extensions import db
from .utils.identity import get_identity
from datetime import datetime
<<<<<<< HEAD
from .services.business_case_service import BusinessCaseService
from .schemas import BusinessCaseCreateSchema, BusinessCaseUpdateSchema
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3

business_case_blueprint = Blueprint('business_cases', __name__)

@business_case_blueprint.route('', methods=['POST'])
<<<<<<< HEAD
def create_business_case() -> tuple:
=======
def create_business_case():
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
    user_id, tenant_id = get_identity()
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
<<<<<<< HEAD
    schema = BusinessCaseCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, business_case = BusinessCaseService.create(user_id, tenant_id, data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'business_case': business_case.to_dict()}), 201

@business_case_blueprint.route('', methods=['GET'])
def list_business_cases() -> tuple:
    _, tenant_id = get_identity()
    cases = BusinessCaseService.list(tenant_id)
    return jsonify({'items': [c.to_dict() for c in cases]})

@business_case_blueprint.route('/<int:case_id>', methods=['GET'])
def get_business_case(case_id: int) -> tuple:
    _, tenant_id = get_identity()
    case = BusinessCaseService.get(case_id, tenant_id)
    if not case:
=======
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
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
        return jsonify({'error': 'BusinessCase not found'}), 404
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['PUT'])
<<<<<<< HEAD
def update_business_case(case_id: int) -> tuple:
    _, tenant_id = get_identity()
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
    schema = BusinessCaseUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, case = BusinessCaseService.update(case_id, tenant_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['DELETE'])
def delete_business_case(case_id: int) -> tuple:
    _, tenant_id = get_identity()
    success = BusinessCaseService.delete(case_id, tenant_id)
    if not success:
        return jsonify({'error': 'BusinessCase not found'}), 404
=======
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
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
    return '', 204
