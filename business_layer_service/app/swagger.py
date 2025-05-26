from flask import Blueprint

bp = Blueprint('swagger', __name__)

@bp.route('/apidocs')
def apidocs():
    return "Swagger UI would be here. Integrate flasgger or similar for full docs."
