#!/bin/bash
# Odoo SSH Tunnel Startup Script
# Creates reliable SSH tunnel to bypass Colima port forwarding issues

set -euo pipefail

PROFILE="odoo"
CONTAINER_NAME="odoo-core"
LOCAL_PORT=8069
LONGPOLL_PORT=8072

echo "🚀 Starting Odoo tunnel..."

# Get current container IP
DOCKER_HOST="unix:///Users/tbwa/.colima/${PROFILE}/docker.sock"
CONTAINER_IP=$(docker inspect "${CONTAINER_NAME}" --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "")

if [ -z "$CONTAINER_IP" ]; then
    echo "❌ Container ${CONTAINER_NAME} not found or not running"
    echo "💡 Start Odoo first: docker compose up -d"
    exit 1
fi

echo "📍 Container IP: ${CONTAINER_IP}"

# Kill existing tunnels
pkill -f "ssh.*${LOCAL_PORT}" 2>/dev/null || true
sleep 1

# Get Colima SSH port
SSH_PORT=$(lsof -ti:57180 -sTCP:LISTEN 2>/dev/null | head -1 || echo "57180")

# Create SSH tunnel
ssh -F /dev/null \
    -o IdentityFile="/Users/tbwa/.colima/_lima/_config/user" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o NoHostAuthenticationForLocalhost=yes \
    -o GSSAPIAuthentication=no \
    -o PreferredAuthentications=publickey \
    -o Compression=no \
    -o BatchMode=yes \
    -o IdentitiesOnly=yes \
    -o User=tbwa \
    -L "${LOCAL_PORT}:${CONTAINER_IP}:8069" \
    -L "${LONGPOLL_PORT}:${CONTAINER_IP}:8072" \
    -N -f \
    -p "${SSH_PORT}" \
    127.0.0.1

if [ $? -eq 0 ]; then
    echo "✅ Tunnel created successfully!"
    echo ""
    echo "🌐 Access Odoo at: http://localhost:${LOCAL_PORT}"
    echo "📡 Longpolling at: http://localhost:${LONGPOLL_PORT}"
    echo ""
    echo "⏹️  To stop: pkill -f 'ssh.*${LOCAL_PORT}'"
else
    echo "❌ Failed to create tunnel"
    exit 1
fi
