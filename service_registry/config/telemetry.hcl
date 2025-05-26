telemetry {
  statsd_address = "localhost:9125"
  disable_hostname = false
  enable_hostname_label = true
  prometheus_retention_time = "24h"
  prefix = "reqarchitect"

  metrics_health {
    enabled = true
    interval = "10s"
  }

  dogstatsd_tags = ["dc=primary", "service=consul"]
}

ui_config {
  metrics_provider = "prometheus"
  metrics_proxy {
    base_url = "http://localhost:9090"
  }
}
