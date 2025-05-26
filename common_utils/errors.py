from flask import jsonify, request
import traceback

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        tb = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": tb,
            "url": request.url,
            "method": request.method,
            "data": request.get_data(as_text=True)
        }), 500 