from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from common_utils.responses import success_response, error_response
from common_utils.auth import rbac_required
from common_utils.traceability import log_audit_event
from flasgger import swag_from
from .models import db, Node, Device, SystemSoftware, TechnologyService, TechnologyInterface, TechnologyFunction, TechnologyProcess, TechnologyInteraction, TechnologyCollaboration, Artifact, Equipment, Material, Facility, CommunicationPath, DistributionNetwork

bp = Blueprint('technology', __name__, url_prefix='/api/v1')

def register_crud_routes(model, model_name):
    endpoint = model_name.lower() + 's'
    # Unique function names per model
    @bp.route(f'/{endpoint}', methods=['POST'])
    @jwt_required()
    @rbac_required(roles=['admin', 'devops'])
    @swag_from({...})
    def create_item(**kwargs):
        data = request.get_json()
        item = model(**data)
        db.session.add(item)
        db.session.commit()
        log_audit_event(current_app.logger, f'create_{endpoint}', {'details': f'Created {model_name}'})
        return success_response(item.to_dict(), 201)
    create_item.__name__ = f'create_{endpoint}'

    @bp.route(f'/{endpoint}', methods=['GET'])
    @jwt_required()
    @rbac_required(roles=['admin', 'devops'])
    @swag_from({...})
    def list_items(**kwargs):
        items = model.query.all()
        log_audit_event(current_app.logger, f'list_{endpoint}', {'details': f'Listed {model_name}s'})
        return success_response([i.to_dict() for i in items])
    list_items.__name__ = f'list_{endpoint}'

    @bp.route(f'/{endpoint}/<int:item_id>', methods=['GET'])
    @jwt_required()
    @rbac_required(roles=['admin', 'devops'])
    @swag_from({...})
    def get_item(item_id, **kwargs):
        item = model.query.get(item_id)
        if not item:
            return error_response(f'{model_name} not found', 404)
        log_audit_event(current_app.logger, f'get_{endpoint}', {'details': f'Retrieved {model_name}'})
        return success_response(item.to_dict())
    get_item.__name__ = f'get_{endpoint}'

    @bp.route(f'/{endpoint}/<int:item_id>', methods=['PUT'])
    @jwt_required()
    @rbac_required(roles=['admin', 'devops'])
    @swag_from({...})
    def update_item(item_id, **kwargs):
        item = model.query.get(item_id)
        if not item:
            return error_response(f'{model_name} not found', 404)
        data = request.get_json()
        for k, v in data.items():
            setattr(item, k, v)
        db.session.commit()
        log_audit_event(current_app.logger, f'update_{endpoint}', {'details': f'Updated {model_name}'})
        return success_response(item.to_dict())
    update_item.__name__ = f'update_{endpoint}'

    @bp.route(f'/{endpoint}/<int:item_id>', methods=['DELETE'])
    @jwt_required()
    @rbac_required(roles=['admin', 'devops'])
    @swag_from({...})
    def delete_item(item_id, **kwargs):
        item = model.query.get(item_id)
        if not item:
            return error_response(f'{model_name} not found', 404)
        db.session.delete(item)
        db.session.commit()
        log_audit_event(current_app.logger, f'delete_{endpoint}', {'details': f'Deleted {model_name}'})
        return success_response({'deleted': True})
    delete_item.__name__ = f'delete_{endpoint}'

for model, name in [
    (Node, 'Node'), (Device, 'Device'), (SystemSoftware, 'SystemSoftware'),
    (TechnologyService, 'TechnologyService'), (TechnologyInterface, 'TechnologyInterface'),
    (TechnologyFunction, 'TechnologyFunction'), (TechnologyProcess, 'TechnologyProcess'),
    (TechnologyInteraction, 'TechnologyInteraction'), (TechnologyCollaboration, 'TechnologyCollaboration'),
    (Artifact, 'Artifact'), (Equipment, 'Equipment'), (Material, 'Material'),
    (Facility, 'Facility'), (CommunicationPath, 'CommunicationPath'), (DistributionNetwork, 'DistributionNetwork')
]:
    register_crud_routes(model, name)

# Global error handlers
@bp.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({'message': str(error)}), 500 