from marshmallow import Schema, fields

class ReportSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    user_id = fields.Int(allow_none=True)
    tenant_id = fields.Int(allow_none=True)
    parameters = fields.Dict(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(allow_none=True) 