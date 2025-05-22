def log_user_activity(db, user_id, action, details=None, ip_address=None):
    """Log user activity"""
    from app.models import UserActivity
    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(activity)
    db.session.commit() 