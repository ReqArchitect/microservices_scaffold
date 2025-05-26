from marshmallow import Schema, fields, validate, validates, ValidationError
from typing import Any, Dict

class RegisterRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    full_name = fields.String(required=True)
    tenant_name = fields.String(required=True)
    role = fields.String(validate=validate.OneOf(["vendor_admin", "tenant_admin", "user"]))

class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    tenant_name = fields.String(required=True)

class UpdateUserRequestSchema(Schema):
    full_name = fields.String()
    preferences = fields.Dict()

class UserResponseSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    full_name = fields.String()
    role = fields.String()
    tenant_id = fields.Int()
    is_email_verified = fields.Bool()
    preferences = fields.Dict()
    last_login = fields.DateTime(allow_none=True)

class UserActivityResponseSchema(Schema):
    action = fields.String()
    details = fields.Dict()
    ip_address = fields.String()
    created_at = fields.DateTime() 