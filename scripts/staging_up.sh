#!/usr/bin/env bash
set -e

# Start the staging stack
echo "Starting Staging Environment..."
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"
cd sandbox/dev

# Start only the staging service (and db if not running)
docker compose up -d odoo-stage

echo "Waiting for Staging to be ready..."
sleep 5
docker compose logs --tail=20 odoo-stage

echo "Staging is running at http://localhost:9079"
