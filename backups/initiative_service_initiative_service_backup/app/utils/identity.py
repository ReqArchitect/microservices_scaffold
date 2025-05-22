from flask import request, abort

def get_identity():
    user_id = request.headers.get("X-User-ID")
    tenant_id = request.headers.get("X-Tenant-ID")
    if not user_id or not tenant_id:
        abort(403, description="Missing required identity headers")
    try:
        return int(user_id), int(tenant_id)
    except ValueError:
        abort(403, description="Invalid identity header values") 