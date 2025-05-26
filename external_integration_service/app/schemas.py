from marshmallow import Schema, fields

class IntegrationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    config = fields.Dict(allow_none=True)
    tenant_id = fields.Int(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class IntegrationEventSchema(Schema):
    id = fields.Int(dump_only=True)
    integration_id = fields.Int(required=True)
    event_type = fields.Str(required=True)
    payload = fields.Dict(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True) 