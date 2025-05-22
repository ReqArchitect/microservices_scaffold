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
        @processor.register_handler('capability_created')
        def handle_capability_created(aggregate_id, payload, event):
            """Handle capability created events"""
            try:
                logger.info(f"Processing capability_created event: {aggregate_id}")
                # Logic to notify business layer service or other dependent services
                # For example, using requests.post or other mechanisms
                # This could use circuit breaker, etc.
            except Exception as e:
                logger.error(f"Error processing capability_created event: {str(e)}")
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
