from flask import Blueprint, jsonify, current_app
from common_utils.auth import rbac_required
from common_utils.traceability import log_audit_event
from flasgger import swag_from

bp = Blueprint('motivation', __name__)

# Example endpoint
@bp.route('/motivation', methods=['POST'])
@rbac_required(roles=['admin', 'analyst'])
@swag_from({...})
def add_motivation():
    # ... endpoint logic ...
    log_audit_event(current_app.logger, 'add_motivation', {'details': 'Motivation added'})
    return jsonify({'result': 'success'})

# Global error handlers
@bp.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({'message': str(error)}), 500

# ... repeat for all endpoints ... 