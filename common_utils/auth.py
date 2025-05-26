from flask_jwt_extended import get_jwt_identity, get_jwt

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id 