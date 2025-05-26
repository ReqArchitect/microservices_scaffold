from typing import Any, Dict, Optional, Tuple, List
from ..models import Objective, db

class ObjectiveService:
    """
    Service layer for Objective entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Objective]]:
        """
        Create a new Objective.
        """
        if not data.get('title'):
            return False, 'Title is required', None
        objective = Objective(**data)
        db.session.add(objective)
        db.session.commit()
        return True, 'Objective created', objective

    @staticmethod
    def get(objective_id: int) -> Optional[Objective]:
        """
        Get an Objective by ID.
        """
        return Objective.query.get(objective_id)

    @staticmethod
    def update(objective_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Objective]]:
        """
        Update an Objective.
        """
        objective = Objective.query.get(objective_id)
        if not objective:
            return False, 'Objective not found', None
        for field in ['title', 'description', 'goal_id']:
            if field in data:
                setattr(objective, field, data[field])
        db.session.commit()
        return True, 'Objective updated', objective

    @staticmethod
    def delete(objective_id: int) -> bool:
        """
        Delete an Objective.
        """
        objective = Objective.query.get(objective_id)
        if not objective:
            return False
        db.session.delete(objective)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[Objective]:
        """
        List all Objectives.
        """
        return Objective.query.all() 