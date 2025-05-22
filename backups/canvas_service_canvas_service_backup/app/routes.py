# API routes

from flask import Blueprint, request, jsonify
from .models import db, BusinessModelCanvas, KeyPartner, KeyActivity, KeyResource, ValueProposition, CustomerSegment, Channel, CustomerRelationship, RevenueStream, CostStructure
from .utils.identity import get_identity
from datetime import datetime
from fastapi import Depends

canvas_blueprint = Blueprint('canvas', __name__)

# --- BusinessModelCanvas CRUD ---
@canvas_blueprint.route('', methods=['POST'])
async def create_canvas(identity=Depends(get_identity)):
    user_id = identity['user_id']
    tenant_id = identity['tenant_id']
    data = request.get_json()
    if data is None or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    canvas = BusinessModelCanvas(
        user_id=user_id,
        tenant_id=tenant_id,
        title=data['title'],
        description=data.get('description'),
        justification=data.get('justification'),
        expected_benefits=data.get('expected_benefits'),
        risk_assessment=data.get('risk_assessment'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    )
    db.session.add(canvas)
    db.session.commit()
    return jsonify({'canvas': canvas.to_dict()}), 201

@canvas_blueprint.route('', methods=['GET'])
async def list_canvases(identity=Depends(get_identity)):
    tenant_id = identity['tenant_id']
    canvases = BusinessModelCanvas.query.filter_by(tenant_id=tenant_id).all()
    return jsonify({'items': [c.to_dict() for c in canvases]})

@canvas_blueprint.route('/<int:canvas_id>', methods=['GET'])
async def get_canvas(canvas_id, identity=Depends(get_identity)):
    tenant_id = identity['tenant_id']
    canvas = BusinessModelCanvas.query.get(canvas_id)
    if not canvas or canvas.tenant_id != tenant_id:
        return jsonify({'error': 'Canvas not found'}), 404
    return jsonify(canvas.to_dict())

@canvas_blueprint.route('/<int:canvas_id>', methods=['PUT'])
async def update_canvas(canvas_id, identity=Depends(get_identity)):
    tenant_id = identity['tenant_id']
    canvas = BusinessModelCanvas.query.get(canvas_id)
    if not canvas or canvas.tenant_id != tenant_id:
        return jsonify({'error': 'Canvas not found'}), 404
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.'}), 400
    for field in ['title', 'description', 'justification', 'expected_benefits', 'risk_assessment', 'start_date', 'end_date']:
        if field in data:
            if field in ['start_date', 'end_date']:
                setattr(canvas, field, datetime.strptime(data[field], '%Y-%m-%d').date() if data[field] else None)
            else:
                setattr(canvas, field, data[field])
    db.session.commit()
    return jsonify(canvas.to_dict())

@canvas_blueprint.route('/<int:canvas_id>', methods=['DELETE'])
async def delete_canvas(canvas_id, identity=Depends(get_identity)):
    tenant_id = identity['tenant_id']
    canvas = BusinessModelCanvas.query.get(canvas_id)
    if not canvas or canvas.tenant_id != tenant_id:
        return jsonify({'error': 'Canvas not found'}), 404
    db.session.delete(canvas)
    db.session.commit()
    return '', 204

# --- Helper for all component CRUDs ---
def component_crud_routes(model, model_name, required_fields=None, extra_fields=None):
    # Create
    @canvas_blueprint.route(f'/<int:canvas_id>/{model_name}', methods=['POST'])
    async def create_component(canvas_id, identity=Depends(get_identity)):
        user_id = identity['user_id']
        tenant_id = identity['tenant_id']
        canvas = BusinessModelCanvas.query.get(canvas_id)
        if not canvas or canvas.tenant_id != tenant_id:
            return jsonify({'error': 'Canvas not found'}), 404
        data = request.get_json()
        if data is None or not all(data.get(f) for f in (required_fields or [])):
            return jsonify({'error': f"{', '.join(required_fields or [])} is required"}), 400
        kwargs = dict(
            canvas_id=canvas_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        for field in (required_fields or []):
            kwargs[field] = data.get(field)
        if extra_fields:
            for field in extra_fields:
                kwargs[field] = data.get(field)
        component = model(**kwargs)
        db.session.add(component)
        db.session.commit()
        return jsonify({model_name: component.to_dict()}), 201
    # List
    @canvas_blueprint.route(f'/<int:canvas_id>/{model_name}', methods=['GET'])
    async def list_components(canvas_id, identity=Depends(get_identity)):
        tenant_id = identity['tenant_id']
        canvas = BusinessModelCanvas.query.get(canvas_id)
        if not canvas or canvas.tenant_id != tenant_id:
            return jsonify({'error': 'Canvas not found'}), 404
        items = model.query.filter_by(canvas_id=canvas_id, tenant_id=tenant_id).all()
        return jsonify({'items': [c.to_dict() for c in items]})
    # Get
    @canvas_blueprint.route(f'/<int:canvas_id>/{model_name}/<int:comp_id>', methods=['GET'])
    async def get_component(canvas_id, comp_id, identity=Depends(get_identity)):
        tenant_id = identity['tenant_id']
        component = model.query.get(comp_id)
        if not component or component.canvas_id != canvas_id or component.tenant_id != tenant_id:
            return jsonify({'error': f'{model.__name__} not found'}), 404
        return jsonify(component.to_dict())
    # Update
    @canvas_blueprint.route(f'/<int:canvas_id>/{model_name}/<int:comp_id>', methods=['PUT'])
    async def update_component(canvas_id, comp_id, identity=Depends(get_identity)):
        tenant_id = identity['tenant_id']
        component = model.query.get(comp_id)
        if not component or component.canvas_id != canvas_id or component.tenant_id != tenant_id:
            return jsonify({'error': f'{model.__name__} not found'}), 404
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request body must be valid JSON.'}), 400
        for field in (required_fields or []):
            if field in data:
                setattr(component, field, data[field])
        if extra_fields:
            for field in extra_fields:
                if field in data:
                    setattr(component, field, data[field])
        db.session.commit()
        return jsonify(component.to_dict())
    # Delete
    @canvas_blueprint.route(f'/<int:canvas_id>/{model_name}/<int:comp_id>', methods=['DELETE'])
    async def delete_component(canvas_id, comp_id, identity=Depends(get_identity)):
        tenant_id = identity['tenant_id']
        component = model.query.get(comp_id)
        if not component or component.canvas_id != canvas_id or component.tenant_id != tenant_id:
            return jsonify({'error': f'{model.__name__} not found'}), 404
        db.session.delete(component)
        db.session.commit()
        return '', 204

# Register component CRUDs
component_crud_routes(KeyPartner, 'key_partner', required_fields=['name'], extra_fields=['description', 'partner_type'])
component_crud_routes(KeyActivity, 'key_activity', required_fields=['name'], extra_fields=['description', 'activity_type'])
component_crud_routes(KeyResource, 'key_resource', required_fields=['name'], extra_fields=['description', 'resource_type'])
component_crud_routes(ValueProposition, 'value_proposition', required_fields=['name'], extra_fields=['description', 'value_type'])
component_crud_routes(CustomerSegment, 'customer_segment', required_fields=['name'], extra_fields=['description', 'demographic_info'])
component_crud_routes(Channel, 'channel', required_fields=['name'], extra_fields=['description', 'channel_type'])
component_crud_routes(CustomerRelationship, 'customer_relationship', required_fields=['name'], extra_fields=['description', 'relationship_type'])
component_crud_routes(RevenueStream, 'revenue_stream', required_fields=['name'], extra_fields=['description', 'revenue_model', 'amount', 'currency'])
component_crud_routes(CostStructure, 'cost_structure', required_fields=['name'], extra_fields=['description', 'cost_type', 'amount', 'currency', 'frequency'])
