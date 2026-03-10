#!/bin/bash
# View logs for the ops stack

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR/docker"

# If service name provided, show that service
if [ -n "$1" ]; then
    docker compose logs -f --tail=100 "$1"
else
    docker compose logs -f --tail=100
fi
