#!/bin/bash
# =============================================================================
# TLS Certificate Setup Script
# =============================================================================
# Usage: ./scripts/setup-tls.sh [letsencrypt|selfsigned]
#
# Options:
#   letsencrypt  - Obtain certificate via Let's Encrypt (requires public DNS)
#   selfsigned   - Generate self-signed certificate (for development/testing)
# =============================================================================

set -euo pipefail

DOMAIN="${DOMAIN:-erp.insightpulseai.net}"
CERT_DIR="./nginx/certs"
MODE="${1:-selfsigned}"

mkdir -p "$CERT_DIR"

case "$MODE" in
    letsencrypt)
        echo "=== Let's Encrypt Certificate ==="
        echo "Domain: $DOMAIN"
        echo ""

        # Check if certbot is installed
        if ! command -v certbot &> /dev/null; then
            echo "Installing certbot..."
            if [[ "$OSTYPE" == "darwin"* ]]; then
                brew install certbot
            else
                sudo apt-get update && sudo apt-get install -y certbot
            fi
        fi

        # Stop nginx temporarily for standalone mode
        docker compose stop nginx 2>/dev/null || true

        # Obtain certificate
        sudo certbot certonly \
            --standalone \
            --non-interactive \
            --agree-tos \
            --email "admin@insightpulseai.net" \
            -d "$DOMAIN"

        # Copy certificates to nginx/certs
        sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/"
        sudo chown "$USER:$USER" "$CERT_DIR"/*.pem
        chmod 600 "$CERT_DIR/privkey.pem"

        echo ""
        echo "✓ Let's Encrypt certificate installed"
        echo ""
        echo "To auto-renew, add to crontab:"
        echo "0 0 1 * * certbot renew --quiet && docker compose restart nginx"
        ;;

    selfsigned)
        echo "=== Self-Signed Certificate (Development) ==="
        echo "Domain: $DOMAIN"
        echo ""

        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$CERT_DIR/privkey.pem" \
            -out "$CERT_DIR/fullchain.pem" \
            -subj "/CN=$DOMAIN" \
            -addext "subjectAltName=DNS:$DOMAIN,DNS:localhost"

        chmod 600 "$CERT_DIR/privkey.pem"

        echo ""
        echo "✓ Self-signed certificate created"
        echo ""
        echo "WARNING: Self-signed certificates will show browser warnings."
        echo "For production, use: ./scripts/setup-tls.sh letsencrypt"
        ;;

    *)
        echo "Usage: $0 [letsencrypt|selfsigned]"
        exit 1
        ;;
esac

echo ""
echo "Certificate location: $CERT_DIR"
ls -la "$CERT_DIR"
