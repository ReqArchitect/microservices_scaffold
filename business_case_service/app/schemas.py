from marshmallow import Schema, fields, validate

class BusinessCaseCreateSchema(Schema):
    title = fields.String(required=True)
    description = fields.String()
    justification = fields.String()
    expected_benefits = fields.String()
    risk_assessment = fields.String()
    start_date = fields.String(validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$'))
    end_date = fields.String(validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$'))

class BusinessCaseUpdateSchema(Schema):
    title = fields.String()
    description = fields.String()
    justification = fields.String()
    expected_benefits = fields.String()
    risk_assessment = fields.String()
    start_date = fields.String(validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$'))
    end_date = fields.String(validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$'))

class BusinessCaseResponseSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    tenant_id = fields.Int()
    title = fields.String()
    description = fields.String()
    justification = fields.String()
    expected_benefits = fields.String()
    risk_assessment = fields.String()
    start_date = fields.String()
    end_date = fields.String()
    created_at = fields.String()
    updated_at = fields.String() 