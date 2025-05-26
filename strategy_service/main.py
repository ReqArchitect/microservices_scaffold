import dotenv
import os
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app, db
from app.models import OutboxEvent

app = create_app()

# Background thread for outbox processing
def process_outbox_events():
    """Background thread to process outbox events"""
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
<<<<<<< HEAD
        import requests
        from requests.exceptions import RequestException
=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
        
        # Setup processor with handlers
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types
        @processor.register_handler('capability_created')
        def handle_capability_created(aggregate_id, payload, event):
            """Handle capability created events"""
            try:
                logger.info(f"Processing capability_created event: {aggregate_id}")
<<<<<<< HEAD
                
                # Notify business layer service
                business_layer_url = app.config.get('BUSINESS_LAYER_SERVICE_URL', 'http://localhost:5002')
                response = requests.post(
                    f"{business_layer_url}/api/v1/notifications/capabilities",
                    json={
                        "event_type": "capability_created",
                        "capability_id": aggregate_id,
                        "data": payload
                    }
                )
                response.raise_for_status()
                
                # Notify initiative service if there's an initiative context
                if payload.get('initiative_context_id'):
                    initiative_url = app.config.get('INITIATIVE_SERVICE_URL', 'http://localhost:5003')
                    response = requests.post(
                        f"{initiative_url}/api/v1/notifications/capabilities",
                        json={
                            "event_type": "capability_created",
                            "capability_id": aggregate_id,
                            "initiative_id": payload['initiative_context_id'],
                            "data": payload
                        }
                    )
                    response.raise_for_status()
                
            except RequestException as e:
                logger.error(f"Error processing capability_created event {aggregate_id}: {str(e)}")
                raise
        
        @processor.register_handler('capability_updated')
        def handle_capability_updated(aggregate_id, payload, event):
            """Handle capability updated events"""
            try:
                logger.info(f"Processing capability_updated event: {aggregate_id}")
                changes = payload.get('changes', {})
                full_object = payload.get('full_object', {})
                
                # Notify services about the update
                services_to_notify = []
                
                # Always notify business layer
                services_to_notify.append(('BUSINESS_LAYER_SERVICE_URL', 'http://localhost:5002'))
                
                # Notify initiative service if initiative context changed or exists
                if 'initiative_context_id' in changes or full_object.get('initiative_context_id'):
                    services_to_notify.append(('INITIATIVE_SERVICE_URL', 'http://localhost:5003'))
                
                for service_key, default_url in services_to_notify:
                    service_url = app.config.get(service_key, default_url)
                    response = requests.post(
                        f"{service_url}/api/v1/notifications/capabilities",
                        json={
                            "event_type": "capability_updated",
                            "capability_id": aggregate_id,
                            "changes": changes,
                            "data": full_object
                        }
                    )
                    response.raise_for_status()
                    
            except RequestException as e:
                logger.error(f"Error processing capability_updated event {aggregate_id}: {str(e)}")
                raise
        
        @processor.register_handler('capability_deleted')
        def handle_capability_deleted(aggregate_id, payload, event):
            """Handle capability deleted events"""
            try:
                logger.info(f"Processing capability_deleted event: {aggregate_id}")
                
                # Notify all related services about deletion
                services = [
                    ('BUSINESS_LAYER_SERVICE_URL', 'http://localhost:5002'),
                    ('INITIATIVE_SERVICE_URL', 'http://localhost:5003')
                ]
                
                for service_key, default_url in services:
                    service_url = app.config.get(service_key, default_url)
                    response = requests.post(
                        f"{service_url}/api/v1/notifications/capabilities",
                        json={
                            "event_type": "capability_deleted",
                            "capability_id": aggregate_id
                        }
                    )
                    response.raise_for_status()
                    
            except RequestException as e:
                logger.error(f"Error processing capability_deleted event {aggregate_id}: {str(e)}")
=======
                # Logic to notify business layer service or other dependent services
                # For example, using requests.post or other mechanisms
                # This could use circuit breaker, etc.
            except Exception as e:
                logger.error(f"Error processing capability_created event: {str(e)}")
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
                raise
        
        # Main processing loop
        while True:
            try:
                processed = processor.process_pending_events(limit=10)
                if processed > 0:
                    logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                logger.error(f"Error in outbox processor: {str(e)}")
            
            # Sleep between processing rounds
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
if outbox_enabled:
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    logger.info("Started outbox processor thread")

if __name__ == "__main__":
    # Fix port conflict in docker-compose-enhanced.yml
    port = int(os.environ.get('SERVICE_PORT', 5001))
    app.run(host="0.0.0.0", port=port)
