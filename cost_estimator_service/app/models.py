from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.JSON, nullable=True)

class UsageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost_model_id = db.Column(db.Integer, db.ForeignKey('cost_model.id'), nullable=False)
    usage_amount = db.Column(db.Float, nullable=False)
    usage_date = db.Column(db.Date, nullable=False)

class TCOScenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    cost_model_id = db.Column(db.Integer, db.ForeignKey('cost_model.id'), nullable=False)
    scenario_data = db.Column(db.JSON, nullable=True) 