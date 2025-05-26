from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import ApplicationComponent, ApplicationCollaboration, ApplicationInterface, ApplicationFunction, ApplicationInteraction, ApplicationService, DataObject, db
from common_utils.auth import get_user_and_tenant
from common_utils.responses import success_response, error_response
from common_utils.http import post_with_jwt
from common_utils.validation import validate_payload
from common_utils.ai import call_ai_assistant

bp = Blueprint('api', __name__)

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id

# ApplicationComponent Endpoints
@bp.route('/application_components', methods=['GET'])
@jwt_required()
def get_application_components():
    components = ApplicationComponent.query.all()
    return success_response([{ 'id': c.id, 'name': c.name, 'description': c.description, 'user_id': c.user_id, 'tenant_id': c.tenant_id } for c in components])

@bp.route('/application_components', methods=['POST'])
@jwt_required()
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
    return success_response({'id': component.id}, 201)

# ... Repeat similar CRUD endpoints for all other models ...
