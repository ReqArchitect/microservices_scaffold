from marshmallow import Schema, fields

class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    currency = fields.Str(required=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    plan = fields.Str(required=True)
    status = fields.Str()
    started_at = fields.DateTime(dump_only=True)
    ended_at = fields.DateTime(allow_none=True) 