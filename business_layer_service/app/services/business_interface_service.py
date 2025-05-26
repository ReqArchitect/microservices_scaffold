from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessInterface, db

class BusinessInterfaceService:
    """
    Service layer for BusinessInterface entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessInterface]]:
        if not data.get('name'):
            return False, 'Name is required', None
        interface = BusinessInterface(**data)
        db.session.add(interface)
        db.session.commit()
        return True, 'BusinessInterface created', interface

    @staticmethod
    def get(interface_id: int) -> Optional[BusinessInterface]:
        return BusinessInterface.query.get(interface_id)

    @staticmethod
    def update(interface_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessInterface]]:
        interface = BusinessInterface.query.get(interface_id)
        if not interface:
            return False, 'BusinessInterface not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(interface, field, data[field])
        db.session.commit()
        return True, 'BusinessInterface updated', interface

    @staticmethod
    def delete(interface_id: int) -> bool:
        interface = BusinessInterface.query.get(interface_id)
        if not interface:
            return False
        db.session.delete(interface)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessInterface]:
        return BusinessInterface.query.all() 