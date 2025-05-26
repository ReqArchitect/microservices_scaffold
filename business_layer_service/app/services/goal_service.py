from typing import Any, Dict, Optional, Tuple, List
from ..models import Goal, db

class GoalService:
    """
    Service layer for Goal entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Goal]]:
        """
        Create a new Goal.
        """
        if not data.get('title'):
            return False, 'Title is required', None
        goal = Goal(**data)
        db.session.add(goal)
        db.session.commit()
        return True, 'Goal created', goal

    @staticmethod
    def get(goal_id: int) -> Optional[Goal]:
        """
        Get a Goal by ID.
        """
        return Goal.query.get(goal_id)

    @staticmethod
    def update(goal_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Goal]]:
        """
        Update a Goal.
        """
        goal = Goal.query.get(goal_id)
        if not goal:
            return False, 'Goal not found', None
        for field in ['title', 'description', 'business_case_id']:
            if field in data:
                setattr(goal, field, data[field])
        db.session.commit()
        return True, 'Goal updated', goal

    @staticmethod
    def delete(goal_id: int) -> bool:
        """
        Delete a Goal.
        """
        goal = Goal.query.get(goal_id)
        if not goal:
            return False
        db.session.delete(goal)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[Goal]:
        """
        List all Goals.
        """
        return Goal.query.all() 