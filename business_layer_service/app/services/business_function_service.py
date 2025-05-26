from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessFunction, db

class BusinessFunctionService:
    """
    Service layer for BusinessFunction entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessFunction]]:
        if not data.get('name'):
            return False, 'Name is required', None
        function = BusinessFunction(**data)
        db.session.add(function)
        db.session.commit()
        return True, 'BusinessFunction created', function

    @staticmethod
    def get(function_id: int) -> Optional[BusinessFunction]:
        return BusinessFunction.query.get(function_id)

    @staticmethod
    def update(function_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessFunction]]:
        function = BusinessFunction.query.get(function_id)
        if not function:
            return False, 'BusinessFunction not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(function, field, data[field])
        db.session.commit()
        return True, 'BusinessFunction updated', function

    @staticmethod
    def delete(function_id: int) -> bool:
        function = BusinessFunction.query.get(function_id)
        if not function:
            return False
        db.session.delete(function)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessFunction]:
        return BusinessFunction.query.all() 