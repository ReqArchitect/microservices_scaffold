from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessRole, db

class BusinessRoleService:
    """
    Service layer for BusinessRole entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessRole]]:
        """
        Create a new BusinessRole.
        """
        if not data.get('name'):
            return False, 'Name is required', None
        role = BusinessRole(**data)
        db.session.add(role)
        db.session.commit()
        return True, 'BusinessRole created', role

    @staticmethod
    def get(role_id: int) -> Optional[BusinessRole]:
        """
        Get a BusinessRole by ID.
        """
        return BusinessRole.query.get(role_id)

    @staticmethod
    def update(role_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessRole]]:
        """
        Update a BusinessRole.
        """
        role = BusinessRole.query.get(role_id)
        if not role:
            return False, 'BusinessRole not found', None
        for field in ['name', 'description']:
            if field in data:
                setattr(role, field, data[field])
        db.session.commit()
        return True, 'BusinessRole updated', role

    @staticmethod
    def delete(role_id: int) -> bool:
        """
        Delete a BusinessRole.
        """
        role = BusinessRole.query.get(role_id)
        if not role:
            return False
        db.session.delete(role)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessRole]:
        """
        List all BusinessRoles.
        """
        return BusinessRole.query.all() 