from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Tenant, UserActivity

class AuthService:
    """
    Service layer for authentication-related business logic.
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
        tenant_id = data.get("tenant_id")
        role = data.get("role", "user")

        if not all([email, password, full_name, tenant_id]):
            return False, "All fields are required", None

        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return False, "Invalid tenant", None

        user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
        if user:
            return False, "User already exists", None

        new_user = User(
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            role=role,
            tenant_id=tenant.id
        )
        db.session.add(new_user)
        db.session.commit()
        # Log activity
        activity = UserActivity(
            user_id=new_user.id,
            action="register",
            details={"tenant_id": tenant.id}
        )
        db.session.add(activity)
        db.session.commit()
        return True, "User registered successfully", new_user

    @staticmethod
    def login(data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user and return user if successful.
        """
        email = data.get("email")
        password = data.get("password")
        tenant_id = data.get("tenant_id")

        if not all([email, password, tenant_id]):
            return False, "All fields are required", None

        user = User.query.filter_by(email=email, tenant_id=tenant_id).first()
        if not user or not check_password_hash(user.password_hash, password):
            return False, "Invalid credentials", None

        if not user.is_active:
            return False, "Account is inactive", None

        user.last_login = datetime.utcnow()
        db.session.commit()
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action="login",
            details={}
        )
        db.session.add(activity)
        db.session.commit()
        return True, "Login successful", user

    @staticmethod
    def refresh(user: User) -> Tuple[bool, str]:
        """
        Refresh user session/token.
        """
        if not user or not user.is_active:
            return False, "Invalid refresh token"
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action="token_refresh",
            details={}
        )
        db.session.add(activity)
        db.session.commit()
        return True, "Token refreshed"

    @staticmethod
    def logout(user: User) -> Tuple[bool, str]:
        """
        Log out user.
        """
        if not user:
            return False, "User not found"
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action="logout",
            details={}
        )
        db.session.add(activity)
        db.session.commit()
        return True, "Logged out successfully" 