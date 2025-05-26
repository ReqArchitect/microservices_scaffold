from flask import Blueprint, request, jsonify
from .service import ReportService
from .schemas import ReportSchema
from flasgger import swag_from
from datetime import datetime

report_bp = Blueprint('report', __name__, url_prefix='/api/v1/report')

@report_bp.route('/reports', methods=['POST'])
@swag_from({"summary": "Create report", "responses": {201: {"description": "Created"}}})
def create_report():
    data = request.get_json()
    report = ReportService.create_report(data)
    return ReportSchema().jsonify(report), 201

@report_bp.route('/reports/<int:report_id>', methods=['GET'])
@swag_from({"summary": "Get report", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_report(report_id):
    report = ReportService.get_report(report_id)
    if not report:
        return jsonify({'message': 'Not found'}), 404
    return ReportSchema().jsonify(report)

@report_bp.route('/reports', methods=['GET'])
@swag_from({"summary": "List reports", "responses": {200: {"description": "OK"}}})
def get_reports():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    reports = ReportService.get_reports(limit, offset)
    return ReportSchema(many=True).jsonify(reports)

@report_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "reporting-service", "timestamp": datetime.utcnow().isoformat()})

@report_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_reports": len(ReportService.get_reports(1000, 0))}) 