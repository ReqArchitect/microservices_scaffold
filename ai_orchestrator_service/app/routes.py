from flask import Blueprint, jsonify, current_app
from common_utils.auth import rbac_required
from common_utils.traceability import log_audit_event
from flasgger import swag_from

bp = Blueprint('ai_orchestrator', __name__)

# Example endpoint
@bp.route('/generate-code', methods=['POST'])
@rbac_required(roles=['admin', 'ai_engineer'])
@swag_from({...})
def generate_code():
    # ... endpoint logic ...
    log_audit_event(current_app.logger, 'generate_code', {'details': 'Code generated'})
    return jsonify({'result': 'success'})

# Global error handlers
@bp.errorhandler(Exception)
def handle_general_error(error):
    return jsonify({'message': str(error)}), 500

# ... repeat for all endpoints ... 