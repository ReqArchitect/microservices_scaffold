from .models import Integration, IntegrationEvent, db

class IntegrationService:
    @staticmethod
    def create_integration(data):
        integration = Integration(**data)
        db.session.add(integration)
        db.session.commit()
        return integration

    @staticmethod
    def get_integration(integration_id):
        return Integration.query.get(integration_id)

    @staticmethod
    def get_integrations(limit=10, offset=0):
        return Integration.query.order_by(Integration.created_at.desc()).limit(limit).offset(offset).all()

class IntegrationEventService:
    @staticmethod
    def create_event(data):
        event = IntegrationEvent(**data)
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def get_event(event_id):
        return IntegrationEvent.query.get(event_id)

    @staticmethod
    def get_events(limit=10, offset=0):
        return IntegrationEvent.query.order_by(IntegrationEvent.created_at.desc()).limit(limit).offset(offset).all() 