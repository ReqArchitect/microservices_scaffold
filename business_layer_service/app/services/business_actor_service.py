from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessActor, db

class BusinessActorService:
    """
    Service layer for BusinessActor entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessActor]]:
        """
        Create a new BusinessActor.
        """
        if not data.get('name'):
            return False, 'Name is required', None
        actor = BusinessActor(**data)
        db.session.add(actor)
        db.session.commit()
        return True, 'BusinessActor created', actor

    @staticmethod
    def get(actor_id: int) -> Optional[BusinessActor]:
        """
        Get a BusinessActor by ID.
        """
        return BusinessActor.query.get(actor_id)

    @staticmethod
    def update(actor_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessActor]]:
        """
        Update a BusinessActor.
        """
        actor = BusinessActor.query.get(actor_id)
        if not actor:
            return False, 'BusinessActor not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(actor, field, data[field])
        db.session.commit()
        return True, 'BusinessActor updated', actor

    @staticmethod
    def delete(actor_id: int) -> bool:
        """
        Delete a BusinessActor.
        """
        actor = BusinessActor.query.get(actor_id)
        if not actor:
            return False
        db.session.delete(actor)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessActor]:
        """
        List all BusinessActors.
        """
        return BusinessActor.query.all() 