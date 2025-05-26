from .models import db, Integration, IntegrationEvent, IntegrationLog

class IntegrationService:
    @staticmethod
    def create(data):
        integration = Integration(**data)
        db.session.add(integration)
        db.session.commit()
        return integration

    @staticmethod
    def get(integration_id):
        return Integration.query.get(integration_id)

    @staticmethod
    def update(integration_id, data):
        integration = Integration.query.get(integration_id)
        if not integration:
            return None
        for k, v in data.items():
            setattr(integration, k, v)
        db.session.commit()
        return integration

    @staticmethod
    def delete(integration_id):
        integration = Integration.query.get(integration_id)
        if not integration:
            return False
        db.session.delete(integration)
        db.session.commit()
        return True

    @staticmethod
    def list():
        return Integration.query.all() 