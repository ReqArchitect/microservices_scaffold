from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import Capability, CourseOfAction, db
import os
import requests
from common_utils.auth import get_user_and_tenant
from common_utils.responses import success_response, error_response
from common_utils.http import post_with_jwt
from common_utils.validation import validate_payload
from common_utils.ai import call_ai_assistant
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics
import logging

logger = logging.getLogger(__name__)

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    
    metrics = PrometheusMetrics(bp)

    # Capability Endpoints
    @bp.route('/capabilities', methods=['GET'])
    @jwt_required(optional=True)
    @metrics.counter('capabilities_get_requests', 'Number of capability list requests')
    def get_capabilities():
        try:
            capabilities = Capability.query.all()
            logger.info(f"Retrieved {len(capabilities)} capabilities")
            return success_response([{
                'id': c.id,
                'title': c.title,
                'description': c.description,
                'user_id': c.user_id,
                'tenant_id': c.tenant_id,
                'business_case_id': c.business_case_id,
                'initiative_id': c.initiative_id
            } for c in capabilities])
        except Exception as e:
            logger.error(f"Error retrieving capabilities: {str(e)}")
            return error_response(str(e), 500)

@bp.route('/capabilities', methods=['POST'])
@jwt_required()
def create_capability():
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    try:
        data = request.get_json()
    except Exception as e:
        return error_response(f'JSON decode error: {str(e)}', 400)
    required_fields = ['title', 'description']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'Missing required field: {field}', 400, data)
    user_id, tenant_id = get_user_and_tenant()
    payload = {
        'title': data['title'],
        'description': data.get('description'),
        'user_id': user_id,
        'tenant_id': tenant_id,
        'business_case_id': data.get('business_case_id'),
        'initiative_id': data.get('initiative_id')
    }
    is_valid, errors = validate_payload(payload, 'capability')
    if not is_valid:
        return error_response('Validation failed', 400, errors)
    c = Capability(**payload)
    db.session.add(c)
    db.session.commit()
    # Orchestration: POST to business_layer_service
    # post_with_jwt(os.environ.get('BUSINESS_LAYER_SERVICE_URL', 'http://localhost:5002/api/business_actors'), {...}, request.headers.get('Authorization'))
    return success_response({'id': c.id}, 201)

# CourseOfAction Endpoints
@bp.route('/courses_of_action', methods=['GET'])
@jwt_required(optional=True)
def get_courses_of_action():
    actions = CourseOfAction.query.all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'user_id': a.user_id,
        'tenant_id': a.tenant_id,
        'initiative_id': a.initiative_id,
        'capability_id': a.capability_id
    } for a in actions])

@bp.route('/courses_of_action', methods=['POST'])
@jwt_required()
def create_course_of_action():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': f'JSON decode error: {str(e)}'}), 400
    required_fields = ['title', 'description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}', 'data': data}), 400
    identity = get_jwt_identity()
    claims = get_jwt()
    user_id = int(identity)
    tenant_id = claims.get('tenant_id')
    a = CourseOfAction(
        title=data['title'],
        description=data.get('description'),
        user_id=user_id,
        tenant_id=tenant_id,
        initiative_id=data.get('initiative_id'),
        capability_id=data.get('capability_id')
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({'id': a.id}), 201
