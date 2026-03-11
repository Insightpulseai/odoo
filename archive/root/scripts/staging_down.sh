#!/usr/bin/env bash
set -e

echo "Stopping Staging Environment..."
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"
cd sandbox/dev

docker compose stop odoo-stage

echo "Staging stopped."
