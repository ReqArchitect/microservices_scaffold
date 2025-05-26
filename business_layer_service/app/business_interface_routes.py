from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_interface_service import BusinessInterfaceService
from .schemas import BusinessInterfaceCreateSchema, BusinessInterfaceUpdateSchema, BusinessInterfaceResponseSchema
from flasgger import swag_from

bp_business_interface = Blueprint('business_interfaces', __name__, url_prefix='/business_interfaces')

@swag_from({
    "tags": ["BusinessInterface"],
    "summary": "List all business interfaces",
    "responses": {200: {"description": "A list of business interfaces"}},
})
@bp_business_interface.route('', methods=['GET'])
@jwt_required()
def list_business_interfaces():
    interfaces = BusinessInterfaceService.list()
    schema = BusinessInterfaceResponseSchema(many=True)
    return jsonify(schema.dump(interfaces)), 200

@swag_from({
    "tags": ["BusinessInterface"],
    "summary": "Create a business interface",
    "parameters": [{"in": "body", "schema": BusinessInterfaceCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_interface.route('', methods=['POST'])
@jwt_required()
def create_business_interface():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessInterfaceCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, interface = BusinessInterfaceService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': interface.id}), 201

@swag_from({
    "tags": ["BusinessInterface"],
    "summary": "Get a business interface by ID",
    "parameters": [{"in": "path", "name": "interface_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business interface found"}, 404: {"description": "Not found"}},
})
@bp_business_interface.route('/<int:interface_id>', methods=['GET'])
@jwt_required()
def get_business_interface(interface_id: int):
    interface = BusinessInterfaceService.get(interface_id)
    if not interface:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessInterfaceResponseSchema()
    return jsonify(schema.dump(interface)), 200

@swag_from({
    "tags": ["BusinessInterface"],
    "summary": "Update a business interface",
    "parameters": [
        {"in": "path", "name": "interface_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessInterfaceUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_interface.route('/<int:interface_id>', methods=['PUT'])
@jwt_required()
def update_business_interface(interface_id: int):
    data = request.get_json()
    schema = BusinessInterfaceUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, interface = BusinessInterfaceService.update(interface_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': interface.id})

@swag_from({
    "tags": ["BusinessInterface"],
    "summary": "Delete a business interface",
    "parameters": [{"in": "path", "name": "interface_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_interface.route('/<int:interface_id>', methods=['DELETE'])
@jwt_required()
def delete_business_interface(interface_id: int):
    success = BusinessInterfaceService.delete(interface_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 