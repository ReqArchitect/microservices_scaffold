telemetry {
  prometheus_retention_time = "24h"
  enable_hostname = true
  prefix = "reqarchitect"
}

acl {
  enabled = true
  default_policy = "deny"
  down_policy = "extend-cache"
}

performance {
  raft_multiplier = 1
}

tls {
  defaults {
    verify_incoming = true
    verify_outgoing = true
  }
}

log_level = "INFO"
