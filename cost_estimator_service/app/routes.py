from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db
from .services import CostModelService
from .schemas import CostModelSchema
from flasgger import swag_from

bp = Blueprint('cost_model', __name__, url_prefix='/cost_models')

@swag_from({})
@bp.route('', methods=['GET'])
@jwt_required()
def list_cost_models():
    items = CostModelService.list()
    return jsonify(CostModelSchema(many=True).dump(items)), 200

@swag_from({})
@bp.route('', methods=['POST'])
@jwt_required()
def create_cost_model():
    data = request.get_json()
    schema = CostModelSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    model = CostModelService.create(data)
    return jsonify(schema.dump(model)), 201

@swag_from({})
@bp.route('/<int:model_id>', methods=['GET'])
@jwt_required()
def get_cost_model(model_id):
    model = CostModelService.get(model_id)
    if not model:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(CostModelSchema().dump(model)), 200

@swag_from({})
@bp.route('/<int:model_id>', methods=['PUT'])
@jwt_required()
def update_cost_model(model_id):
    data = request.get_json()
    model = CostModelService.update(model_id, data)
    if not model:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(CostModelSchema().dump(model)), 200

@swag_from({})
@bp.route('/<int:model_id>', methods=['DELETE'])
@jwt_required()
def delete_cost_model(model_id):
    if not CostModelService.delete(model_id):
        return jsonify({'error': 'Not found'}), 404
    return '', 204

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@bp.route('/metrics', methods=['GET'])
def metrics():
    return 'cost_estimator_service_up 1\n', 200, {'Content-Type': 'text/plain'}
