#!/bin/bash
# Generate self-signed certificates for mTLS in the service mesh

# Create output directory
mkdir -p ./service_mesh/certs

# Create CA key and certificate
openssl genrsa -out ./service_mesh/certs/ca.key 4096
openssl req -new -x509 -key ./service_mesh/certs/ca.key -sha256 -subj "/CN=flask-microservices-ca" -out ./service_mesh/certs/ca.crt -days 365

# Function to create certificate for a service
create_service_cert() {
    SERVICE_NAME=$1
    
    echo "Generating certificate for $SERVICE_NAME"
    
    # Create private key
    openssl genrsa -out ./service_mesh/certs/${SERVICE_NAME}.key 2048
    
    # Create CSR (Certificate Signing Request)
    openssl req -new -key ./service_mesh/certs/${SERVICE_NAME}.key \
        -out ./service_mesh/certs/${SERVICE_NAME}.csr \
        -subj "/CN=${SERVICE_NAME}" \
        -config <(cat <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[dn]
CN = ${SERVICE_NAME}

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${SERVICE_NAME}
DNS.2 = ${SERVICE_NAME}-service
DNS.3 = ${SERVICE_NAME}-service.reqarchitect
DNS.4 = ${SERVICE_NAME}-service.reqarchitect.svc.cluster.local
EOF
        )
        
    # Sign the certificate with our CA
    openssl x509 -req -in ./service_mesh/certs/${SERVICE_NAME}.csr \
        -CA ./service_mesh/certs/ca.crt \
        -CAkey ./service_mesh/certs/ca.key \
        -CAcreateserial \
        -out ./service_mesh/certs/${SERVICE_NAME}.crt \
        -days 365 \
        -extensions req_ext \
        -extfile <(cat <<EOF
[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${SERVICE_NAME}
DNS.2 = ${SERVICE_NAME}-service
DNS.3 = ${SERVICE_NAME}-service.reqarchitect
DNS.4 = ${SERVICE_NAME}-service.reqarchitect.svc.cluster.local
EOF
        )
        
    # Create a combined PEM file (some tools prefer this format)
    cat ./service_mesh/certs/${SERVICE_NAME}.key ./service_mesh/certs/${SERVICE_NAME}.crt > ./service_mesh/certs/${SERVICE_NAME}.pem
    
    # Cleanup the CSR as it's no longer needed
    rm ./service_mesh/certs/${SERVICE_NAME}.csr
}

# Generate certificates for each service
create_service_cert "strategy"
create_service_cert "business-layer"
create_service_cert "user"
create_service_cert "kpi"
create_service_cert "initiative"
create_service_cert "envoy"

echo "Certificate generation complete. Certificates stored in ./service_mesh/certs/"
