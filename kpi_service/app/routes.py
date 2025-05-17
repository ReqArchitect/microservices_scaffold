# API routes

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import KPI
from app.extensions import db

kpi_blueprint = Blueprint('kpi', __name__, url_prefix='/api/kpis')

@kpi_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_kpis():
    tenant_id = get_jwt().get('tenant_id')
    kpis = KPI.query.filter_by(tenant_id=tenant_id).all()
    return jsonify([kpi.to_dict() for kpi in kpis]), 200

@kpi_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_kpi():
    tenant_id = get_jwt().get('tenant_id')
    user_id = get_jwt_identity()
    data = request.get_json()
    new_kpi = KPI(
        tenant_id=tenant_id,
        owner_id=user_id,
        business_case_id=data['business_case_id'],
        title=data['title'],
        description=data.get('description'),
        metric=data['metric'],
        target_value=data['target_value'],
        current_value=data.get('current_value'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date')
    )
    db.session.add(new_kpi)
    db.session.commit()
    return jsonify(new_kpi.to_dict()), 201

@kpi_blueprint.route('/<int:kpi_id>', methods=['PUT'])
@jwt_required()
def update_kpi(kpi_id):
    tenant_id = get_jwt().get('tenant_id')
    kpi = KPI.query.filter_by(id=kpi_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    kpi.title = data.get('title', kpi.title)
    kpi.description = data.get('description', kpi.description)
    kpi.metric = data.get('metric', kpi.metric)
    kpi.target_value = data.get('target_value', kpi.target_value)
    kpi.current_value = data.get('current_value', kpi.current_value)
    kpi.start_date = data.get('start_date', kpi.start_date)
    kpi.end_date = data.get('end_date', kpi.end_date)
    db.session.commit()
    return jsonify(kpi.to_dict()), 200

@kpi_blueprint.route('/<int:kpi_id>', methods=['DELETE'])
@jwt_required()
def delete_kpi(kpi_id):
    tenant_id = get_jwt().get('tenant_id')
    kpi = KPI.query.filter_by(id=kpi_id, tenant_id=tenant_id).first_or_404()
    db.session.delete(kpi)
    db.session.commit()
    return '', 204
