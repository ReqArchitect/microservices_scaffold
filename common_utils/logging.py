import structlog
import logging
import os

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    logger = structlog.get_logger()
    return logger

def log_with_context(logger, message, **kwargs):
    # Add trace_id, tenant_id, user_id if available
    trace_id = kwargs.get('trace_id') or os.environ.get('TRACE_ID')
    tenant_id = kwargs.get('tenant_id') or os.environ.get('TENANT_ID')
    user_id = kwargs.get('user_id') or os.environ.get('USER_ID')
    logger.info(message, trace_id=trace_id, tenant_id=tenant_id, user_id=user_id, **kwargs) 