import uuid
import datetime

def generate_artifact_metadata(source, transformation, template_version, user_id=None, tenant_id=None):
    return {
        "artifact_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "source": source,
        "transformation": transformation,
        "template_version": template_version,
        "user_id": user_id,
        "tenant_id": tenant_id
    }

def log_audit_event(logger, event_type, details, user_id=None, tenant_id=None):
    logger.info("audit_event", event_type=event_type, details=details, user_id=user_id, tenant_id=tenant_id)

def assert_log_contains(logs, message):
    assert message in logs

def assert_metric_value(metrics, name, value):
    assert metrics.get(name) == value

def assert_audit_event(events, action):
    assert any(e['action'] == action for e in events) 