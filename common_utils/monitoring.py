from prometheus_flask_exporter import PrometheusMetrics

def init_metrics(app):
    metrics = PrometheusMetrics(app)
    return metrics 