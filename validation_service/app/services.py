from .models import db, Policy, ValidationLog

class PolicyService:
    @staticmethod
    def create(data):
        policy = Policy(**data)
        db.session.add(policy)
        db.session.commit()
        return policy

    @staticmethod
    def get(policy_id):
        return Policy.query.get(policy_id)

    @staticmethod
    def update(policy_id, data):
        policy = Policy.query.get(policy_id)
        if not policy:
            return None
        for k, v in data.items():
            setattr(policy, k, v)
        db.session.commit()
        return policy

    @staticmethod
    def delete(policy_id):
        policy = Policy.query.get(policy_id)
        if not policy:
            return False
        db.session.delete(policy)
        db.session.commit()
        return True

    @staticmethod
    def list():
        return Policy.query.all() 