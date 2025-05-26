from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessCollaboration, db

class BusinessCollaborationService:
    """
    Service layer for BusinessCollaboration entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessCollaboration]]:
        if not data.get('name'):
            return False, 'Name is required', None
        collab = BusinessCollaboration(**data)
        db.session.add(collab)
        db.session.commit()
        return True, 'BusinessCollaboration created', collab

    @staticmethod
    def get(collab_id: int) -> Optional[BusinessCollaboration]:
        return BusinessCollaboration.query.get(collab_id)

    @staticmethod
    def update(collab_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessCollaboration]]:
        collab = BusinessCollaboration.query.get(collab_id)
        if not collab:
            return False, 'BusinessCollaboration not found', None
        for field in ['name', 'description', 'initiative_id']:
            if field in data:
                setattr(collab, field, data[field])
        db.session.commit()
        return True, 'BusinessCollaboration updated', collab

    @staticmethod
    def delete(collab_id: int) -> bool:
        collab = BusinessCollaboration.query.get(collab_id)
        if not collab:
            return False
        db.session.delete(collab)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessCollaboration]:
        return BusinessCollaboration.query.all() 