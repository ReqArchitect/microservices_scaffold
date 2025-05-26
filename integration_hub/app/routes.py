from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db
from .services import IntegrationService
from .schemas import IntegrationSchema
from flasgger import swag_from

bp = Blueprint('integration', __name__, url_prefix='/integrations')

@swag_from({})
@bp.route('', methods=['GET'])
@jwt_required()
def list_integrations():
    items = IntegrationService.list()
    return jsonify(IntegrationSchema(many=True).dump(items)), 200

@swag_from({})
@bp.route('', methods=['POST'])
@jwt_required()
def create_integration():
    data = request.get_json()
    schema = IntegrationSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    integration = IntegrationService.create(data)
    return jsonify(schema.dump(integration)), 201

@swag_from({})
@bp.route('/<int:integration_id>', methods=['GET'])
@jwt_required()
def get_integration(integration_id):
    integration = IntegrationService.get(integration_id)
    if not integration:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(IntegrationSchema().dump(integration)), 200

@swag_from({})
@bp.route('/<int:integration_id>', methods=['PUT'])
@jwt_required()
def update_integration(integration_id):
    data = request.get_json()
    integration = IntegrationService.update(integration_id, data)
    if not integration:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(IntegrationSchema().dump(integration)), 200

@swag_from({})
@bp.route('/<int:integration_id>', methods=['DELETE'])
@jwt_required()
def delete_integration(integration_id):
    if not IntegrationService.delete(integration_id):
        return jsonify({'error': 'Not found'}), 404
    return '', 204

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@bp.route('/metrics', methods=['GET'])
def metrics():
    return 'integration_hub_up 1\n', 200, {'Content-Type': 'text/plain'}
