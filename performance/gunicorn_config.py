# Flask optimizations for production environments

# Gunicorn configuration
bind = "0.0.0.0:${SERVICE_PORT}"
workers = 4
worker_class = "gevent"
worker_connections = 1000
keepalive = 5
timeout = 30
graceful_timeout = 10
max_requests = 1000
max_requests_jitter = 50

# Enable preloading for faster startup (but disables graceful reloading)
preload_app = True

# Set logging configurations
errorlog = "-"  # stderr
loglevel = "info"
accesslog = "-"  # stdout
access_log_format = '%({X-Request-ID}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" - %(L)s'

# Process naming
proc_name = "${SERVICE_NAME}"

# Performance monitoring with statsd
statsd_host = "${STATSD_HOST:-localhost:8125}"
statsd_prefix = "${SERVICE_NAME}"

# Called after the worker has been initialized but before it processes any requests
def post_fork(server, worker):
    import logging
    logging.info(f"Worker {worker.pid} spawned")

# Called just before a worker processes the request
def pre_request(worker, req):
    req.start_time = time.time()

# Called after a worker processes the request
def post_request(worker, req, environ, resp):
    request_time = time.time() - req.start_time
    worker.statsd_client.timing('request.time', request_time * 1000)
