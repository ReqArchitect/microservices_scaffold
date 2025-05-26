from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_collaboration_service import BusinessCollaborationService
from .schemas import BusinessCollaborationCreateSchema, BusinessCollaborationUpdateSchema, BusinessCollaborationResponseSchema
from flasgger import swag_from

bp_business_collab = Blueprint('business_collaborations', __name__, url_prefix='/business_collaborations')

@swag_from({
    "tags": ["BusinessCollaboration"],
    "summary": "List all business collaborations",
    "responses": {200: {"description": "A list of business collaborations"}},
})
@bp_business_collab.route('', methods=['GET'])
@jwt_required()
def list_business_collaborations():
    collaborations = BusinessCollaborationService.list()
    schema = BusinessCollaborationResponseSchema(many=True)
    return jsonify(schema.dump(collaborations)), 200

@swag_from({
    "tags": ["BusinessCollaboration"],
    "summary": "Create a business collaboration",
    "parameters": [{"in": "body", "schema": BusinessCollaborationCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_collab.route('', methods=['POST'])
@jwt_required()
def create_business_collaboration():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessCollaborationCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, collab = BusinessCollaborationService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': collab.id}), 201

@swag_from({
    "tags": ["BusinessCollaboration"],
    "summary": "Get a business collaboration by ID",
    "parameters": [{"in": "path", "name": "collab_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business collaboration found"}, 404: {"description": "Not found"}},
})
@bp_business_collab.route('/<int:collab_id>', methods=['GET'])
@jwt_required()
def get_business_collaboration(collab_id: int):
    collab = BusinessCollaborationService.get(collab_id)
    if not collab:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessCollaborationResponseSchema()
    return jsonify(schema.dump(collab)), 200

@swag_from({
    "tags": ["BusinessCollaboration"],
    "summary": "Update a business collaboration",
    "parameters": [
        {"in": "path", "name": "collab_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessCollaborationUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_collab.route('/<int:collab_id>', methods=['PUT'])
@jwt_required()
def update_business_collaboration(collab_id: int):
    data = request.get_json()
    schema = BusinessCollaborationUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, collab = BusinessCollaborationService.update(collab_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': collab.id})

@swag_from({
    "tags": ["BusinessCollaboration"],
    "summary": "Delete a business collaboration",
    "parameters": [{"in": "path", "name": "collab_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_collab.route('/<int:collab_id>', methods=['DELETE'])
@jwt_required()
def delete_business_collaboration(collab_id: int):
    success = BusinessCollaborationService.delete(collab_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 