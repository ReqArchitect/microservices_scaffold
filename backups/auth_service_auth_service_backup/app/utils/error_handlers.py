# Minimal error_handlers for testing

def handle_400(error):
    return {'error': 'Bad request'}, 400

def handle_401(error):
    return {'error': 'Unauthorized'}, 401

def handle_403(error):
    return {'error': 'Forbidden'}, 403

def handle_404(error):
    return {'error': 'Not found'}, 404

def handle_405(error):
    return {'error': 'Method not allowed'}, 405

def handle_429(error):
    return {'error': 'Too many requests'}, 429

def handle_500(error):
    return {'error': 'Internal server error'}, 500

def handle_validation_error(error):
    return {'error': 'Validation error'}, 422 