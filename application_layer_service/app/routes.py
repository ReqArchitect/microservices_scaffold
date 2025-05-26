from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import ApplicationComponent, ApplicationCollaboration, ApplicationInterface, ApplicationFunction, ApplicationInteraction, ApplicationService, DataObject, db
from common_utils.auth import rbac_required
from common_utils.responses import success_response, error_response
from common_utils.http import post_with_jwt
from common_utils.validation import validate_payload
from common_utils.ai import call_ai_assistant
from common_utils.traceability import log_audit_event
from flasgger import swag_from

bp = Blueprint('api', __name__)

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id

# ApplicationComponent Endpoints
@bp.route('/application_components', methods=['GET'])
@jwt_required()
@rbac_required(roles=['admin', 'architect'])
@swag_from({...})
def get_application_components():
    components = ApplicationComponent.query.all()
    log_audit_event(current_app.logger, 'list_application_components', {'details': 'Listed all components'})
    return success_response([{ 'id': c.id, 'name': c.name, 'description': c.description, 'user_id': c.user_id, 'tenant_id': c.tenant_id } for c in components])

@bp.route('/application_components', methods=['POST'])
@jwt_required()
@rbac_required(roles=['admin', 'architect'])
@swag_from({...})
def create_application_component():
    data = request.get_json()
    if not data or not data.get('name'):
        return error_response('Missing required field: name', 400)
    user_id, tenant_id = get_user_and_tenant()
    payload = {
        'name': data['name'],
        'description': data.get('description'),
        'user_id': user_id,
        'tenant_id': tenant_id
    }
    is_valid, errors = validate_payload(payload, 'application_component')
    if not is_valid:
        return error_response('Validation failed', 400, errors)
    component = ApplicationComponent(**payload)
    db.session.add(component)
    db.session.commit()
    # Example orchestration: POST to technology_layer_service (if needed)
    # post_with_jwt(os.environ['TECHNOLOGY_LAYER_SERVICE_URL'] + '/technology_components', {...}, request.headers.get('Authorization'))
    log_audit_event(current_app.logger, 'create_application_component', {'details': f'Created component with id: {component.id}'})
    return success_response({'id': component.id}, 201)

# ... Repeat similar CRUD endpoints for all other models ...

@bp.route('/generate', methods=['POST'])
@jwt_required()
@rbac_required(roles=['admin', 'architect'])
@swag_from({...})
def generate():
    # ... endpoint logic ...
    log_audit_event(current_app.logger, 'generate', {'details': 'Generated app artifact'})
    return jsonify({'result': 'success'})

# Global error handlers
@bp.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({'message': str(error)}), 500
