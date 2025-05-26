from ..models import db, ApplicationComponent, ApplicationService, ApplicationInterface
from common_utils.outbox import OutboxEvent
import json
import logging

logger = logging.getLogger(__name__)

def handle_capability_event(event_data):
    """Handle capability events from the strategy service"""
    try:
        payload = json.loads(event_data.payload)
        capability_id = payload.get('id')
        
        # Update application components related to the capability
        components = ApplicationComponent.query.filter_by(capability_context_id=capability_id).all()
        for component in components:
            component.create_outbox_event(
                event_type="ApplicationComponentCapabilityUpdated",
                aggregate_type="ApplicationComponent",
                aggregate_id=str(component.id),
                payload=component.to_dict()
            )
            
        # Update application services
        services = ApplicationService.query.filter_by(capability_context_id=capability_id).all()
        for service in services:
            service.create_outbox_event(
                event_type="ApplicationServiceCapabilityUpdated",
                aggregate_type="ApplicationService",
                aggregate_id=str(service.id),
                payload=service.to_dict()
            )
        
        db.session.commit()
        logger.info(f"Processed capability event for {len(components)} components and {len(services)} services")
        
    except Exception as e:
        logger.error(f"Error handling capability event: {str(e)}")
        db.session.rollback()
        raise

def handle_course_of_action_event(event_data):
    """Handle course of action events from the strategy service"""
    try:
        payload = json.loads(event_data.payload)
        coa_id = payload.get('id')
        
        # Update application interfaces
        interfaces = ApplicationInterface.query.filter_by(course_of_action_context_id=coa_id).all()
        for interface in interfaces:
            interface.create_outbox_event(
                event_type="ApplicationInterfaceCourseOfActionUpdated",
                aggregate_type="ApplicationInterface",
                aggregate_id=str(interface.id),
                payload=interface.to_dict()
            )
        
        db.session.commit()
        logger.info(f"Processed course of action event for {len(interfaces)} interfaces")
        
    except Exception as e:
        logger.error(f"Error handling course of action event: {str(e)}")
        db.session.rollback()
        raise
