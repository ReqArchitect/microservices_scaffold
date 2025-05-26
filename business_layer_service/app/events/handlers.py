from ..models import db, BusinessCase, Initiative
from common_utils.outbox import OutboxEvent
import json
import logging

logger = logging.getLogger(__name__)

def handle_capability_event(event_data):
    """Handle capability events from the strategy service"""
    try:
        payload = json.loads(event_data.payload)
        business_context_id = payload.get('business_context_id')
        
        if business_context_id:
            business_case = BusinessCase.query.get(business_context_id)
            if business_case:
                business_case.create_outbox_event(
                    event_type="BusinessCaseCapabilityUpdated",
                    aggregate_type="BusinessCase",
                    aggregate_id=str(business_case.id),
                    payload=business_case.to_dict()
                )
        
        db.session.commit()
        logger.info(f"Processed capability event for business case {business_context_id}")
        
    except Exception as e:
        logger.error(f"Error handling capability event: {str(e)}")
        db.session.rollback()
        raise

def handle_course_of_action_event(event_data):
    """Handle course of action events from the strategy service"""
    try:
        payload = json.loads(event_data.payload)
        initiative_context_id = payload.get('initiative_context_id')
        
        if initiative_context_id:
            initiative = Initiative.query.get(initiative_context_id)
            if initiative:
                initiative.create_outbox_event(
                    event_type="InitiativeCourseOfActionUpdated",
                    aggregate_type="Initiative",
                    aggregate_id=str(initiative.id),
                    payload=initiative.to_dict()
                )
        
        db.session.commit()
        logger.info(f"Processed course of action event for initiative {initiative_context_id}")
        
    except Exception as e:
        logger.error(f"Error handling course of action event: {str(e)}")
        db.session.rollback()
        raise
