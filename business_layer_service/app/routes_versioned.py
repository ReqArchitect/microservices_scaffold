from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, BusinessCase
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics
import logging

logger = logging.getLogger(__name__)

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    
    metrics = PrometheusMetrics(bp)
    
    # Health check endpoint (public)
    @bp.route('/health', methods=['GET'])
    @metrics.do_not_track()
    def health_check():
        return jsonify({'status': 'healthy', 'service': current_app.config.get('SERVICE_NAME')}), 200
    
    # Business case endpoints
    @bp.route('/business-cases', methods=['GET'])
    @jwt_required()
    @metrics.counter('business_cases_get_requests', 'Number of business case list requests')
    def get_business_cases():
        try:
            # Get the JWT identity
            current_user = get_jwt_identity()
            
            # Query business cases
            business_cases = BusinessCase.query.all()
            
            # Log successful retrieval
            logger.info(f"Retrieved {len(business_cases)} business cases")
            
            # Format response
            return jsonify({
                'status': 'success',
                'data': [business_case.to_dict() for business_case in business_cases]
            }), 200
        except Exception as e:
            logger.error(f"Error retrieving business cases: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @bp.route('/business-cases', methods=['POST'])
    @jwt_required()
    @metrics.counter('business_cases_create_requests', 'Number of business case creation requests')
    @latest_version
    def create_business_case():
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400
        
        try:
            # Get the request data
            data = request.json
            
            # Create a new business case
            business_case = BusinessCase(
                title=data.get('title'),
                description=data.get('description'),
                user_id=get_jwt_identity().get('user_id'),
                tenant_id=get_jwt_identity().get('tenant_id')
            )
            
            # Save to database
            db.session.add(business_case)
            db.session.commit()
            
            # Log successful creation
            logger.info(f"Created business case with id {business_case.id}")
            
            # Return the created business case
            return jsonify({
                'status': 'success',
                'data': business_case.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating business case: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @bp.route('/business-cases/<int:id>', methods=['GET'])
    @jwt_required()
    @metrics.counter('business_case_get_requests', 'Number of business case detail requests')
    def get_business_case(id):
        try:
            # Query the business case
            business_case = BusinessCase.query.get(id)
            
            if not business_case:
                return jsonify({
                    'status': 'error',
                    'message': f'Business case with id {id} not found'
                }), 404
            
            # Log successful retrieval
            logger.info(f"Retrieved business case with id {id}")
            
            # Return the business case
            return jsonify({
                'status': 'success',
                'data': business_case.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"Error retrieving business case {id}: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # More endpoints can be added here
    
    return bp