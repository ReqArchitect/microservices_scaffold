from .models import AuditLog, db

class AuditService:
    @staticmethod
    def create_log(data):
        log = AuditLog(**data)
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_log(log_id):
        return AuditLog.query.get(log_id)

    @staticmethod
    def get_logs(limit=10, offset=0):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def log_event(event_type, user_id=None, tenant_id=None, details=None):
        log = AuditLog(event_type=event_type, user_id=user_id, tenant_id=tenant_id, details=details)
        db.session.add(log)
        db.session.commit()
        return log 