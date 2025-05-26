from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_object_service import BusinessObjectService
from .schemas import BusinessObjectCreateSchema, BusinessObjectUpdateSchema, BusinessObjectResponseSchema
from flasgger import swag_from

bp_business_object = Blueprint('business_objects', __name__, url_prefix='/business_objects')

@swag_from({
    "tags": ["BusinessObject"],
    "summary": "List all business objects",
    "responses": {200: {"description": "A list of business objects"}},
})
@bp_business_object.route('', methods=['GET'])
@jwt_required()
def list_business_objects():
    objects = BusinessObjectService.list()
    schema = BusinessObjectResponseSchema(many=True)
    return jsonify(schema.dump(objects)), 200

@swag_from({
    "tags": ["BusinessObject"],
    "summary": "Create a business object",
    "parameters": [{"in": "body", "schema": BusinessObjectCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_object.route('', methods=['POST'])
@jwt_required()
def create_business_object():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessObjectCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, obj = BusinessObjectService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': obj.id}), 201

@swag_from({
    "tags": ["BusinessObject"],
    "summary": "Get a business object by ID",
    "parameters": [{"in": "path", "name": "object_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business object found"}, 404: {"description": "Not found"}},
})
@bp_business_object.route('/<int:object_id>', methods=['GET'])
@jwt_required()
def get_business_object(object_id: int):
    obj = BusinessObjectService.get(object_id)
    if not obj:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessObjectResponseSchema()
    return jsonify(schema.dump(obj)), 200

@swag_from({
    "tags": ["BusinessObject"],
    "summary": "Update a business object",
    "parameters": [
        {"in": "path", "name": "object_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessObjectUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_object.route('/<int:object_id>', methods=['PUT'])
@jwt_required()
def update_business_object(object_id: int):
    data = request.get_json()
    schema = BusinessObjectUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, obj = BusinessObjectService.update(object_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': obj.id})

@swag_from({
    "tags": ["BusinessObject"],
    "summary": "Delete a business object",
    "parameters": [{"in": "path", "name": "object_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_object.route('/<int:object_id>', methods=['DELETE'])
@jwt_required()
def delete_business_object(object_id: int):
    success = BusinessObjectService.delete(object_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 