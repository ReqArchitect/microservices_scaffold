from marshmallow import Schema, fields

class IntegrationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    config = fields.Dict()

class IntegrationEventSchema(Schema):
    id = fields.Int(dump_only=True)
    integration_id = fields.Int(required=True)
    event_type = fields.Str(required=True)
    payload = fields.Dict(required=True)
    created_at = fields.DateTime(dump_only=True)

class IntegrationLogSchema(Schema):
    id = fields.Int(dump_only=True)
    integration_id = fields.Int(required=True)
    message = fields.Str(required=True)
    level = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True) 