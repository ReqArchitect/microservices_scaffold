from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Initiative, InitiativeMember
from common_utils.auth_client import auth_required
from flasgger import swag_from
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from datetime import datetime
from sqlalchemy import or_
import logging
from app.auth import (
    permission_required, role_required, log_auth_event,
    check_tenant_access, validate_token, has_permission
)
from flask_jwt_extended import jwt_required
from app.utils.identity import get_identity

initiative_blueprint = Blueprint("initiatives", __name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"],
    storage_uri="memory://"
)

cache = Cache()

def get_pagination_params():
    """Get pagination parameters from request."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['DEFAULT_PAGE_SIZE'], type=int)
    per_page = min(per_page, current_app.config['MAX_PAGE_SIZE'])
    return page, per_page

def get_filter_params():
    """Get filter parameters from request."""
    return {
        'status': request.args.get('status'),
        'priority': request.args.get('priority'),
        'search': request.args.get('search'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'tags': request.args.getlist('tags')
    }

@initiative_blueprint.route("", methods=["POST"])
@swag_from({
    "tags": ["Initiatives"],
    "summary": "Create new initiative",
    "description": "Creates a new initiative",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "strategic_objective": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "status": {"type": "string", "enum": ["draft", "active", "completed", "cancelled"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "progress": {"type": "number"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "description", "strategic_objective"]
            }
        }
    ],
    "responses": {
        201: {"description": "Initiative created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
})
def create_initiative():
    user_id, tenant_id = get_identity()
    data = request.get_json()
    required_fields = ['title', 'description', 'strategic_objective']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field.capitalize()} is required"}), 400
    initiative = Initiative(
        title=data['title'],
        description=data['description'],
        strategic_objective=data['strategic_objective'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else None,
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else None,
        status=data.get('status', 'draft'),
        priority=data.get('priority', 'medium'),
        progress=data.get('progress', 0),
        tenant_id=tenant_id,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else (data.get('tags') or '')
    )
    db.session.add(initiative)
    db.session.commit()
    member = InitiativeMember(
        initiative_id=initiative.id,
        user_id=user_id,
        role='admin'
    )
    db.session.add(member)
    db.session.commit()
    current_app.logger.info(
        f"Auth Event: initiative_created | User: {user_id} | Tenant: {tenant_id} | initiative_id: {initiative.id}"
    )
    return jsonify({
        "message": "Initiative created successfully",
        "initiative": initiative.to_dict()
    }), 201

@initiative_blueprint.route("", methods=["GET"])
@swag_from({
    "tags": ["Initiatives"],
    "summary": "List initiatives",
    "description": "Get a list of initiatives",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "default": 1
        },
        {
            "name": "per_page",
            "in": "query",
            "type": "integer",
            "default": 20
        },
        {
            "name": "strategic_objective",
            "in": "query",
            "type": "string"
        },
        {
            "name": "priority",
            "in": "query",
            "type": "string"
        },
        {
            "name": "tags",
            "in": "query",
            "type": "string"
        },
        {
            "name": "search",
            "in": "query",
            "type": "string"
        },
        {
            "name": "status",
            "in": "query",
            "type": "string"
        }
    ],
    "responses": {
        200: {"description": "List of initiatives"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
})
def list_initiatives():
    user_id, tenant_id = get_identity()
    query = Initiative.query.filter_by(tenant_id=tenant_id)
    # Filtering
    strategic_objective = request.args.get('strategic_objective')
    if strategic_objective:
        query = query.filter(Initiative.strategic_objective == strategic_objective)
    priority = request.args.get('priority')
    if priority:
        query = query.filter(Initiative.priority == priority)
    tags = request.args.get('tags')
    if tags:
        # Match if any tag in the comma-separated list matches
        query = query.filter(Initiative.tags.ilike(f"%{tags}%"))
    status = request.args.get('status')
    if status:
        query = query.filter(Initiative.status == status)
    search = request.args.get('search')
    if search:
        search = f"%{search}%"
        query = query.filter(or_(Initiative.title.ilike(search), Initiative.description.ilike(search)))
    # Pagination (optional, not required by tests)
    page, per_page = get_pagination_params()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [initiative.to_dict() for initiative in pagination.items]
    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page
    })

@initiative_blueprint.route("/<int:initiative_id>", methods=["GET"])
@swag_from({
    "tags": ["Initiatives"],
    "summary": "Get initiative details",
    "description": "Get details of a specific initiative",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "initiative_id",
            "in": "path",
            "required": True,
            "type": "integer"
        }
    ],
    "responses": {
        200: {"description": "Initiative details"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Initiative not found"}
    }
})
def get_initiative(initiative_id):
    user_id, tenant_id = get_identity()
    initiative = Initiative.query.get(initiative_id)
    if not initiative or initiative.tenant_id != tenant_id:
        return jsonify({"error": "Initiative not found"}), 404
    return jsonify(initiative.to_dict()), 200

@initiative_blueprint.route("/<int:initiative_id>", methods=["PUT"])
@swag_from({
    "tags": ["Initiatives"],
    "summary": "Update initiative",
    "description": "Update details of a specific initiative",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "initiative_id",
            "in": "path",
            "required": True,
            "type": "integer"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "strategic_objective": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "status": {"type": "string", "enum": ["draft", "active", "completed", "cancelled"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "progress": {"type": "number"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "description", "strategic_objective"]
            }
        }
    ],
    "responses": {
        200: {"description": "Initiative updated successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Initiative not found"}
    }
})
def update_initiative(initiative_id):
    user_id, tenant_id = get_identity()
    initiative = Initiative.query.get(initiative_id)
    if not initiative or initiative.tenant_id != tenant_id:
        return jsonify({"error": "Initiative not found"}), 404
    data = request.get_json()
    for field in ['title', 'description', 'strategic_objective', 'start_date', 'end_date', 'status', 'priority', 'progress', 'tags']:
        if field in data:
            if field in ['start_date', 'end_date']:
                setattr(initiative, field, datetime.strptime(data[field], '%Y-%m-%d').date() if data[field] else None)
            elif field == 'tags' and isinstance(data[field], list):
                setattr(initiative, field, ','.join(data[field]))
            else:
                setattr(initiative, field, data[field])
    initiative.updated_by = user_id
    db.session.commit()
    return jsonify(initiative.to_dict()), 200

@initiative_blueprint.route("/<int:initiative_id>/members", methods=["POST"])
@swag_from({
    "tags": ["Initiative Members"],
    "summary": "Add initiative member",
    "description": "Add a new member to the initiative",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "initiative_id",
            "in": "path",
            "required": True,
            "type": "integer"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "role": {"type": "string", "enum": ["admin", "member"]}
                },
                "required": ["user_id", "role"]
            }
        }
    ],
    "responses": {
        201: {"description": "Member added successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Initiative not found"}
    }
})
def add_initiative_member(initiative_id):
    user_id, tenant_id = get_identity()
    initiative = Initiative.query.get(initiative_id)
    if not initiative or initiative.tenant_id != tenant_id:
        return jsonify({"error": "Initiative not found"}), 404
    data = request.get_json()
    if not data.get('user_id') or not data.get('role'):
        return jsonify({"error": "user_id and role are required"}), 400
    member = InitiativeMember(
        initiative_id=initiative_id,
        user_id=data['user_id'],
        role=data['role']
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201

@initiative_blueprint.route("/<int:initiative_id>", methods=["DELETE"])
@swag_from({
    "tags": ["Initiatives"],
    "summary": "Delete initiative",
    "description": "Delete a specific initiative",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "initiative_id",
            "in": "path",
            "required": True,
            "type": "integer"
        }
    ],
    "responses": {
        204: {"description": "Initiative deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Initiative not found"}
    }
})
def delete_initiative(initiative_id):
    user_id, tenant_id = get_identity()
    initiative = Initiative.query.get(initiative_id)
    if not initiative or initiative.tenant_id != tenant_id:
        return jsonify({"error": "Initiative not found"}), 404
    db.session.delete(initiative)
    db.session.commit()
    return '', 204
