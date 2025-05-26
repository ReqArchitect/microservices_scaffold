from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Tenant, User, UserActivity
from app.utils import (
    validate_password, validate_email_format, generate_password_reset_token,
    generate_email_verification_token, log_user_activity
)

class UserService:
    """
    Service layer for user-related business logic.
    """
    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user and assign to a tenant.
        Returns (success, message, user)
        """
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")
        tenant_name = data.get("tenant_name")
        role = data.get("role", "user")

        if not all([email, password, full_name, tenant_name]):
            return False, "All fields are required", None

        is_valid_email, email_message = validate_email_format(email)
        if not is_valid_email:
            return False, email_message, None

        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            return False, password_message, None

        tenant = Tenant.query.filter_by(name=tenant_name).first()
        if not tenant:
            tenant = Tenant(name=tenant_name)
            db.session.add(tenant)
            db.session.commit()

        user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
        if user:
            return False, "User already exists", None

        if User.query.count() == 0:
            role = "vendor_admin"
        elif role not in ["vendor_admin", "tenant_admin", "user"]:
            role = "user"

        verification_token = generate_email_verification_token()
        new_user = User(
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            role=role,
            tenant_id=tenant.id,
            email_verification_token=verification_token
        )
        db.session.add(new_user)
        db.session.commit()
        log_user_activity(db, new_user.id, "register", {"tenant_id": tenant.id})
        return True, "User registered successfully", new_user

    @staticmethod
    def login(data: Dict[str, Any]) -> Tuple[bool, str, Optional[User], Optional[Tenant]]:
        """
        Authenticate user and return user and tenant if successful.
        """
        email = data.get("email")
        password = data.get("password")
        tenant_name = data.get("tenant_name")

        if not all([email, password, tenant_name]):
            return False, "All fields are required", None, None

        tenant = Tenant.query.filter_by(name=tenant_name).first()
        if not tenant:
            return False, "Invalid tenant", None, None

        user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
        if not user or not check_password_hash(user.password_hash, password):
            return False, "Invalid credentials", None, None

        if not user.is_active:
            return False, "Account is inactive", None, None

        user.last_login = datetime.utcnow()
        db.session.commit()
        log_user_activity(db, user.id, "login", {})
        return True, "Login successful", user, tenant

    @staticmethod
    def update_user(user: User, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update user profile fields.
        """
        if "full_name" in data:
            user.full_name = data["full_name"]
        if "preferences" in data:
            user.preferences = data["preferences"]
        db.session.commit()
        return True, "User updated successfully"

    @staticmethod
    def get_user_activity(user: User, limit: int = 10, offset: int = 0) -> list:
        """
        Get user activity log.
        """
        activities = UserActivity.query.filter_by(user_id=user.id)\
            .order_by(UserActivity.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        return activities 