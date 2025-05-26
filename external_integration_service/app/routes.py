from flask import Blueprint, request, jsonify
from .service import IntegrationService, IntegrationEventService
from .schemas import IntegrationSchema, IntegrationEventSchema
from flasgger import swag_from
from datetime import datetime

integration_bp = Blueprint('integration', __name__, url_prefix='/api/v1/integration')

# Integration endpoints
@integration_bp.route('/integrations', methods=['POST'])
@swag_from({"summary": "Create integration", "responses": {201: {"description": "Created"}}})
def create_integration():
    data = request.get_json()
    integration = IntegrationService.create_integration(data)
    return IntegrationSchema().jsonify(integration), 201

@integration_bp.route('/integrations/<int:integration_id>', methods=['GET'])
@swag_from({"summary": "Get integration", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_integration(integration_id):
    integration = IntegrationService.get_integration(integration_id)
    if not integration:
        return jsonify({'message': 'Not found'}), 404
    return IntegrationSchema().jsonify(integration)

@integration_bp.route('/integrations', methods=['GET'])
@swag_from({"summary": "List integrations", "responses": {200: {"description": "OK"}}})
def get_integrations():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    integrations = IntegrationService.get_integrations(limit, offset)
    return IntegrationSchema(many=True).jsonify(integrations)

# IntegrationEvent endpoints
@integration_bp.route('/events', methods=['POST'])
@swag_from({"summary": "Create integration event", "responses": {201: {"description": "Created"}}})
def create_event():
    data = request.get_json()
    event = IntegrationEventService.create_event(data)
    return IntegrationEventSchema().jsonify(event), 201

@integration_bp.route('/events/<int:event_id>', methods=['GET'])
@swag_from({"summary": "Get integration event", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_event(event_id):
    event = IntegrationEventService.get_event(event_id)
    if not event:
        return jsonify({'message': 'Not found'}), 404
    return IntegrationEventSchema().jsonify(event)

@integration_bp.route('/events', methods=['GET'])
@swag_from({"summary": "List integration events", "responses": {200: {"description": "OK"}}})
def get_events():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    events = IntegrationEventService.get_events(limit, offset)
    return IntegrationEventSchema(many=True).jsonify(events)

@integration_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "external-integration-service", "timestamp": datetime.utcnow().isoformat()})

@integration_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_integrations": len(IntegrationService.get_integrations(1000, 0)), "total_events": len(IntegrationEventService.get_events(1000, 0))}) 