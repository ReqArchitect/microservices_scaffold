from marshmallow import Schema, fields

class BusinessActorCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessActorUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessActorResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessProcessCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)
    kpi_id = fields.Int(allow_none=True)

class BusinessProcessUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)
    kpi_id = fields.Int(allow_none=True)

class BusinessProcessResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)
    kpi_id = fields.Int(allow_none=True)

class GoalCreateSchema(Schema):
    title = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    business_case_id = fields.Int(allow_none=True)

class GoalUpdateSchema(Schema):
    title = fields.String()
    description = fields.String()
    business_case_id = fields.Int(allow_none=True)

class GoalResponseSchema(Schema):
    id = fields.Int()
    title = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    business_case_id = fields.Int(allow_none=True)

class ObjectiveCreateSchema(Schema):
    title = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    goal_id = fields.Int(allow_none=True)

class ObjectiveUpdateSchema(Schema):
    title = fields.String()
    description = fields.String()
    goal_id = fields.Int(allow_none=True)

class ObjectiveResponseSchema(Schema):
    id = fields.Int()
    title = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    goal_id = fields.Int(allow_none=True)

class BusinessRoleCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)

class BusinessRoleUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()

class BusinessRoleResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()

class BusinessCollaborationCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessCollaborationUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessCollaborationResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessInterfaceCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessInterfaceUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessInterfaceResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessFunctionCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessFunctionUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessFunctionResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessInteractionCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessInteractionUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessInteractionResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessEventCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessEventUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessEventResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessServiceCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessServiceUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessServiceResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class BusinessObjectCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class BusinessObjectUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class BusinessObjectResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class ContractCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class ContractUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class ContractResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True)

class ProductCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    user_id = fields.Int(required=True)
    tenant_id = fields.Int(required=True)
    initiative_id = fields.Int(allow_none=True)

class ProductUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    initiative_id = fields.Int(allow_none=True)

class ProductResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    user_id = fields.Int()
    tenant_id = fields.Int()
    initiative_id = fields.Int(allow_none=True) 