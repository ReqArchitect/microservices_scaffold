from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface, BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent, BusinessService, BusinessObject, Contract, Product, Goal, Objective, db
from common_utils.auth import get_user_and_tenant
from common_utils.responses import success_response, error_response
from common_utils.http import post_with_jwt
from common_utils.validation import validate_payload
from common_utils.ai import call_ai_assistant
from .services.business_actor_service import BusinessActorService
from .services.business_process_service import BusinessProcessService
from .schemas import BusinessActorCreateSchema, BusinessActorUpdateSchema, BusinessActorResponseSchema, BusinessProcessCreateSchema, BusinessProcessUpdateSchema, BusinessProcessResponseSchema, GoalCreateSchema, GoalUpdateSchema, GoalResponseSchema
from .services.goal_service import GoalService
from .services.objective_service import ObjectiveService
from .schemas import ObjectiveCreateSchema, ObjectiveUpdateSchema, ObjectiveResponseSchema
from .services.business_role_service import BusinessRoleService
from .schemas import BusinessRoleCreateSchema, BusinessRoleUpdateSchema, BusinessRoleResponseSchema

bp = Blueprint('api', __name__)

# Helper to extract user/tenant from JWT

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id

# BusinessActor Endpoints
@bp.route('/business_actors', methods=['GET'])
@jwt_required()
def get_business_actors() -> tuple:
    actors = BusinessActorService.list()
    schema = BusinessActorResponseSchema(many=True)
    return jsonify(schema.dump(actors)), 200

@bp.route('/business_actors', methods=['POST'])
@jwt_required()
def create_business_actor() -> tuple:
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    data = request.get_json()
    user_id, tenant_id = get_user_and_tenant()
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessActorCreateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, actor = BusinessActorService.create(data)
    if not success:
        return error_response(message, 400)
    return success_response({'id': actor.id}, 201)

@bp.route('/business_actors/<int:actor_id>', methods=['GET'])
@jwt_required()
def get_business_actor(actor_id: int) -> tuple:
    actor = BusinessActorService.get(actor_id)
    if not actor:
        return error_response('BusinessActor not found', 404)
    schema = BusinessActorResponseSchema()
    return jsonify(schema.dump(actor)), 200

@bp.route('/business_actors/<int:actor_id>', methods=['PUT'])
@jwt_required()
def update_business_actor(actor_id: int) -> tuple:
    data = request.get_json()
    if not data:
        return error_response('Request must be JSON', 400)
    schema = BusinessActorUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, actor = BusinessActorService.update(actor_id, data)
    if not success:
        return error_response(message, 404)
    return success_response({'id': actor.id})

@bp.route('/business_actors/<int:actor_id>', methods=['DELETE'])
@jwt_required()
def delete_business_actor(actor_id: int) -> tuple:
    success = BusinessActorService.delete(actor_id)
    if not success:
        return error_response('BusinessActor not found', 404)
    return '', 204

# BusinessProcess Endpoints
@bp.route('/business_processes', methods=['GET'])
@jwt_required(optional=True)
def get_business_processes() -> tuple:
    processes = BusinessProcessService.list()
    schema = BusinessProcessResponseSchema(many=True)
    return jsonify(schema.dump(processes)), 200

@bp.route('/business_processes', methods=['POST'])
@jwt_required()
def create_business_process() -> tuple:
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    data = request.get_json()
    user_id, tenant_id = get_user_and_tenant()
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessProcessCreateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, process = BusinessProcessService.create(data)
    if not success:
        return error_response(message, 400)
    return success_response({'id': process.id}, 201)

@bp.route('/business_processes/<int:process_id>', methods=['GET'])
@jwt_required()
def get_business_process(process_id: int) -> tuple:
    process = BusinessProcessService.get(process_id)
    if not process:
        return error_response('BusinessProcess not found', 404)
    schema = BusinessProcessResponseSchema()
    return jsonify(schema.dump(process)), 200

@bp.route('/business_processes/<int:process_id>', methods=['PUT'])
@jwt_required()
def update_business_process(process_id: int) -> tuple:
    data = request.get_json()
    if not data:
        return error_response('Request must be JSON', 400)
    schema = BusinessProcessUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, process = BusinessProcessService.update(process_id, data)
    if not success:
        return error_response(message, 404)
    return success_response({'id': process.id})

@bp.route('/business_processes/<int:process_id>', methods=['DELETE'])
@jwt_required()
def delete_business_process(process_id: int) -> tuple:
    success = BusinessProcessService.delete(process_id)
    if not success:
        return error_response('BusinessProcess not found', 404)
    return '', 204

# Goal Endpoints
@bp.route('/goals', methods=['GET'])
@jwt_required(optional=True)
def get_goals() -> tuple:
    goals = GoalService.list()
    schema = GoalResponseSchema(many=True)
    return jsonify(schema.dump(goals)), 200

@bp.route('/goals', methods=['POST'])
@jwt_required()
def create_goal() -> tuple:
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    data = request.get_json()
    user_id, tenant_id = get_user_and_tenant()
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = GoalCreateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, goal = GoalService.create(data)
    if not success:
        return error_response(message, 400)
    return success_response({'id': goal.id}, 201)

@bp.route('/goals/<int:goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id: int) -> tuple:
    goal = GoalService.get(goal_id)
    if not goal:
        return error_response('Goal not found', 404)
    schema = GoalResponseSchema()
    return jsonify(schema.dump(goal)), 200

@bp.route('/goals/<int:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id: int) -> tuple:
    data = request.get_json()
    if not data:
        return error_response('Request must be JSON', 400)
    schema = GoalUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, goal = GoalService.update(goal_id, data)
    if not success:
        return error_response(message, 404)
    return success_response({'id': goal.id})

@bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id: int) -> tuple:
    success = GoalService.delete(goal_id)
    if not success:
        return error_response('Goal not found', 404)
    return '', 204

# Objective Endpoints
@bp.route('/objectives', methods=['GET'])
@jwt_required(optional=True)
def get_objectives() -> tuple:
    objectives = ObjectiveService.list()
    schema = ObjectiveResponseSchema(many=True)
    return jsonify(schema.dump(objectives)), 200

@bp.route('/objectives', methods=['POST'])
@jwt_required()
def create_objective() -> tuple:
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    data = request.get_json()
    user_id, tenant_id = get_user_and_tenant()
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = ObjectiveCreateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, objective = ObjectiveService.create(data)
    if not success:
        return error_response(message, 400)
    return success_response({'id': objective.id}, 201)

@bp.route('/objectives/<int:objective_id>', methods=['GET'])
@jwt_required()
def get_objective(objective_id: int) -> tuple:
    objective = ObjectiveService.get(objective_id)
    if not objective:
        return error_response('Objective not found', 404)
    schema = ObjectiveResponseSchema()
    return jsonify(schema.dump(objective)), 200

@bp.route('/objectives/<int:objective_id>', methods=['PUT'])
@jwt_required()
def update_objective(objective_id: int) -> tuple:
    data = request.get_json()
    if not data:
        return error_response('Request must be JSON', 400)
    schema = ObjectiveUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, objective = ObjectiveService.update(objective_id, data)
    if not success:
        return error_response(message, 404)
    return success_response({'id': objective.id})

@bp.route('/objectives/<int:objective_id>', methods=['DELETE'])
@jwt_required()
def delete_objective(objective_id: int) -> tuple:
    success = ObjectiveService.delete(objective_id)
    if not success:
        return error_response('Objective not found', 404)
    return '', 204

# BusinessRole Endpoints
@bp.route('/business_roles', methods=['GET'])
@jwt_required()
def get_business_roles() -> tuple:
    roles = BusinessRoleService.list()
    schema = BusinessRoleResponseSchema(many=True)
    return jsonify(schema.dump(roles)), 200

@bp.route('/business_roles', methods=['POST'])
@jwt_required()
def create_business_role() -> tuple:
    data = request.get_json()
    user_id, tenant_id = get_user_and_tenant()
    data['user_id'] = user_id
    data['tenant_id'] = tenant_id
    schema = BusinessRoleCreateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, role = BusinessRoleService.create(data)
    if not success:
        return error_response(message, 400)
    return success_response({'id': role.id}, 201)

@bp.route('/business_roles/<int:role_id>', methods=['GET'])
@jwt_required()
def get_business_role(role_id: int) -> tuple:
    role = BusinessRoleService.get(role_id)
    if not role:
        return error_response('BusinessRole not found', 404)
    schema = BusinessRoleResponseSchema()
    return jsonify(schema.dump(role)), 200

@bp.route('/business_roles/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_business_role(role_id: int) -> tuple:
    data = request.get_json()
    if not data:
        return error_response('Request must be JSON', 400)
    schema = BusinessRoleUpdateSchema()
    errors = schema.validate(data)
    if errors:
        return error_response('Validation error', 400, errors)
    success, message, role = BusinessRoleService.update(role_id, data)
    if not success:
        return error_response(message, 404)
    return success_response({'id': role.id})

@bp.route('/business_roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_business_role(role_id: int) -> tuple:
    success = BusinessRoleService.delete(role_id)
    if not success:
        return error_response('BusinessRole not found', 404)
    return '', 204

# BusinessCollaboration Endpoints
@bp.route('/business_collaborations', methods=['GET'])
@jwt_required()
def get_business_collaborations():
    collaborations = BusinessCollaboration.query.all()
    return jsonify([{ 'id': c.id, 'name': c.name, 'description': c.description, 'user_id': c.user_id, 'tenant_id': c.tenant_id } for c in collaborations])

@bp.route('/business_collaborations', methods=['POST'])
@jwt_required()
def create_business_collaboration():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    collab = BusinessCollaboration(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(collab)
    db.session.commit()
    return jsonify({'id': collab.id}), 201

@bp.route('/business_collaborations/<int:collab_id>', methods=['GET'])
@jwt_required()
def get_business_collaboration(collab_id):
    collab = BusinessCollaboration.query.get_or_404(collab_id)
    return jsonify({ 'id': collab.id, 'name': collab.name, 'description': collab.description, 'user_id': collab.user_id, 'tenant_id': collab.tenant_id })

@bp.route('/business_collaborations/<int:collab_id>', methods=['PUT'])
@jwt_required()
def update_business_collaboration(collab_id):
    collab = BusinessCollaboration.query.get_or_404(collab_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        collab.name = data['name']
    if 'description' in data:
        collab.description = data['description']
    db.session.commit()
    return jsonify({'id': collab.id})

@bp.route('/business_collaborations/<int:collab_id>', methods=['DELETE'])
@jwt_required()
def delete_business_collaboration(collab_id):
    collab = BusinessCollaboration.query.get_or_404(collab_id)
    db.session.delete(collab)
    db.session.commit()
    return '', 204

# BusinessInterface Endpoints
@bp.route('/business_interfaces', methods=['GET'])
@jwt_required()
def get_business_interfaces():
    interfaces = BusinessInterface.query.all()
    return jsonify([{ 'id': i.id, 'name': i.name, 'description': i.description, 'user_id': i.user_id, 'tenant_id': i.tenant_id } for i in interfaces])

@bp.route('/business_interfaces', methods=['POST'])
@jwt_required()
def create_business_interface():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    interface = BusinessInterface(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(interface)
    db.session.commit()
    return jsonify({'id': interface.id}), 201

@bp.route('/business_interfaces/<int:interface_id>', methods=['GET'])
@jwt_required()
def get_business_interface(interface_id):
    interface = BusinessInterface.query.get_or_404(interface_id)
    return jsonify({ 'id': interface.id, 'name': interface.name, 'description': interface.description, 'user_id': interface.user_id, 'tenant_id': interface.tenant_id })

@bp.route('/business_interfaces/<int:interface_id>', methods=['PUT'])
@jwt_required()
def update_business_interface(interface_id):
    interface = BusinessInterface.query.get_or_404(interface_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        interface.name = data['name']
    if 'description' in data:
        interface.description = data['description']
    db.session.commit()
    return jsonify({'id': interface.id})

@bp.route('/business_interfaces/<int:interface_id>', methods=['DELETE'])
@jwt_required()
def delete_business_interface(interface_id):
    interface = BusinessInterface.query.get_or_404(interface_id)
    db.session.delete(interface)
    db.session.commit()
    return '', 204

# BusinessFunction Endpoints
@bp.route('/business_functions', methods=['GET'])
@jwt_required()
def get_business_functions():
    functions = BusinessFunction.query.all()
    return jsonify([{ 'id': f.id, 'name': f.name, 'description': f.description, 'user_id': f.user_id, 'tenant_id': f.tenant_id } for f in functions])

@bp.route('/business_functions', methods=['POST'])
@jwt_required()
def create_business_function():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    function = BusinessFunction(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(function)
    db.session.commit()
    return jsonify({'id': function.id}), 201

@bp.route('/business_functions/<int:function_id>', methods=['GET'])
@jwt_required()
def get_business_function(function_id):
    function = BusinessFunction.query.get_or_404(function_id)
    return jsonify({ 'id': function.id, 'name': function.name, 'description': function.description, 'user_id': function.user_id, 'tenant_id': function.tenant_id })

@bp.route('/business_functions/<int:function_id>', methods=['PUT'])
@jwt_required()
def update_business_function(function_id):
    function = BusinessFunction.query.get_or_404(function_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        function.name = data['name']
    if 'description' in data:
        function.description = data['description']
    db.session.commit()
    return jsonify({'id': function.id})

@bp.route('/business_functions/<int:function_id>', methods=['DELETE'])
@jwt_required()
def delete_business_function(function_id):
    function = BusinessFunction.query.get_or_404(function_id)
    db.session.delete(function)
    db.session.commit()
    return '', 204

# BusinessInteraction Endpoints
@bp.route('/business_interactions', methods=['GET'])
@jwt_required()
def get_business_interactions():
    interactions = BusinessInteraction.query.all()
    return jsonify([{ 'id': i.id, 'name': i.name, 'description': i.description, 'user_id': i.user_id, 'tenant_id': i.tenant_id } for i in interactions])

@bp.route('/business_interactions', methods=['POST'])
@jwt_required()
def create_business_interaction():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    interaction = BusinessInteraction(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(interaction)
    db.session.commit()
    return jsonify({'id': interaction.id}), 201

@bp.route('/business_interactions/<int:interaction_id>', methods=['GET'])
@jwt_required()
def get_business_interaction(interaction_id):
    interaction = BusinessInteraction.query.get_or_404(interaction_id)
    return jsonify({ 'id': interaction.id, 'name': interaction.name, 'description': interaction.description, 'user_id': interaction.user_id, 'tenant_id': interaction.tenant_id })

@bp.route('/business_interactions/<int:interaction_id>', methods=['PUT'])
@jwt_required()
def update_business_interaction(interaction_id):
    interaction = BusinessInteraction.query.get_or_404(interaction_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        interaction.name = data['name']
    if 'description' in data:
        interaction.description = data['description']
    db.session.commit()
    return jsonify({'id': interaction.id})

@bp.route('/business_interactions/<int:interaction_id>', methods=['DELETE'])
@jwt_required()
def delete_business_interaction(interaction_id):
    interaction = BusinessInteraction.query.get_or_404(interaction_id)
    db.session.delete(interaction)
    db.session.commit()
    return '', 204

# BusinessEvent Endpoints
@bp.route('/business_events', methods=['GET'])
@jwt_required()
def get_business_events():
    events = BusinessEvent.query.all()
    return jsonify([{ 'id': e.id, 'name': e.name, 'description': e.description, 'user_id': e.user_id, 'tenant_id': e.tenant_id } for e in events])

@bp.route('/business_events', methods=['POST'])
@jwt_required()
def create_business_event():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    event = BusinessEvent(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(event)
    db.session.commit()
    return jsonify({'id': event.id}), 201

@bp.route('/business_events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_business_event(event_id):
    event = BusinessEvent.query.get_or_404(event_id)
    return jsonify({ 'id': event.id, 'name': event.name, 'description': event.description, 'user_id': event.user_id, 'tenant_id': event.tenant_id })

@bp.route('/business_events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_business_event(event_id):
    event = BusinessEvent.query.get_or_404(event_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        event.name = data['name']
    if 'description' in data:
        event.description = data['description']
    db.session.commit()
    return jsonify({'id': event.id})

@bp.route('/business_events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_business_event(event_id):
    event = BusinessEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return '', 204

# BusinessService Endpoints
@bp.route('/business_services', methods=['GET'])
@jwt_required()
def get_business_services():
    services = BusinessService.query.all()
    return jsonify([{ 'id': s.id, 'name': s.name, 'description': s.description, 'user_id': s.user_id, 'tenant_id': s.tenant_id } for s in services])

@bp.route('/business_services', methods=['POST'])
@jwt_required()
def create_business_service():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    service = BusinessService(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(service)
    db.session.commit()
    return jsonify({'id': service.id}), 201

@bp.route('/business_services/<int:service_id>', methods=['GET'])
@jwt_required()
def get_business_service(service_id):
    service = BusinessService.query.get_or_404(service_id)
    return jsonify({ 'id': service.id, 'name': service.name, 'description': service.description, 'user_id': service.user_id, 'tenant_id': service.tenant_id })

@bp.route('/business_services/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_business_service(service_id):
    service = BusinessService.query.get_or_404(service_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        service.name = data['name']
    if 'description' in data:
        service.description = data['description']
    db.session.commit()
    return jsonify({'id': service.id})

@bp.route('/business_services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_business_service(service_id):
    service = BusinessService.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return '', 204

# BusinessObject Endpoints
@bp.route('/business_objects', methods=['GET'])
@jwt_required()
def get_business_objects():
    objects = BusinessObject.query.all()
    return jsonify([{ 'id': o.id, 'name': o.name, 'description': o.description, 'user_id': o.user_id, 'tenant_id': o.tenant_id } for o in objects])

@bp.route('/business_objects', methods=['POST'])
@jwt_required()
def create_business_object():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    obj = BusinessObject(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(obj)
    db.session.commit()
    return jsonify({'id': obj.id}), 201

@bp.route('/business_objects/<int:object_id>', methods=['GET'])
@jwt_required()
def get_business_object(object_id):
    obj = BusinessObject.query.get_or_404(object_id)
    return jsonify({ 'id': obj.id, 'name': obj.name, 'description': obj.description, 'user_id': obj.user_id, 'tenant_id': obj.tenant_id })

@bp.route('/business_objects/<int:object_id>', methods=['PUT'])
@jwt_required()
def update_business_object(object_id):
    obj = BusinessObject.query.get_or_404(object_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        obj.name = data['name']
    if 'description' in data:
        obj.description = data['description']
    db.session.commit()
    return jsonify({'id': obj.id})

@bp.route('/business_objects/<int:object_id>', methods=['DELETE'])
@jwt_required()
def delete_business_object(object_id):
    obj = BusinessObject.query.get_or_404(object_id)
    db.session.delete(obj)
    db.session.commit()
    return '', 204

# Contract Endpoints
@bp.route('/contracts', methods=['GET'])
@jwt_required()
def get_contracts():
    contracts = Contract.query.all()
    return jsonify([{ 'id': c.id, 'name': c.name, 'description': c.description, 'user_id': c.user_id, 'tenant_id': c.tenant_id } for c in contracts])

@bp.route('/contracts', methods=['POST'])
@jwt_required()
def create_contract():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    contract = Contract(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(contract)
    db.session.commit()
    return jsonify({'id': contract.id}), 201

@bp.route('/contracts/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return jsonify({ 'id': contract.id, 'name': contract.name, 'description': contract.description, 'user_id': contract.user_id, 'tenant_id': contract.tenant_id })

@bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@jwt_required()
def update_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        contract.name = data['name']
    if 'description' in data:
        contract.description = data['description']
    db.session.commit()
    return jsonify({'id': contract.id})

@bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
@jwt_required()
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    db.session.delete(contract)
    db.session.commit()
    return '', 204

# Product Endpoints
@bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    return jsonify([{ 'id': p.id, 'name': p.name, 'description': p.description, 'user_id': p.user_id, 'tenant_id': p.tenant_id } for p in products])

@bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    product = Product(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(product)
    db.session.commit()
    return jsonify({'id': product.id}), 201

@bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({ 'id': product.id, 'name': product.name, 'description': product.description, 'user_id': product.user_id, 'tenant_id': product.tenant_id })

@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    db.session.commit()
    return jsonify({'id': product.id})

@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return '', 204
