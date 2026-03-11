#!/bin/bash
# Start the ops stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting ipai-ops-stack..."

cd "$PROJECT_DIR/docker"

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy .env.example to .env and configure."
    exit 1
fi

# Start services
docker compose up -d

echo ""
echo "Stack started. Checking health..."
sleep 10

"$SCRIPT_DIR/healthcheck.sh"
