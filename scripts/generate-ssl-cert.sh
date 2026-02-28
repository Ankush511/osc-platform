#!/bin/bash
# Generate self-signed SSL certificate for development/testing
# For production, use Let's Encrypt or a proper CA

set -e

SSL_DIR="nginx/ssl"
DOMAIN="${DOMAIN:-localhost}"
DAYS="${DAYS:-365}"

echo "Generating self-signed SSL certificate..."
echo "Domain: ${DOMAIN}"
echo "Valid for: ${DAYS} days"

# Create SSL directory if it doesn't exist
mkdir -p "${SSL_DIR}"

# Generate private key and certificate
openssl req -x509 -nodes -days ${DAYS} -newkey rsa:2048 \
    -keyout "${SSL_DIR}/key.pem" \
    -out "${SSL_DIR}/cert.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"

# Set proper permissions
chmod 600 "${SSL_DIR}/key.pem"
chmod 644 "${SSL_DIR}/cert.pem"

echo ""
echo "SSL certificate generated successfully!"
echo "Certificate: ${SSL_DIR}/cert.pem"
echo "Private key: ${SSL_DIR}/key.pem"
echo ""
echo "WARNING: This is a self-signed certificate for development only."
echo "For production, use Let's Encrypt:"
echo "  certbot certonly --webroot -w /var/www/certbot -d yourdomain.com"
