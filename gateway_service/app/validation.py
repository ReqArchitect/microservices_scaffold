"""
Request validation for the API Gateway
"""
from functools import wraps
from flask import request, jsonify
import jsonschema
import yaml
import os
import logging

logger = logging.getLogger(__name__)

class RequestValidator:
    """
    OpenAPI specification based request validator
    """
    def __init__(self):
        self.specs = {}
        self.load_specs()
        
    def load_specs(self):
        """Load OpenAPI specifications for all services"""
        specs_dir = os.path.join(os.path.dirname(__file__), '..', 'specs')
        
        if os.path.exists(specs_dir):
            for filename in os.listdir(specs_dir):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    service_name = filename.split('.')[0]
                    spec_path = os.path.join(specs_dir, filename)
                    
                    try:
                        with open(spec_path, 'r') as f:
                            self.specs[service_name] = yaml.safe_load(f)
                    except Exception as e:
                        logger.error(f"Error loading spec for {service_name}: {str(e)}")
                        
    def validate_request(self, service_name, path, method, request_data=None):
        """
        Validate a request against OpenAPI specification
        
        Args:
            service_name: Name of the service
            path: Request path
            method: HTTP method
            request_data: Request body data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if service_name not in self.specs:
            return True, None  # No spec available, assume valid
            
        spec = self.specs[service_name]
        
        # Find matching path in spec
        path_spec = None
        for spec_path, path_item in spec.get('paths', {}).items():
            # Convert path parameters to regex pattern
            pattern = spec_path.replace('{', '(?P<').replace('}', '>[^/]+)')
            if re.match(pattern, path):
                path_spec = path_item
                break
                
        if not path_spec or method.lower() not in path_spec:
            return True, None  # No spec for this path/method, assume valid
            
        method_spec = path_spec[method.lower()]
        
        # Validate request body if present
        if request_data and 'requestBody' in method_spec:
            content_type = request.headers.get('Content-Type', 'application/json')
            if content_type in method_spec['requestBody'].get('content', {}):
                schema = method_spec['requestBody']['content'][content_type]['schema']
                
                try:
                    jsonschema.validate(request_data, schema)
                except jsonschema.exceptions.ValidationError as e:
                    return False, str(e)
                    
        # Validate query parameters
        for param in method_spec.get('parameters', []):
            if param['in'] == 'query':
                param_name = param['name']
                param_required = param.get('required', False)
                param_schema = param.get('schema', {})
                
                if param_required and param_name not in request.args:
                    return False, f"Missing required query parameter: {param_name}"
                    
                if param_name in request.args:
                    try:
                        jsonschema.validate({param_name: request.args[param_name]}, {
                            'type': 'object',
                            'properties': {param_name: param_schema}
                        })
                    except jsonschema.exceptions.ValidationError as e:
                        return False, str(e)
                        
        return True, None

# Global validator instance
validator = RequestValidator()

def validate_request(f):
    """Request validation decorator"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Extract service name from function name (e.g., kpi_proxy -> kpi_service)
        service_name = f.__name__.split('_')[0] + '_service'
        
        is_valid, error = validator.validate_request(
            service_name,
            request.path,
            request.method,
            request.get_json() if request.is_json else None
        )
        
        if not is_valid:
            return jsonify({
                'error': 'Validation failed',
                'detail': error
            }), 400
            
        return f(*args, **kwargs)
        
    return wrapped
