from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.contract_service import ContractService
from .schemas import ContractCreateSchema, ContractUpdateSchema, ContractResponseSchema
from flasgger import swag_from

bp_contract = Blueprint('contracts', __name__, url_prefix='/contracts')

@swag_from({
    "tags": ["Contract"],
    "summary": "List all contracts",
    "responses": {200: {"description": "A list of contracts"}},
})
@bp_contract.route('', methods=['GET'])
@jwt_required()
def list_contracts():
    contracts = ContractService.list()
    schema = ContractResponseSchema(many=True)
    return jsonify(schema.dump(contracts)), 200

@swag_from({
    "tags": ["Contract"],
    "summary": "Create a contract",
    "parameters": [{"in": "body", "schema": ContractCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_contract.route('', methods=['POST'])
@jwt_required()
def create_contract():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = ContractCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, contract = ContractService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': contract.id}), 201

@swag_from({
    "tags": ["Contract"],
    "summary": "Get a contract by ID",
    "parameters": [{"in": "path", "name": "contract_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Contract found"}, 404: {"description": "Not found"}},
})
@bp_contract.route('/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id: int):
    contract = ContractService.get(contract_id)
    if not contract:
        return jsonify({'error': 'Not found'}), 404
    schema = ContractResponseSchema()
    return jsonify(schema.dump(contract)), 200

@swag_from({
    "tags": ["Contract"],
    "summary": "Update a contract",
    "parameters": [
        {"in": "path", "name": "contract_id", "type": "integer", "required": True},
        {"in": "body", "schema": ContractUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_contract.route('/<int:contract_id>', methods=['PUT'])
@jwt_required()
def update_contract(contract_id: int):
    data = request.get_json()
    schema = ContractUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, contract = ContractService.update(contract_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': contract.id})

@swag_from({
    "tags": ["Contract"],
    "summary": "Delete a contract",
    "parameters": [{"in": "path", "name": "contract_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_contract.route('/<int:contract_id>', methods=['DELETE'])
@jwt_required()
def delete_contract(contract_id: int):
    success = ContractService.delete(contract_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 