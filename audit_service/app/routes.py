from flask import Blueprint, request, jsonify
from .service import AuditService
from .schemas import AuditLogSchema
from flasgger import swag_from
from datetime import datetime

audit_bp = Blueprint('audit', __name__, url_prefix='/api/v1/audit')

@audit_bp.route('/logs', methods=['POST'])
@swag_from({"summary": "Create audit log", "responses": {201: {"description": "Created"}}})
def create_log():
    data = request.get_json()
    log = AuditService.create_log(data)
    return AuditLogSchema().jsonify(log), 201

@audit_bp.route('/logs/<int:log_id>', methods=['GET'])
@swag_from({"summary": "Get audit log", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_log(log_id):
    log = AuditService.get_log(log_id)
    if not log:
        return jsonify({'message': 'Not found'}), 404
    return AuditLogSchema().jsonify(log)

@audit_bp.route('/logs', methods=['GET'])
@swag_from({"summary": "List audit logs", "responses": {200: {"description": "OK"}}})
def get_logs():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    logs = AuditService.get_logs(limit, offset)
    return AuditLogSchema(many=True).jsonify(logs)

@audit_bp.route('/log_event', methods=['POST'])
@swag_from({"summary": "Log event", "responses": {201: {"description": "Created"}}})
def log_event():
    data = request.get_json()
    log = AuditService.log_event(**data)
    return AuditLogSchema().jsonify(log), 201

@audit_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "audit-service", "timestamp": datetime.utcnow().isoformat()})

@audit_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_logs": len(AuditService.get_logs(1000, 0))}) 