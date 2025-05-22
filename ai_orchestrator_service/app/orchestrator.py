"""
AI orchestration logic for ReqArchitect
"""
import os
import logging
import json
import time
from flask import current_app
import requests
from app.models import AIProvider, AIModel, AIRequest
from common_utils.ai_client import AIServiceClient

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Orchestrates AI operations across multiple providers and models
    """
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.providers = {}
        self.load_providers()
        
    def load_providers(self):
        """Load AI providers from the database or initialize default ones"""
        if self.db_session:
            providers = AIProvider.query.filter_by(is_enabled=True).all()
            
            if not providers:
                # Initialize default providers
                openai_provider = AIProvider(
                    name="OpenAI",
                    api_type="openai",
                    description="OpenAI API Provider",
                    is_enabled=True,
                    default_model="gpt-4",
                    credentials=self._encrypt_credentials({
                        "api_key": os.environ.get("OPENAI_API_KEY", "")
                    })
                )
                self.db_session.add(openai_provider)
                
                anthropic_provider = AIProvider(
                    name="Anthropic",
                    api_type="anthropic",
                    description="Anthropic API Provider",
                    is_enabled=True,
                    default_model="claude-2",
                    credentials=self._encrypt_credentials({
                        "api_key": os.environ.get("ANTHROPIC_API_KEY", "")
                    })
                )
                self.db_session.add(anthropic_provider)
                
                huggingface_provider = AIProvider(
                    name="HuggingFace",
                    api_type="huggingface",
                    description="HuggingFace API Provider",
                    is_enabled=True,
                    default_model="mistralai/Mistral-7B-Instruct-v0.2",
                    credentials=self._encrypt_credentials({
                        "api_key": os.environ.get("HF_API_KEY", "")
                    })
                )
                self.db_session.add(huggingface_provider)
                
                self.db_session.commit()
                
                # After committing, fetch the providers
                providers = AIProvider.query.filter_by(is_enabled=True).all()
                
            for provider in providers:
                self.providers[provider.name.lower()] = provider
                
    def _encrypt_credentials(self, credentials_dict):
        """Simple encryption of credentials (in a real system, use proper encryption)"""
        # This is just a placeholder - in a real system, use proper encryption
        return json.dumps(credentials_dict)
        
    def _decrypt_credentials(self, encrypted_credentials):
        """Simple decryption of credentials (in a real system, use proper decryption)"""
        # This is just a placeholder - in a real system, use proper decryption
        if not encrypted_credentials:
            return {}
        return json.loads(encrypted_credentials)
    
    def execute_operation(self, operation, data, tenant_id=None, model=None, provider=None):
        """
        Execute an AI operation
        
        Args:
            operation (str): Operation type (e.g., "generate_code", "analyze_requirements")
            data (dict): Input data for the operation
            tenant_id (str): Tenant ID
            model (str): Specific model to use
            provider (str): Specific provider to use
            
        Returns:
            dict: Result of the operation
        """
        # Select provider and model
        selected_provider = self._select_provider(provider)
        selected_model = self._select_model(selected_provider, model, operation)
        
        # Create request record
        ai_request = AIRequest(
            tenant_id=tenant_id,
            provider_id=selected_provider.id,
            model_id=selected_model.id,
            operation_type=operation,
            status="pending",
            request_data=json.dumps(data)
        )
        
        if self.db_session:
            self.db_session.add(ai_request)
            self.db_session.commit()
            
        # Prepare the execution
        try:
            start_time = time.time()
            
            # Execute the operation based on provider type
            result = self._execute_provider_operation(
                selected_provider,
                selected_model,
                operation,
                data
            )
            
            # Calculate performance metrics
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update request record
            if self.db_session:
                ai_request.status = "completed"
                ai_request.duration_ms = duration_ms
                ai_request.response_data = json.dumps(result)
                
                # Update token counts and cost if provided in the result
                if 'usage' in result:
                    usage = result['usage']
                    ai_request.prompt_tokens = usage.get('prompt_tokens', 0)
                    ai_request.completion_tokens = usage.get('completion_tokens', 0)
                    ai_request.total_tokens = usage.get('total_tokens', 0)
                    
                    # Calculate cost
                    input_cost = ai_request.prompt_tokens * selected_model.cost_per_token_input
                    output_cost = ai_request.completion_tokens * selected_model.cost_per_token_output
                    ai_request.cost = input_cost + output_cost
                
                self.db_session.add(ai_request)
                self.db_session.commit()
                
            # Return the result
            return {
                'request_id': ai_request.request_id,
                'result': result,
                'metrics': {
                    'duration_ms': duration_ms,
                    'model': selected_model.name,
                    'provider': selected_provider.name
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing AI operation {operation}: {str(e)}")
            
            # Update request record with error
            if self.db_session:
                ai_request.status = "failed"
                ai_request.error_message = str(e)
                self.db_session.add(ai_request)
                self.db_session.commit()
                
            # Return error response
            return {
                'request_id': ai_request.request_id,
                'error': str(e)
            }
    
    def _select_provider(self, provider_name=None):
        """
        Select an AI provider based on the requested name or default
        """
        if provider_name and provider_name.lower() in self.providers:
            return self.providers[provider_name.lower()]
        
        # Use the default provider from config
        default_provider_name = current_app.config.get('DEFAULT_AI_PROVIDER', 'openai').lower()
        
        if default_provider_name in self.providers:
            return self.providers[default_provider_name]
        
        # Fallback to first available provider
        if self.providers:
            return list(self.providers.values())[0]
            
        raise ValueError("No AI providers available")
        
    def _select_model(self, provider, model_name=None, operation=None):
        """
        Select an AI model based on the requested name, operation, or default
        """
        if self.db_session:
            if model_name:
                # Find the specific model
                model = AIModel.query.filter_by(
                    provider_id=provider.id,
                    name=model_name,
                    is_enabled=True
                ).first()
                
                if model:
                    return model
            
            # Find model suited for the operation
            if operation:
                # This would require a more sophisticated selection in a real system
                # based on operation type and model capabilities
                pass
            
            # Fallback to provider's default model
            if provider.default_model:
                model = AIModel.query.filter_by(
                    provider_id=provider.id,
                    name=provider.default_model,
                    is_enabled=True
                ).first()
                
                if model:
                    return model
            
            # Fallback to first enabled model for this provider
            model = AIModel.query.filter_by(
                provider_id=provider.id,
                is_enabled=True
            ).first()
            
            if model:
                return model
        
        # If DB queries fail or no model found, create a placeholder model
        placeholder_model = AIModel(
            id=-1,
            name=model_name or provider.default_model or "default",
            provider_id=provider.id,
            model_type="text",
            is_enabled=True,
            cost_per_token_input=0.0001,
            cost_per_token_output=0.0002
        )
        
        return placeholder_model
    
    def _execute_provider_operation(self, provider, model, operation, data):
        """
        Execute an operation using the selected provider and model
        """
        provider_type = provider.api_type.lower()
        
        if provider_type == "openai":
            return self._execute_openai_operation(provider, model, operation, data)
        elif provider_type == "anthropic":
            return self._execute_anthropic_operation(provider, model, operation, data)
        elif provider_type == "huggingface":
            return self._execute_huggingface_operation(provider, model, operation, data)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
    
    def _execute_openai_operation(self, provider, model, operation, data):
        """
        Execute an operation using OpenAI
        """
        import openai
        
        # Get credentials
        credentials = self._decrypt_credentials(provider.credentials)
        openai.api_key = credentials.get("api_key")
        
        if not openai.api_key:
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            
        if not openai.api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Prepare prompt and parameters based on operation
        system_message, user_message = self._prepare_prompt(operation, data)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=model.name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Process response
        result = {
            "response": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        return result
    
    def _execute_anthropic_operation(self, provider, model, operation, data):
        """
        Execute an operation using Anthropic Claude
        """
        import anthropic
        
        # Get credentials
        credentials = self._decrypt_credentials(provider.credentials)
        api_key = credentials.get("api_key")
        
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Initialize client
        client = anthropic.Client(api_key=api_key)
        
        # Prepare prompt and parameters based on operation
        system_message, user_message = self._prepare_prompt(operation, data)
        
        # Call Anthropic API
        response = client.messages.create(
            model=model.name,
            system=system_message,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Process response
        result = {
            "response": response.content[0].text,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
        
        return result
    
    def _execute_huggingface_operation(self, provider, model, operation, data):
        """
        Execute an operation using HuggingFace Inference API
        """
        # Get credentials
        credentials = self._decrypt_credentials(provider.credentials)
        api_key = credentials.get("api_key")
        
        if not api_key:
            api_key = os.environ.get("HF_API_KEY")
            
        if not api_key:
            raise ValueError("HuggingFace API key not configured")
        
        # Prepare prompt and parameters based on operation
        system_message, user_message = self._prepare_prompt(operation, data)
        
        # Create prompt in the format expected by the model
        prompt = f"<s>[INST] {system_message}\n\n{user_message} [/INST]"
        
        # Call HuggingFace API
        API_URL = f"https://api-inference.huggingface.co/models/{model.name}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"Error from HuggingFace API: {response.text}")
        
        # Process response
        response_data = response.json()
        
        # HuggingFace doesn't provide token counts
        approximate_tokens = len(prompt.split()) + len(response_data[0]["generated_text"].split())
        
        result = {
            "response": response_data[0]["generated_text"],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_data[0]["generated_text"].split()),
                "total_tokens": approximate_tokens
            }
        }
        
        return result
    
    def _prepare_prompt(self, operation, data):
        """
        Prepare system and user prompts based on operation type
        """
        if operation == "code_generation":
            system_message = (
                "You are an expert software developer and architect for ReqArchitect. "
                "You excel at translating business requirements and architectural designs into clean, "
                "well-structured code that follows best practices and design patterns. Ensure your code is "
                "secure, efficient, and maintainable."
            )
            
            user_message = (
                f"Please generate code for the following requirement:\n\n"
                f"{data.get('requirement', '')}\n\n"
                f"Context:\n{json.dumps(data.get('context', {}), indent=2)}\n\n"
                f"Language: {data.get('language', 'Python')}\n"
                f"Framework: {data.get('framework', 'Flask')}\n"
            )
            
        elif operation == "semantic_analysis":
            system_message = (
                "You are an expert requirements analyst and domain expert for ReqArchitect. "
                "You excel at understanding business requirements, identifying gaps, inconsistencies, "
                "and ambiguities, and suggesting improvements. Focus on semantic meaning and intent."
            )
            
            user_message = (
                f"Please analyze the following requirement semantically:\n\n"
                f"{data.get('requirement', '')}\n\n"
                f"Context:\n{json.dumps(data.get('context', {}), indent=2)}\n\n"
                f"Analysis Points: {data.get('analysis_points', 'gaps, inconsistencies, ambiguities')}\n"
            )
            
        elif operation == "business_to_technical":
            system_message = (
                "You are an expert software architect for ReqArchitect. "
                "You excel at translating business requirements into technical specifications "
                "that can be implemented by development teams. Focus on architecture, components, "
                "interfaces, data models, and non-functional requirements."
            )
            
            user_message = (
                f"Please translate the following business requirement into a technical specification:\n\n"
                f"{data.get('business_requirement', '')}\n\n"
                f"Context:\n{json.dumps(data.get('context', {}), indent=2)}\n\n"
                f"Required Sections: {data.get('sections', 'architecture, components, interfaces, data models')}\n"
            )
            
        else:
            # Default generic prompt
            system_message = (
                "You are an expert AI assistant for ReqArchitect, an enterprise design automation tool. "
                "You help with various tasks related to software development, architecture, and requirements."
            )
            
            user_message = (
                f"Please help with the following {operation} task:\n\n"
                f"{json.dumps(data, indent=2)}\n"
            )
            
        return system_message, user_message
