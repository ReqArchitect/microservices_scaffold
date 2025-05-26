from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_interaction_service import BusinessInteractionService
from .schemas import BusinessInteractionCreateSchema, BusinessInteractionUpdateSchema, BusinessInteractionResponseSchema
from flasgger import swag_from

bp_business_interaction = Blueprint('business_interactions', __name__, url_prefix='/business_interactions')

@swag_from({
    "tags": ["BusinessInteraction"],
    "summary": "List all business interactions",
    "responses": {200: {"description": "A list of business interactions"}},
})
@bp_business_interaction.route('', methods=['GET'])
@jwt_required()
def list_business_interactions():
    interactions = BusinessInteractionService.list()
    schema = BusinessInteractionResponseSchema(many=True)
    return jsonify(schema.dump(interactions)), 200

@swag_from({
    "tags": ["BusinessInteraction"],
    "summary": "Create a business interaction",
    "parameters": [{"in": "body", "schema": BusinessInteractionCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_interaction.route('', methods=['POST'])
@jwt_required()
def create_business_interaction():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessInteractionCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, interaction = BusinessInteractionService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': interaction.id}), 201

@swag_from({
    "tags": ["BusinessInteraction"],
    "summary": "Get a business interaction by ID",
    "parameters": [{"in": "path", "name": "interaction_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business interaction found"}, 404: {"description": "Not found"}},
})
@bp_business_interaction.route('/<int:interaction_id>', methods=['GET'])
@jwt_required()
def get_business_interaction(interaction_id: int):
    interaction = BusinessInteractionService.get(interaction_id)
    if not interaction:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessInteractionResponseSchema()
    return jsonify(schema.dump(interaction)), 200

@swag_from({
    "tags": ["BusinessInteraction"],
    "summary": "Update a business interaction",
    "parameters": [
        {"in": "path", "name": "interaction_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessInteractionUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_interaction.route('/<int:interaction_id>', methods=['PUT'])
@jwt_required()
def update_business_interaction(interaction_id: int):
    data = request.get_json()
    schema = BusinessInteractionUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, interaction = BusinessInteractionService.update(interaction_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': interaction.id})

@swag_from({
    "tags": ["BusinessInteraction"],
    "summary": "Delete a business interaction",
    "parameters": [{"in": "path", "name": "interaction_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_interaction.route('/<int:interaction_id>', methods=['DELETE'])
@jwt_required()
def delete_business_interaction(interaction_id: int):
    success = BusinessInteractionService.delete(interaction_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 