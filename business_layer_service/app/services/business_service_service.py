from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessService, db

class BusinessServiceService:
    """
    Service layer for BusinessService entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessService]]:
        if not data.get('name'):
            return False, 'Name is required', None
        service = BusinessService(**data)
        db.session.add(service)
        db.session.commit()
        return True, 'BusinessService created', service

    @staticmethod
    def get(service_id: int) -> Optional[BusinessService]:
        return BusinessService.query.get(service_id)

    @staticmethod
    def update(service_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessService]]:
        service = BusinessService.query.get(service_id)
        if not service:
            return False, 'BusinessService not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(service, field, data[field])
        db.session.commit()
        return True, 'BusinessService updated', service

    @staticmethod
    def delete(service_id: int) -> bool:
        service = BusinessService.query.get(service_id)
        if not service:
            return False
        db.session.delete(service)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessService]:
        return BusinessService.query.all() 