from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_service_service import BusinessServiceService
from .schemas import BusinessServiceCreateSchema, BusinessServiceUpdateSchema, BusinessServiceResponseSchema
from flasgger import swag_from

bp_business_service = Blueprint('business_services', __name__, url_prefix='/business_services')

@swag_from({
    "tags": ["BusinessService"],
    "summary": "List all business services",
    "responses": {200: {"description": "A list of business services"}},
})
@bp_business_service.route('', methods=['GET'])
@jwt_required()
def list_business_services():
    services = BusinessServiceService.list()
    schema = BusinessServiceResponseSchema(many=True)
    return jsonify(schema.dump(services)), 200

@swag_from({
    "tags": ["BusinessService"],
    "summary": "Create a business service",
    "parameters": [{"in": "body", "schema": BusinessServiceCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_service.route('', methods=['POST'])
@jwt_required()
def create_business_service():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessServiceCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, service = BusinessServiceService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': service.id}), 201

@swag_from({
    "tags": ["BusinessService"],
    "summary": "Get a business service by ID",
    "parameters": [{"in": "path", "name": "service_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business service found"}, 404: {"description": "Not found"}},
})
@bp_business_service.route('/<int:service_id>', methods=['GET'])
@jwt_required()
def get_business_service(service_id: int):
    service = BusinessServiceService.get(service_id)
    if not service:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessServiceResponseSchema()
    return jsonify(schema.dump(service)), 200

@swag_from({
    "tags": ["BusinessService"],
    "summary": "Update a business service",
    "parameters": [
        {"in": "path", "name": "service_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessServiceUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_service.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_business_service(service_id: int):
    data = request.get_json()
    schema = BusinessServiceUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, service = BusinessServiceService.update(service_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': service.id})

@swag_from({
    "tags": ["BusinessService"],
    "summary": "Delete a business service",
    "parameters": [{"in": "path", "name": "service_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_service.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_business_service(service_id: int):
    success = BusinessServiceService.delete(service_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 