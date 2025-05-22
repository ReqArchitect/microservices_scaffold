from flask_jwt_extended import get_jwt
import logging

def get_identity():
    claims = get_jwt()
    logging.getLogger(__name__).debug(f"get_identity: claims={claims}")
    user_id = claims.get('sub', {}).get('id') if isinstance(claims.get('sub'), dict) else claims.get('sub')
    tenant_id = claims.get('tenant_id')
    role = claims.get('role')
    logging.getLogger(__name__).debug(f"get_identity: user_id={user_id}, tenant_id={tenant_id}, role={role}")
    return user_id, tenant_id, role 