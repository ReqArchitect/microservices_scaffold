from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface, BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent, BusinessService, BusinessObject, Contract, Product, Goal, Objective, db
from common_utils.auth import get_user_and_tenant
from common_utils.responses import success_response, error_response
from common_utils.http import post_with_jwt
from common_utils.validation import validate_payload
from common_utils.ai import call_ai_assistant

bp = Blueprint('api', __name__)

# Helper to extract user/tenant from JWT

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id

# BusinessActor Endpoints
@bp.route('/business_actors', methods=['GET'])
@jwt_required()
def get_business_actors():
    actors = BusinessActor.query.all()
    return success_response([{
        'id': a.id,
        'name': a.name,
        'description': a.description,
        'user_id': a.user_id,
        'tenant_id': a.tenant_id,
        'initiative_id': a.initiative_id
    } for a in actors])

@bp.route('/business_actors', methods=['POST'])
@jwt_required()
def create_business_actor():
    if not request.is_json:
        return error_response('Request must be JSON', 400)
    data = request.get_json()
    if not data.get('name'):
        return error_response('Missing required field: name', 400)
    user_id, tenant_id = get_user_and_tenant()
    payload = {
        'name': data['name'],
        'description': data.get('description'),
        'user_id': user_id,
        'tenant_id': tenant_id,
        'initiative_id': data.get('initiative_id')
    }
    is_valid, errors = validate_payload(payload, 'business_actor')
    if not is_valid:
        return error_response('Validation failed', 400, errors)
    actor = BusinessActor(**payload)
    db.session.add(actor)
    db.session.commit()
    # Example orchestration: POST to application_layer_service (if needed)
    # post_with_jwt(os.environ['APPLICATION_LAYER_SERVICE_URL'] + '/application_components', {...}, request.headers.get('Authorization'))
    return success_response({'id': actor.id}, 201)

@bp.route('/business_actors/<int:actor_id>', methods=['GET'])
@jwt_required()
def get_business_actor(actor_id):
    actor = BusinessActor.query.get_or_404(actor_id)
    return jsonify({
        'id': actor.id,
        'name': actor.name,
        'description': actor.description,
        'user_id': actor.user_id,
        'tenant_id': actor.tenant_id,
        'initiative_id': actor.initiative_id
    })

@bp.route('/business_actors/<int:actor_id>', methods=['PUT'])
@jwt_required()
def update_business_actor(actor_id):
    actor = BusinessActor.query.get_or_404(actor_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        actor.name = data['name']
    if 'description' in data:
        actor.description = data['description']
    if 'initiative_id' in data:
        actor.initiative_id = data['initiative_id']
    db.session.commit()
    return jsonify({'id': actor.id})

@bp.route('/business_actors/<int:actor_id>', methods=['DELETE'])
@jwt_required()
def delete_business_actor(actor_id):
    actor = BusinessActor.query.get_or_404(actor_id)
    db.session.delete(actor)
    db.session.commit()
    return '', 204

# BusinessProcess Endpoints
@bp.route('/business_processes', methods=['GET'])
@jwt_required(optional=True)
def get_business_processes():
    processes = BusinessProcess.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'user_id': p.user_id,
        'tenant_id': p.tenant_id,
        'initiative_id': p.initiative_id,
        'kpi_id': p.kpi_id
    } for p in processes])

@bp.route('/business_processes', methods=['POST'])
@jwt_required()
def create_business_process():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    process = BusinessProcess(
        name=data['name'],
        description=data.get('description'),
        user_id=user_id,
        tenant_id=tenant_id,
        initiative_id=data.get('initiative_id'),
        kpi_id=data.get('kpi_id')
    )
    db.session.add(process)
    db.session.commit()
    return jsonify({'id': process.id}), 201

@bp.route('/business_processes/<int:process_id>', methods=['GET'])
@jwt_required()
def get_business_process(process_id):
    process = BusinessProcess.query.get_or_404(process_id)
    return jsonify({
        'id': process.id,
        'name': process.name,
        'description': process.description,
        'user_id': process.user_id,
        'tenant_id': process.tenant_id,
        'initiative_id': process.initiative_id,
        'kpi_id': process.kpi_id
    })

@bp.route('/business_processes/<int:process_id>', methods=['PUT'])
@jwt_required()
def update_business_process(process_id):
    process = BusinessProcess.query.get_or_404(process_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        process.name = data['name']
    if 'description' in data:
        process.description = data['description']
    if 'initiative_id' in data:
        process.initiative_id = data['initiative_id']
    if 'kpi_id' in data:
        process.kpi_id = data['kpi_id']
    db.session.commit()
    return jsonify({'id': process.id})

@bp.route('/business_processes/<int:process_id>', methods=['DELETE'])
@jwt_required()
def delete_business_process(process_id):
    process = BusinessProcess.query.get_or_404(process_id)
    db.session.delete(process)
    db.session.commit()
    return '', 204

# Goal Endpoints
@bp.route('/goals', methods=['GET'])
@jwt_required(optional=True)
def get_goals():
    goals = Goal.query.all()
    return jsonify([{
        'id': g.id,
        'title': g.title,
        'description': g.description,
        'user_id': g.user_id,
        'tenant_id': g.tenant_id,
        'business_case_id': g.business_case_id
    } for g in goals])

@bp.route('/goals', methods=['POST'])
@jwt_required()
def create_goal():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Missing required field: title'}), 400
    user_id, tenant_id = get_user_and_tenant()
    goal = Goal(
        title=data['title'],
        description=data.get('description'),
        user_id=user_id,
        tenant_id=tenant_id,
        business_case_id=data.get('business_case_id')
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'id': goal.id}), 201

@bp.route('/goals/<int:goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return jsonify({
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'user_id': goal.user_id,
        'tenant_id': goal.tenant_id,
        'business_case_id': goal.business_case_id
    })

@bp.route('/goals/<int:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'title' in data:
        goal.title = data['title']
    if 'description' in data:
        goal.description = data['description']
    if 'business_case_id' in data:
        goal.business_case_id = data['business_case_id']
    db.session.commit()
    return jsonify({'id': goal.id})

@bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return '', 204

# Objective Endpoints
@bp.route('/objectives', methods=['GET'])
@jwt_required(optional=True)
def get_objectives():
    objectives = Objective.query.all()
    return jsonify([{
        'id': o.id,
        'title': o.title,
        'description': o.description,
        'user_id': o.user_id,
        'tenant_id': o.tenant_id,
        'goal_id': o.goal_id
    } for o in objectives])

@bp.route('/objectives', methods=['POST'])
@jwt_required()
def create_objective():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Missing required field: title'}), 400
    user_id, tenant_id = get_user_and_tenant()
    objective = Objective(
        title=data['title'],
        description=data.get('description'),
        user_id=user_id,
        tenant_id=tenant_id,
        goal_id=data.get('goal_id')
    )
    db.session.add(objective)
    db.session.commit()
    return jsonify({'id': objective.id}), 201

@bp.route('/objectives/<int:objective_id>', methods=['GET'])
@jwt_required()
def get_objective(objective_id):
    objective = Objective.query.get_or_404(objective_id)
    return jsonify({
        'id': objective.id,
        'title': objective.title,
        'description': objective.description,
        'user_id': objective.user_id,
        'tenant_id': objective.tenant_id,
        'goal_id': objective.goal_id
    })

@bp.route('/objectives/<int:objective_id>', methods=['PUT'])
@jwt_required()
def update_objective(objective_id):
    objective = Objective.query.get_or_404(objective_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'title' in data:
        objective.title = data['title']
    if 'description' in data:
        objective.description = data['description']
    if 'goal_id' in data:
        objective.goal_id = data['goal_id']
    db.session.commit()
    return jsonify({'id': objective.id})

@bp.route('/objectives/<int:objective_id>', methods=['DELETE'])
@jwt_required()
def delete_objective(objective_id):
    objective = Objective.query.get_or_404(objective_id)
    db.session.delete(objective)
    db.session.commit()
    return '', 204

# BusinessRole Endpoints
@bp.route('/business_roles', methods=['GET'])
@jwt_required()
def get_business_roles():
    roles = BusinessRole.query.all()
    return jsonify([{ 'id': r.id, 'name': r.name, 'description': r.description, 'user_id': r.user_id, 'tenant_id': r.tenant_id } for r in roles])

@bp.route('/business_roles', methods=['POST'])
@jwt_required()
def create_business_role():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400
    user_id, tenant_id = get_user_and_tenant()
    role = BusinessRole(name=data['name'], description=data.get('description'), user_id=user_id, tenant_id=tenant_id)
    db.session.add(role)
    db.session.commit()
    return jsonify({'id': role.id}), 201

@bp.route('/business_roles/<int:role_id>', methods=['GET'])
@jwt_required()
def get_business_role(role_id):
    role = BusinessRole.query.get_or_404(role_id)
    return jsonify({ 'id': role.id, 'name': role.name, 'description': role.description, 'user_id': role.user_id, 'tenant_id': role.tenant_id })

@bp.route('/business_roles/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_business_role(role_id):
    role = BusinessRole.query.get_or_404(role_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400
    if 'name' in data:
        role.name = data['name']
    if 'description' in data:
        role.description = data['description']
    db.session.commit()
    return jsonify({'id': role.id})

@bp.route('/business_roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_business_role(role_id):
    role = BusinessRole.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
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
