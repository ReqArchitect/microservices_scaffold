from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessObject, db

class BusinessObjectService:
    """
    Service layer for BusinessObject entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessObject]]:
        if not data.get('name'):
            return False, 'Name is required', None
        obj = BusinessObject(**data)
        db.session.add(obj)
        db.session.commit()
        return True, 'BusinessObject created', obj

    @staticmethod
    def get(object_id: int) -> Optional[BusinessObject]:
        return BusinessObject.query.get(object_id)

    @staticmethod
    def update(object_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessObject]]:
        obj = BusinessObject.query.get(object_id)
        if not obj:
            return False, 'BusinessObject not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(obj, field, data[field])
        db.session.commit()
        return True, 'BusinessObject updated', obj

    @staticmethod
    def delete(object_id: int) -> bool:
        obj = BusinessObject.query.get(object_id)
        if not obj:
            return False
        db.session.delete(obj)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessObject]:
        return BusinessObject.query.all() 