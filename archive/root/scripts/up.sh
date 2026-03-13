#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../sandbox/dev"
PROFILE="${1:-dev-db}"
docker compose --profile "$PROFILE" up -d "${@:2}"
docker compose ps
