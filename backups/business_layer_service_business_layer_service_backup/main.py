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
        
        # Setup processor with handlers
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types
        @processor.register_handler('business_case_created')
        def handle_business_case_created(aggregate_id, payload, event):
            """Handle business case created events"""
            try:
                logger.info(f"Processing business_case_created event: {aggregate_id}")
                # Logic to notify other services
                # This could use circuit breaker, etc.
            except Exception as e:
                logger.error(f"Error processing business_case_created event: {str(e)}")
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
    port = int(os.environ.get('SERVICE_PORT', 5002))
    app.run(host="0.0.0.0", port=port)
