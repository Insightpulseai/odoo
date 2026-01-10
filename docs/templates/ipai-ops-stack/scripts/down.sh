#!/bin/bash
# Stop the ops stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Stopping ipai-ops-stack..."

cd "$PROJECT_DIR/docker"
docker compose down

echo "Stack stopped."
