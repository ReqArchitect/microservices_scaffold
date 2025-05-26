from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.business_event_service import BusinessEventService
from .schemas import BusinessEventCreateSchema, BusinessEventUpdateSchema, BusinessEventResponseSchema
from flasgger import swag_from

bp_business_event = Blueprint('business_events', __name__, url_prefix='/business_events')

@swag_from({
    "tags": ["BusinessEvent"],
    "summary": "List all business events",
    "responses": {200: {"description": "A list of business events"}},
})
@bp_business_event.route('', methods=['GET'])
@jwt_required()
def list_business_events():
    events = BusinessEventService.list()
    schema = BusinessEventResponseSchema(many=True)
    return jsonify(schema.dump(events)), 200

@swag_from({
    "tags": ["BusinessEvent"],
    "summary": "Create a business event",
    "parameters": [{"in": "body", "schema": BusinessEventCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_business_event.route('', methods=['POST'])
@jwt_required()
def create_business_event():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessEventCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, event = BusinessEventService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': event.id}), 201

@swag_from({
    "tags": ["BusinessEvent"],
    "summary": "Get a business event by ID",
    "parameters": [{"in": "path", "name": "event_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Business event found"}, 404: {"description": "Not found"}},
})
@bp_business_event.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_business_event(event_id: int):
    event = BusinessEventService.get(event_id)
    if not event:
        return jsonify({'error': 'Not found'}), 404
    schema = BusinessEventResponseSchema()
    return jsonify(schema.dump(event)), 200

@swag_from({
    "tags": ["BusinessEvent"],
    "summary": "Update a business event",
    "parameters": [
        {"in": "path", "name": "event_id", "type": "integer", "required": True},
        {"in": "body", "schema": BusinessEventUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_business_event.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_business_event(event_id: int):
    data = request.get_json()
    schema = BusinessEventUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, event = BusinessEventService.update(event_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': event.id})

@swag_from({
    "tags": ["BusinessEvent"],
    "summary": "Delete a business event",
    "parameters": [{"in": "path", "name": "event_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_business_event.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_business_event(event_id: int):
    success = BusinessEventService.delete(event_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 