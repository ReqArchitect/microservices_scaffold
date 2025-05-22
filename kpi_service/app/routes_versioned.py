
from flask import jsonify, request, current_app
from app.models import db
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics
from flask_jwt_extended import jwt_required, get_jwt_identity

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    
    metrics = PrometheusMetrics(bp)
    
    # Health check endpoint (public)
    @bp.route('/health', methods=['GET'])
    @metrics.do_not_track()
    def health_check():
        return jsonify({'status': 'healthy', 'service': current_app.config.get('SERVICE_NAME')}), 200
        
    # TODO: Replace with actual endpoints for this service
    @bp.route('/sample', methods=['GET'])
    @jwt_required()
    @metrics.counter('sample_requests_counter', 'Number of sample endpoint requests')
    @metrics.histogram('sample_requests_histogram', 'Request latency for sample endpoint')
    @latest_version  # Mark as the latest version
    def sample_endpoint():
        user_id = get_jwt_identity()
        return jsonify({
            'message': f'Hello from {current_app.config.get("SERVICE_NAME")}',
            'user_id': user_id,
            'version': version
        }), 200
    
    return bp
