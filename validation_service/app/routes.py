from flask import Blueprint, request, jsonify, current_app
import requests
import logging
from flask_jwt_extended import jwt_required
from .models import db
from .services import PolicyService
from .schemas import PolicySchema
from flasgger import swag_from

bp = Blueprint('validation', __name__)

@bp.route('/validate', methods=['POST'])
def validate():
    payload = request.json
    opa_url = current_app.config['OPA_URL']
    # Call OPA for policy validation
    opa_input = {'input': payload}
    try:
        opa_response = requests.post(opa_url, json=opa_input)
        opa_result = opa_response.json()
        allowed = opa_result.get('result', False)
        log_msg = f"OPA validation: allowed={allowed}, input={payload}"
        logging.info(log_msg)
        if not allowed:
            return jsonify({'allowed': False, 'reason': 'OPA policy denied'}), 403
    except Exception as e:
        logging.error(f"OPA validation error: {e}")
        return jsonify({'allowed': False, 'reason': 'OPA error'}), 500
    # Placeholder for GPT-4 semantic validation (extend here)
    # gpt4_result = ...
    return jsonify({'allowed': True, 'reason': 'OPA policy allowed'}), 200

bp = Blueprint('policy', __name__, url_prefix='/policies')

@swag_from({})
@bp.route('', methods=['GET'])
@jwt_required()
def list_policies():
    items = PolicyService.list()
    return jsonify(PolicySchema(many=True).dump(items)), 200

@swag_from({})
@bp.route('', methods=['POST'])
@jwt_required()
def create_policy():
    data = request.get_json()
    schema = PolicySchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    policy = PolicyService.create(data)
    return jsonify(schema.dump(policy)), 201

@swag_from({})
@bp.route('/<int:policy_id>', methods=['GET'])
@jwt_required()
def get_policy(policy_id):
    policy = PolicyService.get(policy_id)
    if not policy:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(PolicySchema().dump(policy)), 200

@swag_from({})
@bp.route('/<int:policy_id>', methods=['PUT'])
@jwt_required()
def update_policy(policy_id):
    data = request.get_json()
    policy = PolicyService.update(policy_id, data)
    if not policy:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(PolicySchema().dump(policy)), 200

@swag_from({})
@bp.route('/<int:policy_id>', methods=['DELETE'])
@jwt_required()
def delete_policy(policy_id):
    if not PolicyService.delete(policy_id):
        return jsonify({'error': 'Not found'}), 404
    return '', 204

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@bp.route('/metrics', methods=['GET'])
def metrics():
    return 'validation_service_up 1\n', 200, {'Content-Type': 'text/plain'}
