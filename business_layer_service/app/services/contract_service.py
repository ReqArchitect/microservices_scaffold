from typing import Any, Dict, Optional, Tuple, List
from ..models import Contract, db

class ContractService:
    """
    Service layer for Contract entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Contract]]:
        if not data.get('name'):
            return False, 'Name is required', None
        contract = Contract(**data)
        db.session.add(contract)
        db.session.commit()
        return True, 'Contract created', contract

    @staticmethod
    def get(contract_id: int) -> Optional[Contract]:
        return Contract.query.get(contract_id)

    @staticmethod
    def update(contract_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Contract]]:
        contract = Contract.query.get(contract_id)
        if not contract:
            return False, 'Contract not found', None
        for field in ['name', 'description']:
            if field in data:
                setattr(contract, field, data[field])
        db.session.commit()
        return True, 'Contract updated', contract

    @staticmethod
    def delete(contract_id: int) -> bool:
        contract = Contract.query.get(contract_id)
        if not contract:
            return False
        db.session.delete(contract)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[Contract]:
        return Contract.query.all() 