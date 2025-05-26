# API routes

from flask import Blueprint, request, jsonify
from app.models import KPI
from app.extensions import db
from app.utils.identity import get_identity
from datetime import datetime

kpi_blueprint = Blueprint('kpi', __name__, url_prefix='/api/kpis')

@kpi_blueprint.route('/', methods=['GET'])
def get_kpis():
    user_id, tenant_id = get_identity()
    kpis = KPI.query.filter_by(tenant_id=tenant_id).all()
    return jsonify([kpi.to_dict() for kpi in kpis]), 200

@kpi_blueprint.route('/', methods=['POST'])
def create_kpi():
    user_id, tenant_id = get_identity()
    data = request.get_json()
    # Validate required fields
    required_fields = ['business_case_id', 'title', 'metric', 'target_value']
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return jsonify({'error': f"Missing required field(s): {', '.join(missing)}"}), 400
    # Parse date fields
    start_date = None
    end_date = None
    if data.get('start_date'):
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('end_date'):
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    new_kpi = KPI(
        tenant_id=tenant_id,
        owner_id=user_id,
        business_case_id=data['business_case_id'],
        title=data['title'],
        description=data.get('description'),
        metric=data['metric'],
        target_value=data['target_value'],
        current_value=data.get('current_value'),
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(new_kpi)
    db.session.commit()
    return jsonify(new_kpi.to_dict()), 201

@kpi_blueprint.route('/<int:kpi_id>', methods=['PUT'])
def update_kpi(kpi_id):
    user_id, tenant_id = get_identity()
    kpi = KPI.query.filter_by(id=kpi_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    kpi.title = data.get('title', kpi.title)
    kpi.description = data.get('description', kpi.description)
    kpi.metric = data.get('metric', kpi.metric)
    kpi.target_value = data.get('target_value', kpi.target_value)
    kpi.current_value = data.get('current_value', kpi.current_value)
    # Parse date fields for update
    if 'start_date' in data:
        kpi.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
    if 'end_date' in data:
        kpi.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
    db.session.commit()
    return jsonify(kpi.to_dict()), 200

@kpi_blueprint.route('/<int:kpi_id>', methods=['DELETE'])
def delete_kpi(kpi_id):
    user_id, tenant_id = get_identity()
    kpi = KPI.query.filter_by(id=kpi_id, tenant_id=tenant_id).first_or_404()
    db.session.delete(kpi)
    db.session.commit()
    return '', 204
