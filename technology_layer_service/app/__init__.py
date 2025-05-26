from common_utils.base_service import BaseService
from .models import db, Node, Device, SystemSoftware, TechnologyService, TechnologyInterface, TechnologyFunction, TechnologyProcess, TechnologyInteraction, TechnologyCollaboration, Artifact, Equipment, Material, Facility, CommunicationPath, DistributionNetwork
from .routes import bp as technology_bp

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/technology_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = 'technology_layer_service'
    SERVICE_PORT = 5100
    # Add other config as needed

def create_app(config_object=Config):
    service = BaseService(
        service_name='technology_layer_service',
        config_module=config_object,
        enable_auth=True,
        enable_tracing=True,
        enable_service_registry=True,
        enable_outbox=True,
        enable_metrics=True
    )
    app = service.get_app()
    db.init_app(app)
    # Register blueprints
    app.register_blueprint(technology_bp)
    # Register error handlers
    service.register_error_handlers()
    # Register metrics, tracing, etc. (handled by BaseService)
    return app 