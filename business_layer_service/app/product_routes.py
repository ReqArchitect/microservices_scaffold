from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .services.product_service import ProductService
from .schemas import ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema
from flasgger import swag_from

bp_product = Blueprint('products', __name__, url_prefix='/products')

@swag_from({
    "tags": ["Product"],
    "summary": "List all products",
    "responses": {200: {"description": "A list of products"}},
})
@bp_product.route('', methods=['GET'])
@jwt_required()
def list_products():
    products = ProductService.list()
    schema = ProductResponseSchema(many=True)
    return jsonify(schema.dump(products)), 200

@swag_from({
    "tags": ["Product"],
    "summary": "Create a product",
    "parameters": [{"in": "body", "schema": ProductCreateSchema}],
    "responses": {201: {"description": "Created"}, 400: {"description": "Validation error"}},
})
@bp_product.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = ProductCreateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, product = ProductService.create(data)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'id': product.id}), 201

@swag_from({
    "tags": ["Product"],
    "summary": "Get a product by ID",
    "parameters": [{"in": "path", "name": "product_id", "type": "integer", "required": True}],
    "responses": {200: {"description": "Product found"}, 404: {"description": "Not found"}},
})
@bp_product.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id: int):
    product = ProductService.get(product_id)
    if not product:
        return jsonify({'error': 'Not found'}), 404
    schema = ProductResponseSchema()
    return jsonify(schema.dump(product)), 200

@swag_from({
    "tags": ["Product"],
    "summary": "Update a product",
    "parameters": [
        {"in": "path", "name": "product_id", "type": "integer", "required": True},
        {"in": "body", "schema": ProductUpdateSchema}
    ],
    "responses": {200: {"description": "Updated"}, 400: {"description": "Validation error"}, 404: {"description": "Not found"}},
})
@bp_product.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id: int):
    data = request.get_json()
    schema = ProductUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation error', 'details': errors}), 400
    success, message, product = ProductService.update(product_id, data)
    if not success:
        return jsonify({'error': message}), 404
    return jsonify({'id': product.id})

@swag_from({
    "tags": ["Product"],
    "summary": "Delete a product",
    "parameters": [{"in": "path", "name": "product_id", "type": "integer", "required": True}],
    "responses": {204: {"description": "Deleted"}, 404: {"description": "Not found"}},
})
@bp_product.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id: int):
    success = ProductService.delete(product_id)
    if not success:
        return jsonify({'error': 'Not found'}), 404
    return '', 204 