"""
AI integration utilities for ReqArchitect services
"""
import os
import requests
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AIServiceClient:
    """
    Client for making requests to AI services
    """
    def __init__(self, service_name="ai_assistant", base_url=None, api_key=None):
        self.service_name = service_name
        self.base_url = base_url or os.environ.get(f'{service_name.upper()}_SERVICE_URL')
        self.api_key = api_key or os.environ.get(f'{service_name.upper()}_API_KEY')
        
    def call_assistant(self, prompt, context=None, model="default", jwt_token=None):
        """
        Call the AI assistant service
        
        Args:
            prompt (str): The prompt to send to the AI
            context (dict): Additional context to include
            model (str): The model to use
            jwt_token (str): Authentication token
            
        Returns:
            dict: The response from the AI service
        """
        url = f"{self.base_url}/api/v1/ask" if self.base_url else f"http://ai-assistant-service:5200/api/v1/ask"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if jwt_token:
            headers['Authorization'] = f"Bearer {jwt_token}"
            
        if self.api_key:
            headers['X-API-KEY'] = self.api_key
            
        payload = {
            'prompt': prompt,
            'model': model
        }
        
        if context:
            payload['context'] = context
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling AI assistant: {str(e)}")
            return {'error': str(e)}
    
    def call_orchestrator(self, operation, data, context=None, jwt_token=None):
        """
        Call the AI orchestrator service for advanced operations
        
        Args:
            operation (str): The operation to perform (e.g., "code_generation", "semantic_analysis")
            data (dict): The data for the operation
            context (dict): Additional context to include
            jwt_token (str): Authentication token
            
        Returns:
            dict: The response from the AI orchestrator
        """
        url = f"{self.base_url}/api/v1/{operation}" if self.base_url else f"http://ai-orchestrator-service:5100/api/v1/{operation}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if jwt_token:
            headers['Authorization'] = f"Bearer {jwt_token}"
            
        if self.api_key:
            headers['X-API-KEY'] = self.api_key
            
        payload = {
            'data': data
        }
        
        if context:
            payload['context'] = context
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling AI orchestrator: {str(e)}")
            return {'error': str(e)}

def with_ai_assistance(operation="documentation"):
    """
    Decorator to add AI assistance to a function
    
    Args:
        operation (str): The AI operation to perform
        
    Example:
        @with_ai_assistance("documentation")
        def generate_code(spec):
            # Function implementation
            return code
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = func(*args, **kwargs)
            
            # If enabled, enhance the result with AI
            ai_enabled = os.environ.get('AI_ASSISTANCE_ENABLED', 'true').lower() == 'true'
            if ai_enabled:
                try:
                    ai_client = AIServiceClient()
                    context = {
                        'function_name': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs),
                        'result_type': type(result).__name__
                    }
                    
                    ai_response = ai_client.call_assistant(
                        prompt=f"Enhance this {operation} result: {result}",
                        context=context
                    )
                    
                    if 'error' not in ai_response:
                        enhanced_result = ai_response.get('response', result)
                        if enhanced_result:
                            result = enhanced_result
                except Exception as e:
                    logger.warning(f"AI assistance failed: {str(e)}")
            
            return result
        return wrapper
    return decorator
