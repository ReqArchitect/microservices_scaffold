acl {
  enabled = true
  default_policy = "deny"
  tokens {
    initial_management = "${CONSUL_HTTP_TOKEN}"
  }
}

encrypt = "${CONSUL_GOSSIP_ENCRYPTION_KEY}"
