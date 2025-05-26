from .models import APILog, db

class APIGatewayService:
    @staticmethod
    def create_log(data):
        log = APILog(**data)
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_log(log_id):
        return APILog.query.get(log_id)

    @staticmethod
    def get_logs(limit=10, offset=0):
        return APILog.query.order_by(APILog.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def log_api_call(path, method, status_code, user_id=None, tenant_id=None, request_data=None, response_data=None):
        log = APILog(path=path, method=method, status_code=status_code, user_id=user_id, tenant_id=tenant_id, request_data=request_data, response_data=response_data)
        db.session.add(log)
        db.session.commit()
        return log 