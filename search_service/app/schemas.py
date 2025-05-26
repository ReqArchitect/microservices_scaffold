from marshmallow import Schema, fields

class SearchQuerySchema(Schema):
    id = fields.Int(dump_only=True)
    query = fields.Str(required=True)
    user_id = fields.Int(allow_none=True)
    tenant_id = fields.Int(allow_none=True)
    results = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True) 