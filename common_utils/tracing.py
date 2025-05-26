# Distributed tracing utilities using OpenTelemetry
import os
from flask import Flask, request, current_app
import logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

logger = logging.getLogger(__name__)

class Tracer:
    """Distributed tracing utility for Flask microservices"""
    
    def __init__(self, app=None, service_name=None):
        self.app = app
        self.service_name = service_name
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize tracing with the Flask app"""
        self.app = app
        
        # Get configuration from app
        self.service_name = self.service_name or app.config.get('SERVICE_NAME', 'flask-service')
        jaeger_host = app.config.get('JAEGER_HOST', 'jaeger')
        jaeger_port = app.config.get('JAEGER_PORT', 6831)
        tracing_enabled = app.config.get('TRACING_ENABLED', True)
        
        if not tracing_enabled:
            logger.info("Tracing is disabled, skipping setup")
            return
        
        # Initialize tracer provider with the service name
        resource = Resource(attributes={
            SERVICE_NAME: self.service_name
        })
        provider = TracerProvider(resource=resource)
        
        # Create Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        
        # Add the exporter to the provider
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        
        # Set the provider as the global default
        trace.set_tracer_provider(provider)
        
        # Instrument Flask
        FlaskInstrumentor().instrument_app(app)
        
        # Instrument requests library for outgoing calls
        RequestsInstrumentor().instrument()
        
        # If SQLAlchemy is available in the app, instrument it too
        if hasattr(app, 'extensions') and 'sqlalchemy' in app.extensions:
            SQLAlchemyInstrumentor().instrument(
                engine=app.extensions['sqlalchemy'].db.engine
            )
        
        logger.info(f"Distributed tracing initialized for {self.service_name}")
        
        # Add request ID middleware
        @app.before_request
        def before_request():
            request_id = request.headers.get('X-Request-ID')
            if not request_id:
                # Generate a request ID if not present
                import uuid
                request_id = str(uuid.uuid4())
                # Not setting it in response headers here as that should be 
                # done in an after_request handler to ensure it's in all responses

        @app.after_request
        def after_request(response):
            request_id = request.headers.get('X-Request-ID')
            if request_id:
                response.headers['X-Request-ID'] = request_id
            return response
