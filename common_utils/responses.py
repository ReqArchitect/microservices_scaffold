from flask import jsonify

def success_response(data=None, status=200):
    resp = {'success': True}
    if data is not None:
        resp['data'] = data
    return jsonify(resp), status

def error_response(message, status=400, details=None):
    resp = {'success': False, 'error': message}
    if details:
        resp['details'] = details
    return jsonify(resp), status 