from typing import Any, Dict, Optional, Tuple, List
from datetime import datetime
from .models import BusinessCase, db

class BusinessCaseService:
    """
    Service layer for business case-related business logic.
    """
    @staticmethod
    def create(user_id: int, tenant_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessCase]]:
        """
        Create a new business case.
        """
        if not data.get('title'):
            return False, 'Title is required', None
        business_case = BusinessCase(
            user_id=user_id,
            tenant_id=tenant_id,
            title=data['title'],
            description=data.get('description'),
            justification=data.get('justification'),
            expected_benefits=data.get('expected_benefits'),
            risk_assessment=data.get('risk_assessment'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
        )
        db.session.add(business_case)
        db.session.commit()
        return True, 'Business case created', business_case

    @staticmethod
    def list(tenant_id: int) -> List[BusinessCase]:
        """
        List all business cases for a tenant.
        """
        return BusinessCase.query.filter_by(tenant_id=tenant_id).all()

    @staticmethod
    def get(case_id: int, tenant_id: int) -> Optional[BusinessCase]:
        """
        Get a business case by ID and tenant.
        """
        case = BusinessCase.query.get(case_id)
        if not case or case.tenant_id != tenant_id:
            return None
        return case

    @staticmethod
    def update(case_id: int, tenant_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[BusinessCase]]:
        """
        Update a business case.
        """
        case = BusinessCase.query.get(case_id)
        if not case or case.tenant_id != tenant_id:
            return False, 'BusinessCase not found', None
        for field in ['title', 'description', 'justification', 'expected_benefits', 'risk_assessment', 'start_date', 'end_date']:
            if field in data:
                if field in ['start_date', 'end_date']:
                    setattr(case, field, datetime.strptime(data[field], '%Y-%m-%d').date() if data[field] else None)
                else:
                    setattr(case, field, data[field])
        db.session.commit()
        return True, 'Business case updated', case

    @staticmethod
    def delete(case_id: int, tenant_id: int) -> bool:
        """
        Delete a business case.
        """
        case = BusinessCase.query.get(case_id)
        if not case or case.tenant_id != tenant_id:
            return False
        db.session.delete(case)
        db.session.commit()
        return True 