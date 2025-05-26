from flask import Header, HTTPException, status

def get_identity(
    x_user_id: str = Header(None, alias="X-User-ID"),
    x_tenant_id: str = Header(None, alias="X-Tenant-ID")
):
    if not x_user_id or not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing required identity headers")
    try:
        return {"user_id": int(x_user_id), "tenant_id": int(x_tenant_id)}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid identity header values") 