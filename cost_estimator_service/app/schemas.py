from marshmallow import Schema, fields

class CostModelSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    parameters = fields.Dict()

class UsageRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    cost_model_id = fields.Int(required=True)
    usage_amount = fields.Float(required=True)
    usage_date = fields.Date(required=True)

class TCOScenarioSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    cost_model_id = fields.Int(required=True)
    scenario_data = fields.Dict() 