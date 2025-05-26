from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessInteraction, db

class BusinessInteractionService:
    """
    Service layer for BusinessInteraction entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessInteraction]]:
        if not data.get('name'):
            return False, 'Name is required', None
        interaction = BusinessInteraction(**data)
        db.session.add(interaction)
        db.session.commit()
        return True, 'BusinessInteraction created', interaction

    @staticmethod
    def get(interaction_id: int) -> Optional[BusinessInteraction]:
        return BusinessInteraction.query.get(interaction_id)

    @staticmethod
    def update(interaction_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessInteraction]]:
        interaction = BusinessInteraction.query.get(interaction_id)
        if not interaction:
            return False, 'BusinessInteraction not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(interaction, field, data[field])
        db.session.commit()
        return True, 'BusinessInteraction updated', interaction

    @staticmethod
    def delete(interaction_id: int) -> bool:
        interaction = BusinessInteraction.query.get(interaction_id)
        if not interaction:
            return False
        db.session.delete(interaction)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessInteraction]:
        return BusinessInteraction.query.all() 