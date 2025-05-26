"""
Versioned routes for the template service
"""
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required
from common_utils.tenant import tenant_required
from app.models import TemplateEntity
from app import db

v1_blueprint = Blueprint('v1', __name__)

@v1_blueprint.route('/health')
def health():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: template_service
            version:
              type: string
              example: v1
    """
    return jsonify({
        'status': 'healthy',
        'service': 'template_service',
        'version': 'v1'
    })

@v1_blueprint.route('/template-entities', methods=['GET'])
@jwt_required()
@tenant_required
def get_template_entities():
    """
    Get all template entities for the current tenant
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: List of template entities
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Example Entity"
              description:
                type: string
                example: "This is an example entity"
              status:
                type: string
                example: "draft"
              priority:
                type: integer
                example: 0
              created_at:
                type: string
                format: date-time
              updated_at:
                type: string
                format: date-time
    """
    tenant_id = g.tenant
    entities = TemplateEntity.get_all_for_tenant(tenant_id)
    return jsonify([entity.to_dict() for entity in entities])

@v1_blueprint.route('/template-entities/<int:entity_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_template_entity(entity_id):
    """
    Get a specific template entity
    ---
    security:
      - Bearer: []
    parameters:
      - name: entity_id
        in: path
        type: integer
        required: true
        description: ID of the template entity
    responses:
      200:
        description: Template entity details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Example Entity"
            description:
              type: string
              example: "This is an example entity"
            status:
              type: string
              example: "draft"
            priority:
              type: integer
              example: 0
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Entity not found
    """
    tenant_id = g.tenant
    entity = TemplateEntity.get_by_id_for_tenant(entity_id, tenant_id)
    
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
        
    return jsonify(entity.to_dict())

@v1_blueprint.route('/template-entities', methods=['POST'])
@jwt_required()
@tenant_required
def create_template_entity():
    """
    Create a new template entity
    ---
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: "New Entity"
            description:
              type: string
              example: "This is a new entity"
            status:
              type: string
              example: "draft"
            priority:
              type: integer
              example: 0
    responses:
      201:
        description: Template entity created
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "New Entity"
            description:
              type: string
              example: "This is a new entity"
            status:
              type: string
              example: "draft"
            priority:
              type: integer
              example: 0
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      400:
        description: Invalid input
    """
    tenant_id = g.tenant
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    entity = TemplateEntity(
        tenant_id=tenant_id,
        name=data['name'],
        description=data.get('description'),
        status=data.get('status', 'draft'),
        priority=data.get('priority', 0)
    )
    
    db.session.add(entity)
    db.session.commit()
    
    return jsonify(entity.to_dict()), 201

@v1_blueprint.route('/template-entities/<int:entity_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_template_entity(entity_id):
    """
    Update a template entity
    ---
    security:
      - Bearer: []
    parameters:
      - name: entity_id
        in: path
        type: integer
        required: true
        description: ID of the template entity
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Updated Entity"
            description:
              type: string
              example: "This is an updated entity"
            status:
              type: string
              example: "active"
            priority:
              type: integer
              example: 1
    responses:
      200:
        description: Template entity updated
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Updated Entity"
            description:
              type: string
              example: "This is an updated entity"
            status:
              type: string
              example: "active"
            priority:
              type: integer
              example: 1
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Entity not found
    """
    tenant_id = g.tenant
    entity = TemplateEntity.get_by_id_for_tenant(entity_id, tenant_id)
    
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    
    data = request.json
    
    if 'name' in data:
        entity.name = data['name']
        
    if 'description' in data:
        entity.description = data['description']
        
    if 'status' in data:
        entity.status = data['status']
        
    if 'priority' in data:
        entity.priority = data['priority']
    
    db.session.commit()
    
    return jsonify(entity.to_dict())

@v1_blueprint.route('/template-entities/<int:entity_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_template_entity(entity_id):
    """
    Delete a template entity
    ---
    security:
      - Bearer: []
    parameters:
      - name: entity_id
        in: path
        type: integer
        required: true
        description: ID of the template entity
    responses:
      204:
        description: Template entity deleted
      404:
        description: Entity not found
    """
    tenant_id = g.tenant
    entity = TemplateEntity.get_by_id_for_tenant(entity_id, tenant_id)
    
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404
    
    db.session.delete(entity)
    db.session.commit()
    
    return '', 204
