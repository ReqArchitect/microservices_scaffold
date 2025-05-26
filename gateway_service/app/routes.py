"""
API Gateway routes with standardized handling
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
import requests
from functools import wraps
import logging
from common_utils.tenant import tenant_required
from .service_registry import get_service_url
from .rate_limiting import rate_limit
from .circuit_breaker import circuit_breaker
from .caching import cache
from .validation import validate_request

logger = logging.getLogger(__name__)

# Create blueprints for different API versions
v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

def handle_service_request(service_name):
    """
    Decorator for handling service requests with common functionality:
    - Service discovery
    - Circuit breaking
    - Rate limiting
    - Request validation
    - Response caching
    - Error handling
    - Metrics collection
    - Request tracing
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        @tenant_required
        @rate_limit()
        @circuit_breaker(service_name)
        @validate_request
        def wrapped(*args, **kwargs):
            try:
                # Get service URL from registry
                service_url = get_service_url(service_name)
                if not service_url:
                    return jsonify({'error': f'Service {service_name} not available'}), 503

                # Get tenant and trace IDs
                tenant_id = get_jwt().get('tenant_id')
                trace_id = request.headers.get('X-Trace-ID')

                # Prepare headers
                headers = {
                    'Authorization': request.headers.get('Authorization'),
                    'X-Tenant-ID': tenant_id,
                    'X-Trace-ID': trace_id,
                    'Content-Type': 'application/json'
                }

                # Forward the request
                response = requests.request(
                    method=request.method,
                    url=f"{service_url}{request.path}",
                    headers=headers,
                    params=request.args,
                    json=request.get_json() if request.is_json else None,
                    timeout=30
                )

                return (
                    response.json() if response.content else {},
                    response.status_code,
                    {'X-Trace-ID': trace_id}
                )

            except requests.exceptions.Timeout:
                logger.error(f"Timeout calling {service_name}")
                return jsonify({'error': 'Service timeout'}), 504
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling {service_name}: {str(e)}")
                return jsonify({'error': 'Service unavailable'}), 503
            except Exception as e:
                logger.exception(f"Gateway error: {str(e)}")
                return jsonify({'error': 'Internal gateway error'}), 500

        return wrapped
    return decorator

# Product Discovery Layer routes
@v1_blueprint.route('/kpis', methods=['GET', 'POST'])
@v1_blueprint.route('/kpis/<kpi_id>', methods=['GET', 'PUT', 'DELETE'])
@handle_service_request('kpi_service')
def kpi_proxy(kpi_id=None):
    """Proxy KPI service requests"""
    pass

@v1_blueprint.route('/initiatives', methods=['GET', 'POST'])
@v1_blueprint.route('/initiatives/<initiative_id>', methods=['GET', 'PUT', 'DELETE'])
@handle_service_request('initiative_service')
def initiative_proxy(initiative_id=None):
    """Proxy Initiative service requests"""
    pass

@v1_blueprint.route('/canvases', methods=['GET', 'POST'])
@v1_blueprint.route('/canvases/<canvas_id>', methods=['GET', 'PUT', 'DELETE'])
@handle_service_request('canvas_service')
def canvas_proxy(canvas_id=None):
    """Proxy Canvas service requests"""
    pass

# AI Services routes
@v1_blueprint.route('/ai/execute', methods=['POST'])
@handle_service_request('ai_orchestrator_service')
def ai_orchestrator_proxy():
    """Proxy AI Orchestrator service requests"""
    pass

@v1_blueprint.route('/ai/providers', methods=['GET'])
@handle_service_request('ai_orchestrator_service')
def ai_providers_proxy():
    """Proxy AI providers requests"""
    pass

@v1_blueprint.route('/ai/models', methods=['GET'])
@handle_service_request('ai_orchestrator_service')
def ai_models_proxy():
    """Proxy AI models requests"""
    pass

# Transformation Pipeline routes
@v1_blueprint.route('/transform/strategy', methods=['POST'])
@handle_service_request('strategy_service')
def transform_strategy():
    """Proxy strategy transformation requests"""
    pass

@v1_blueprint.route('/transform/business', methods=['POST'])
@handle_service_request('business_layer_service')
def transform_business():
    """Proxy business layer transformation requests"""
    pass

@v1_blueprint.route('/transform/application', methods=['POST'])
@handle_service_request('application_layer_service')
def transform_application():
    """Proxy application layer transformation requests"""
    pass

# Operational routes
@v1_blueprint.route('/auth/login', methods=['POST'])
@handle_service_request('auth_service')
def auth_login():
    """Proxy authentication requests"""
    pass

@v1_blueprint.route('/users', methods=['GET', 'POST'])
@v1_blueprint.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@handle_service_request('user_service')
def user_proxy(user_id=None):
    """Proxy user service requests"""
    pass
