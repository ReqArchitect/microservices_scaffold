from app import create_app, db
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app()

# Background thread for outbox processing
def process_outbox_events():
    """Background thread to process outbox events"""
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        from app.models import OutboxEvent, db
        
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types
        @processor.register_handler('user_created')
        def handle_user_created(aggregate_id, payload, event):
            """Handle user created events"""
            try:
                logger.info(f"Processing user_created event: {aggregate_id}")
                # Logic to notify other services about new user
            except Exception as e:
                logger.error(f"Error processing user_created event: {str(e)}")
                raise
        
        @processor.register_handler('user_updated')
        def handle_user_updated(aggregate_id, payload, event):
            """Handle user updated events"""
            try:
                logger.info(f"Processing user_updated event: {aggregate_id}")
                # Logic to notify other services about user updates
            except Exception as e:
                logger.error(f"Error processing user_updated event: {str(e)}")
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
outbox_enabled = app.config.get('OUTBOX_ENABLED', True)
if outbox_enabled:
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    logger.info("Started outbox processor")

if __name__ == "__main__":
    port = int(app.config.get('SERVICE_PORT', 5000))
    app.run(host="0.0.0.0", port=port)
        
        # Main processing loop
        while True:
            try:
                processed = processor.process_pending_events(limit=10)
                if processed > 0:
                    app.logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                app.logger.error(f"Error in outbox processor: {str(e)}")
            
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = app.config.get('OUTBOX_ENABLED', True)
if outbox_enabled:
    import threading
    import time
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    app.logger.info("Outbox processor started")


if __name__ == '__main__':
    app.run(debug=True) 