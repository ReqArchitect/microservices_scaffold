from typing import Any, Dict, Optional, Tuple, List
from ..models import BusinessProcess, db

class BusinessProcessService:
    """
    Service layer for BusinessProcess entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessProcess]]:
        """
        Create a new BusinessProcess.
        """
        if not data.get('name'):
            return False, 'Name is required', None
        process = BusinessProcess(**data)
        db.session.add(process)
        db.session.commit()
        return True, 'BusinessProcess created', process

    @staticmethod
    def get(process_id: int) -> Optional[BusinessProcess]:
        """
        Get a BusinessProcess by ID.
        """
        return BusinessProcess.query.get(process_id)

    @staticmethod
    def update(process_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessProcess]]:
        """
        Update a BusinessProcess.
        """
        process = BusinessProcess.query.get(process_id)
        if not process:
            return False, 'BusinessProcess not found', None
        for field in ['name', 'description', 'initiative_id', 'kpi_id']:
            if field in data:
                setattr(process, field, data[field])
        db.session.commit()
        return True, 'BusinessProcess updated', process

    @staticmethod
    def delete(process_id: int) -> bool:
        """
        Delete a BusinessProcess.
        """
        process = BusinessProcess.query.get(process_id)
        if not process:
            return False
        db.session.delete(process)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[BusinessProcess]:
        """
        List all BusinessProcesses.
        """
        return BusinessProcess.query.all() 