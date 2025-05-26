from marshmallow import Schema, fields

class AuditLogSchema(Schema):
    id = fields.Int(dump_only=True)
    event_type = fields.Str(required=True)
    user_id = fields.Int(allow_none=True)
    tenant_id = fields.Int(allow_none=True)
    details = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True) 