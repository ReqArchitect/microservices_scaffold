from flask import Blueprint, request, jsonify, current_app
from .models import db, ImplementationProject, WorkPackage, Deliverable, ImplementationEvent, Gap, Plateau
from datetime import datetime
from common_utils.auth import rbac_required
from common_utils.traceability import log_audit_event
from flasgger import swag_from

bp = Blueprint('implementation', __name__)

# POST /implementation-projects
@bp.route('/implementation-projects', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_project():
    data = request.json
    project = ImplementationProject(
        project_id=data['projectId'],
        title=data['title'],
        description=data.get('description'),
        start_date=data.get('startDate'),
        end_date=data.get('endDate'),
        milestones=data.get('milestones', [])
    )
    db.session.add(project)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_project', {'projectId': project.project_id})
    return jsonify({'projectId': project.project_id}), 201

# POST /work-packages
@bp.route('/work-packages', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_work_package():
    data = request.json
    wp = WorkPackage(
        work_package_id=data['workPackageId'],
        project_id=data['projectId'],
        name=data['title'],
        description=data.get('description'),
        status=data.get('status'),
        assigned_team=data.get('assignedTeam'),
        expected_completion_date=data.get('expectedCompletionDate')
    )
    db.session.add(wp)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_work_package', {'workPackageId': wp.work_package_id})
    return jsonify({'workPackageId': wp.work_package_id}), 201

# POST /deliverables
@bp.route('/deliverables', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_deliverable():
    data = request.json
    d = Deliverable(
        deliverable_id=data['deliverableId'],
        work_package_id=data['workPackageId'],
        name=data['title'],
        status=data.get('status'),
        file_link=data.get('fileLink')
    )
    db.session.add(d)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_deliverable', {'deliverableId': d.deliverable_id})
    return jsonify({'deliverableId': d.deliverable_id}), 201

# POST /implementation-events
@bp.route('/implementation-events', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_event():
    data = request.json
    e = ImplementationEvent(
        event_id=data['eventId'],
        work_package_id=data['workPackageId'],
        name=data.get('eventType'),
        event_type=data.get('eventType'),
        event_date=data.get('timestamp', datetime.utcnow()),
        description=data.get('details')
    )
    db.session.add(e)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_event', {'eventId': e.event_id})
    return jsonify({'eventId': e.event_id}), 201

# POST /gaps
@bp.route('/gaps', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_gap():
    data = request.json
    g = Gap(
        gap_id=data['gapId'],
        work_package_id=data['workPackageId'],
        name=data.get('description', '')[:32],
        description=data.get('description'),
        impact=data.get('impact'),
        suggested_resolution=data.get('suggestedResolution')
    )
    db.session.add(g)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_gap', {'gapId': g.gap_id})
    return jsonify({'gapId': g.gap_id}), 201

# POST /plateaus
@bp.route('/plateaus', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def create_plateau():
    data = request.json
    p = Plateau(
        plateau_id=data['plateauId'],
        name=data.get('phase'),
        description=data.get('architectureSummary'),
        phase=data.get('phase'),
        architecture_summary=data.get('architectureSummary'),
        timestamp=data.get('timestamp', datetime.utcnow())
    )
    db.session.add(p)
    db.session.commit()
    log_audit_event(current_app.logger, 'create_plateau', {'plateauId': p.plateau_id})
    return jsonify({'plateauId': p.plateau_id}), 201

# Example endpoint
@bp.route('/migrate', methods=['POST'])
@rbac_required(roles=['admin', 'migration_manager'])
@swag_from({...})
def migrate():
    # ... endpoint logic ...
    log_audit_event(current_app.logger, 'migrate', {'details': 'Migration executed'})
    return jsonify({'result': 'success'})

# Global error handlers
@bp.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({'message': str(error)}), 500
