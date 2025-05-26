from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_function_service import BusinessFunctionService
from .schemas import BusinessFunctionCreateSchema, BusinessFunctionUpdateSchema, BusinessFunctionResponseSchema
from flasgger import swag_from

bp_business_function = Blueprint('business_functions', __name__, url_prefix='/business_functions')

@swag_from({
    "tags": ["BusinessFunction"],
    "summary": "List all business functions",
    "responses": {200: {"description": "A list of business functions"}},
})
@bp_business_function.route('', methods=['GET'])
@jwt_required()
def list_business_functions():
    functions = BusinessFunctionService.list()
    schema = BusinessFunctionResponseSchema(many=True)
    return jsonify(schema.dump(functions)), 200

@swag_from({
    "tags": ["BusinessFunction"],
    "summary": "Create a business function",
    "parameters": [{"in": "body", "schema": BusinessFunctionCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_function.route('', methods=['POST'])
@jwt_required()
def create_business_function():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessFunctionCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, function = BusinessFunctionService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': function.id}), 201

@swag_from({
    "tags": ["BusinessFunction"],
    "summary": "Get a business function by ID",
    "parameters": [{"in": "path", "name": "function_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business function found"}, 404: {"description": "Not found"}},
})
@bp_business_function.route('/<int:function_id>', methods=['GET'])
@jwt_required()
def get_business_function(function_id: int):
    function = BusinessFunctionService.get(function_id)
    if not function:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessFunctionResponseSchema()
    return jsonify(schema.dump(function)), 200

@swag_from({
    "tags": ["BusinessFunction"],
    "summary": "Update a business function",
    "parameters": [
        {"in": "path", "name": "function_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessFunctionUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_function.route('/<int:function_id>', methods=['PUT'])
@jwt_required()
def update_business_function(function_id: int):
    data = request.get_json()
    schema = BusinessFunctionUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, function = BusinessFunctionService.update(function_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': function.id})

@swag_from({
    "tags": ["BusinessFunction"],
    "summary": "Delete a business function",
    "parameters": [{"in": "path", "name": "function_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_function.route('/<int:function_id>', methods=['DELETE'])
@jwt_required()
def delete_business_function(function_id: int):
    success = BusinessFunctionService.delete(function_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 