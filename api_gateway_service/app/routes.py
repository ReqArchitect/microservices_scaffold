from flask import Blueprint, request, jsonify
from .service import APIGatewayService
from .schemas import APILogSchema
from flasgger import swag_from
from datetime import datetime

api_gateway_bp = Blueprint('api_gateway', __name__, url_prefix='/api/v1/gateway')

@api_gateway_bp.route('/logs', methods=['POST'])
@swag_from({"summary": "Create API log", "responses": {201: {"description": "Created"}}})
def create_log():
    data = request.get_json()
    log = APIGatewayService.create_log(data)
    return APILogSchema().jsonify(log), 201

@api_gateway_bp.route('/logs/<int:log_id>', methods=['GET'])
@swag_from({"summary": "Get API log", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_log(log_id):
    log = APIGatewayService.get_log(log_id)
    if not log:
        return jsonify({'message': 'Not found'}), 404
    return APILogSchema().jsonify(log)

@api_gateway_bp.route('/logs', methods=['GET'])
@swag_from({"summary": "List API logs", "responses": {200: {"description": "OK"}}})
def get_logs():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    logs = APIGatewayService.get_logs(limit, offset)
    return APILogSchema(many=True).jsonify(logs)

@api_gateway_bp.route('/log_api_call', methods=['POST'])
@swag_from({"summary": "Log API call", "responses": {201: {"description": "Created"}}})
def log_api_call():
    data = request.get_json()
    log = APIGatewayService.log_api_call(**data)
    return APILogSchema().jsonify(log), 201

@api_gateway_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "api-gateway-service", "timestamp": datetime.utcnow().isoformat()})

@api_gateway_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_logs": len(APIGatewayService.get_logs(1000, 0))}) 