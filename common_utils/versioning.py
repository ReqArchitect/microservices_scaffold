# API versioning utilities for Flask microservices
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
import re

def versioned_blueprint(name, import_name, version, **options):
    """
    Create a versioned Blueprint with standard URL prefix
    
    Args:
        name: Blueprint name
        import_name: Blueprint import name
        version: API version (e.g., 'v1', 'v2')
        **options: Additional Blueprint options
    
    Returns:
        A Flask Blueprint with versioned URL prefix
    """
    if not re.match(r'^v\d+$', version):
        raise ValueError(f"Version must be in format 'v1', 'v2', etc. Got: {version}")
    
    # Set URL prefix with version
    prefix = options.pop('url_prefix', '')
    versioned_prefix = f"/api/{version}{prefix}"
    
    # Create blueprint with versioned prefix
    bp = Blueprint(f"{name}_{version}", import_name, url_prefix=versioned_prefix, **options)
    
    # Add version header to all responses
    @bp.after_request
    def add_version_header(response):
        response.headers['X-API-Version'] = version
        return response
    
    return bp

def latest_version(func):
    """
    Decorator to mark a route as the latest API version.
    This should be applied to routes in the latest version module.
    It allows accessing the latest version without specifying version in URL.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)
    
    decorated._is_latest_version = True
    return decorated

class VersionedAPI:
    """
    Utility for managing versioned APIs in Flask applications
    """
    
    def __init__(self, app=None):
        self.app = app
        self.versions = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize with a Flask application
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Create unversioned Blueprint to handle redirects to latest version
        unversioned_bp = Blueprint('unversioned_api', __name__, url_prefix='/api')
        
        @unversioned_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        def redirect_to_latest(path):
            """
            Redirect unversioned API calls to the latest version
            """
            latest_version = app.config.get('LATEST_API_VERSION', 'v1')
            return self._proxy_to_versioned_endpoint(latest_version, path)
        
        app.register_blueprint(unversioned_bp)
    
    def register_version(self, version, blueprint):
        """
        Register a versioned blueprint
        
        Args:
            version: API version (e.g., 'v1')
            blueprint: Blueprint instance
        """
        self.versions[version] = blueprint
        self.app.register_blueprint(blueprint)
        
        # If this is the latest version, update the config
        current_latest = self.app.config.get('LATEST_API_VERSION', 'v1')
        version_num = int(version[1:])  # Extract number from 'v1', 'v2', etc.
        current_latest_num = int(current_latest[1:])
        
        if version_num > current_latest_num:
            self.app.config['LATEST_API_VERSION'] = version
    
    def _proxy_to_versioned_endpoint(self, version, path):
        """
        Internal method to proxy requests to the correct versioned endpoint
        """
        # This is a simplified implementation
        # In a real system, you might want to use werkzeug's proxy solution
        target_url = f"/api/{version}/{path}"
        
        # Get the same method
        method = request.method
        headers = {k: v for k, v in request.headers.items()}
        data = request.get_data()
        
        # Create a test request context to dispatch to the right route
        with self.app.test_request_context(
            target_url, 
            method=method, 
            headers=headers, 
            data=data
        ) as ctx:
            try:
                # Dispatch request to the right handler
                rv = self.app.preprocess_request()
                if rv is None:
                    rv = self.app.dispatch_request()
                response = self.app.make_response(rv)
                response = self.app.process_response(response)
                return response
            except Exception as e:
                return jsonify({"error": f"API version {version} not found or error: {str(e)}"}), 404
