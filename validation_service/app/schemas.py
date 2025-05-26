from marshmallow import Schema, fields

class PolicySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    policy_text = fields.Str(required=True)
    is_active = fields.Bool()

class ValidationLogSchema(Schema):
    id = fields.Int(dump_only=True)
    policy_id = fields.Int(required=True)
    input_data = fields.Dict(required=True)
    result = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True) 