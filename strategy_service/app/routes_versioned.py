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
<<<<<<< HEAD
                'tenant_id': c.tenant_id,                'business_context_id': c.business_context_id,
                'initiative_context_id': c.initiative_context_id
=======
                'tenant_id': c.tenant_id,
                'business_case_id': c.business_case_id,
                'initiative_id': c.initiative_id
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
            } for c in capabilities])
        except Exception as e:
            logger.error(f"Error retrieving capabilities: {str(e)}")
            return error_response(str(e), 500)

    @bp.route('/capabilities', methods=['POST'])
    @jwt_required()
    @metrics.counter('capabilities_create_requests', 'Number of capability creation requests')
    @latest_version
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
        
        try:
            c = Capability(**payload)
            db.session.add(c)
            db.session.commit()
            
            # Orchestration: POST to business_layer_service
            try:
                token = request.headers.get('Authorization')
                business_url = os.environ.get('BUSINESS_URL', 'http://business_layer_service:5002/api/v1/business_actors')
                
                # Using our service registry to get the business layer URL
                from flask import current_app
                if hasattr(current_app, 'extensions') and 'service_registry' in current_app.extensions:
                    registry = current_app.extensions['service_registry']
                    dynamic_url = registry.get_service_url('business_layer_service')
                    if dynamic_url:
                        business_url = f"{dynamic_url}/api/v1/business_actors"
                
                # Asynchronous notification using outbox pattern (if configured)
                if hasattr(current_app, 'config') and current_app.config.get('USE_OUTBOX_PATTERN', False):
                    from common_utils.outbox import OutboxEvent
                    OutboxEvent.create_event(
                        session=db.session,
                        event_type='capability_created',
                        aggregate_type='capability',
                        aggregate_id=str(c.id),
                        payload={
                            'name': c.title,
                            'description': c.description,
                            'capability_id': c.id
                        }
                    )
                    db.session.commit()
                else:
                    # Synchronous call to business layer service
                    resp = post_with_jwt(
                        business_url,
                        {
                            'name': c.title,
                            'description': c.description,
                            'capability_id': c.id
                        },
                        token
                    )
                logger.info(f"Business layer service notified about new capability {c.id}")
            except Exception as e:
                logger.error(f"Failed to notify business layer: {str(e)}")
                # Continue anyway - eventual consistency will handle it
            
            return success_response({'id': c.id}, 201)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating capability: {str(e)}")
            return error_response(str(e), 500)

    # CourseOfAction Endpoints
    @bp.route('/courses_of_action', methods=['GET'])
    @jwt_required(optional=True)
    @metrics.counter('coa_get_requests', 'Number of courses of action list requests')
    def get_courses_of_action():
        try:
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
        except Exception as e:
            logger.error(f"Error retrieving courses of action: {str(e)}")
            return error_response(str(e), 500)

    @bp.route('/courses_of_action', methods=['POST'])
    @jwt_required()
    @metrics.counter('coa_create_requests', 'Number of courses of action creation requests')
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
        
        user_id, tenant_id = get_user_and_tenant()
        
        try:
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
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating course of action: {str(e)}")
            return error_response(str(e), 500)
            
    return bp
