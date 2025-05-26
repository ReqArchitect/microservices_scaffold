# Generate Consul encryption keys and tokens
$gossipKey = & consul keygen
$httpToken = [System.Guid]::NewGuid().ToString()

# Create .env file
@"
CONSUL_GOSSIP_ENCRYPTION_KEY=$gossipKey
CONSUL_HTTP_TOKEN=$httpToken
"@ | Set-Content -Path "../.env"

Write-Host "Generated Consul encryption key and tokens. Saved to .env file.
Please make sure to securely store these credentials and distribute them to services that need them."
