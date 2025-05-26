# API routes

from flask import Blueprint, request, jsonify, current_app
from .models import BusinessCase
from .extensions import db
from .utils.identity import get_identity
from datetime import datetime
from .services.business_case_service import BusinessCaseService
from .schemas import BusinessCaseCreateSchema, BusinessCaseUpdateSchema

business_case_blueprint = Blueprint('business_cases', __name__)

@business_case_blueprint.route('', methods=['POST'])
def create_business_case() -> tuple:
    user_id, tenant_id = get_identity()
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
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
        return jsonify({'error': 'BusinessCase not found'}), 404
    return jsonify(case.to_dict())

@business_case_blueprint.route('/<int:case_id>', methods=['PUT'])
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
    return '', 204
