from .models import db, CostModel, UsageRecord, TCOScenario

class CostModelService:
    @staticmethod
    def create(data):
        model = CostModel(**data)
        db.session.add(model)
        db.session.commit()
        return model

    @staticmethod
    def get(model_id):
        return CostModel.query.get(model_id)

    @staticmethod
    def update(model_id, data):
        model = CostModel.query.get(model_id)
        if not model:
            return None
        for k, v in data.items():
            setattr(model, k, v)
        db.session.commit()
        return model

    @staticmethod
    def delete(model_id):
        model = CostModel.query.get(model_id)
        if not model:
            return False
        db.session.delete(model)
        db.session.commit()
        return True

    @staticmethod
    def list():
        return CostModel.query.all() 