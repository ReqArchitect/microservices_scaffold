from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessEvent, db

class BusinessEventService:
    """
    Service layer for BusinessEvent entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessEvent]]:
        if not data.get('name'):
            return False, 'Name is required', None
        event = BusinessEvent(**data)
        db.session.add(event)
        db.session.commit()
        return True, 'BusinessEvent created', event

    @staticmethod
    def get(event_id: int) -> Optional[BusinessEvent]:
        return BusinessEvent.query.get(event_id)

    @staticmethod
    def update(event_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessEvent]]:
        event = BusinessEvent.query.get(event_id)
        if not event:
            return False, 'BusinessEvent not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(event, field, data[field])
        db.session.commit()
        return True, 'BusinessEvent updated', event

    @staticmethod
    def delete(event_id: int) -> bool:
        event = BusinessEvent.query.get(event_id)
        if not event:
            return False
        db.session.delete(event)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessEvent]:
        return BusinessEvent.query.all() 