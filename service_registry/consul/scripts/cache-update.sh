#!/bin/bash

# This script is triggered by Consul watch when Redis service changes
# It notifies affected services to update their cache configuration

# Get the current Redis endpoints
REDIS_ENDPOINTS=$(curl -s http://localhost:8500/v1/health/service/redis | jq -r '.[] | select(.Checks[].Status=="passing") | .Service.Address + ":" + (.Service.Port | tostring)')

# Update the cache configuration in Consul KV store
curl -X PUT -d "$REDIS_ENDPOINTS" http://localhost:8500/v1/kv/reqarchitect/cache/redis_endpoints

# Notify services that need to update their cache configuration
for SERVICE in $(curl -s http://localhost:8500/v1/agent/services | jq -r 'keys[]'); do
    if [[ "$SERVICE" != "consul" && "$SERVICE" != "redis" ]]; then
        # Get service health check endpoint
        HEALTH_CHECK=$(curl -s http://localhost:8500/v1/agent/service/"$SERVICE" | jq -r '.Checks[].HTTP')
        if [[ ! -z "$HEALTH_CHECK" ]]; then
            # Notify service to update cache config
            curl -X POST "$HEALTH_CHECK/cache/refresh" || true
        fi
    fi
done
