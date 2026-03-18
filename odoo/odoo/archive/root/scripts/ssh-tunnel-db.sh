#!/bin/bash
# SSH Tunnel to DigitalOcean PostgreSQL Cluster
# Maps remote PostgreSQL port 25060 to local port 5433
# Usage: ./scripts/ssh-tunnel-db.sh

set -e

DROPLET_IP="178.128.112.214"
DB_HOST="odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
DB_PORT="25060"
LOCAL_PORT="5433"

echo "=== Setting up SSH tunnel to DigitalOcean PostgreSQL ==="
echo "Remote: ${DB_HOST}:${DB_PORT}"
echo "Local: localhost:${LOCAL_PORT}"
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo ""

# Create SSH tunnel
# -L: Local port forwarding
# -N: No remote command
# -f: Background mode (remove -f to keep in foreground)
ssh -L ${LOCAL_PORT}:${DB_HOST}:${DB_PORT} root@${DROPLET_IP} -N

# To run in foreground (recommended for debugging):
# ssh -L ${LOCAL_PORT}:${DB_HOST}:${DB_PORT} root@${DROPLET_IP} -N

# To run in background:
# ssh -f -L ${LOCAL_PORT}:${DB_HOST}:${DB_PORT} root@${DROPLET_IP} -N
# pkill -f "ssh.*${DB_HOST}:${DB_PORT}" # to stop
