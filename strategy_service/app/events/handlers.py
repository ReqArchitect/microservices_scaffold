from ..models import db, Capability, CourseOfAction
from common_utils.outbox import OutboxEvent
import json
import logging

logger = logging.getLogger(__name__)

def handle_business_case_event(event_data):
    """Handle business case events from the business layer service"""
    try:
        payload = json.loads(event_data.payload)
        business_case_id = payload.get('id')
        
        # Update all capabilities linked to this business case
        capabilities = Capability.query.filter_by(business_context_id=business_case_id).all()
        for capability in capabilities:
            capability.create_outbox_event(
                event_type="CapabilityContextUpdated",
                aggregate_type="Capability",
                aggregate_id=str(capability.id),
                payload=capability.to_dict()
            )
        
        db.session.commit()
        logger.info(f"Processed business case event for {len(capabilities)} capabilities")
        
    except Exception as e:
        logger.error(f"Error handling business case event: {str(e)}")
        db.session.rollback()
        raise

def handle_initiative_event(event_data):
    """Handle initiative events from the business layer service"""
    try:
        payload = json.loads(event_data.payload)
        initiative_id = payload.get('id')
        
        # Update capabilities
        capabilities = Capability.query.filter_by(initiative_context_id=initiative_id).all()
        for capability in capabilities:
            capability.create_outbox_event(
                event_type="CapabilityContextUpdated",
                aggregate_type="Capability",
                aggregate_id=str(capability.id),
                payload=capability.to_dict()
            )
            
        # Update courses of action
        actions = CourseOfAction.query.filter_by(initiative_context_id=initiative_id).all()
        for action in actions:
            action.create_outbox_event(
                event_type="CourseOfActionContextUpdated",
                aggregate_type="CourseOfAction",
                aggregate_id=str(action.id),
                payload=action.to_dict()
            )
        
        db.session.commit()
        logger.info(f"Processed initiative event for {len(capabilities)} capabilities and {len(actions)} courses of action")
        
    except Exception as e:
        logger.error(f"Error handling initiative event: {str(e)}")
        db.session.rollback()
        raise
