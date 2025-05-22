from app import create_app

app = create_app()


# Background thread for outbox processing
def process_outbox_events():
    """Background thread to process outbox events"""
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        from app.models import OutboxEvent
        
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types (customize for each service)
        # Example handler:
        # @processor.register_handler('entity_created')
        # def handle_entity_created(aggregate_id, payload, event):
        #     # Handle the event
        #     pass
        
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
    app.run(host='0.0.0.0', port=5000) 