#!/usr/bin/env bash
# ============================================================================
# Codespaces Stop Script
# ============================================================================
# Description: Gracefully stops development services
# Usage: ./scripts/codespaces/stop.sh
# ============================================================================

set -euo pipefail

echo "[codespaces] Stopping development services..."

# ============================================================================
# Docker Compose Services
# ============================================================================

DEV_COMPOSE_FILE="${DEV_COMPOSE_FILE:-docker-compose.yml}"
DEV_COMPOSE_PROJECT="${DEV_COMPOSE_PROJECT:-odoo-dev}"

if [ -f "$DEV_COMPOSE_FILE" ]; then
  echo "[codespaces] Stopping Docker Compose stack..."
  docker compose -p "$DEV_COMPOSE_PROJECT" -f "$DEV_COMPOSE_FILE" down
fi

# ============================================================================
# Supabase Local
# ============================================================================

if command -v supabase >/dev/null 2>&1 && [ -f "supabase/config.toml" ]; then
  echo "[codespaces] Stopping Supabase local..."
  supabase stop || true
fi

echo "[codespaces] All services stopped."
