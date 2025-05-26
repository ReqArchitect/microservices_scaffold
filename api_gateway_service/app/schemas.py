from marshmallow import Schema, fields

class APILogSchema(Schema):
    id = fields.Int(dump_only=True)
    path = fields.Str(required=True)
    method = fields.Str(required=True)
    status_code = fields.Int(required=True)
    user_id = fields.Int(allow_none=True)
    tenant_id = fields.Int(allow_none=True)
    request_data = fields.Dict(allow_none=True)
    response_data = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True) 