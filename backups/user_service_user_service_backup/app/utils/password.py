import re
import secrets

def validate_password(password):
    """Validate password complexity"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_email_format(email):
    """Validate email format"""
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, email
        return False, "Invalid email format"
    except Exception as e:
        return False, str(e)

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def generate_password_reset_token():
    """Generate a password reset token"""
    return generate_token()

def generate_email_verification_token():
    """Generate an email verification token"""
    return generate_token() 