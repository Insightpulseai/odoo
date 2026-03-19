#!/usr/bin/env bash
# ============================================================================
# Codespaces Start Script
# ============================================================================
# Description: Starts development services on container start
# Usage: Called automatically by postStartCommand in devcontainer.json
# ============================================================================

set -euo pipefail

echo "[codespaces] Starting development services..."

# ============================================================================
# Docker Compose Services
# ============================================================================

DEV_COMPOSE_FILE="${DEV_COMPOSE_FILE:-docker-compose.yml}"
DEV_COMPOSE_PROJECT="${DEV_COMPOSE_PROJECT:-odoo-dev}"

if [ -f "$DEV_COMPOSE_FILE" ]; then
  echo "[codespaces] Starting Docker Compose stack..."
  docker compose -p "$DEV_COMPOSE_PROJECT" -f "$DEV_COMPOSE_FILE" up -d

  # Wait for services to be ready
  echo "[codespaces] Waiting for services..."
  sleep 10

  # Health checks
  echo "[codespaces] Running health checks..."

  # Odoo health check
  if curl -fsS "http://127.0.0.1:8069/web/health" >/dev/null 2>&1; then
    echo "[codespaces] ✓ Odoo is healthy (port 8069)"
  else
    echo "[codespaces] ⚠ Odoo not responding yet (may still be starting)"
  fi

  # PostgreSQL health check
  if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
    echo "[codespaces] ✓ PostgreSQL is healthy (port 5432)"
  else
    echo "[codespaces] ⚠ PostgreSQL not responding"
  fi

  # Show running containers
  echo ""
  echo "[codespaces] Running containers:"
  docker compose -p "$DEV_COMPOSE_PROJECT" -f "$DEV_COMPOSE_FILE" ps
else
  echo "[codespaces] No compose file found, skipping Docker services"
fi

# ============================================================================
# Supabase Local (optional)
# ============================================================================

if command -v supabase >/dev/null 2>&1 && [ -f "supabase/config.toml" ]; then
  echo ""
  echo "[codespaces] Starting Supabase local development..."
  supabase start || echo "[codespaces] Supabase start skipped (may already be running or not configured)"
fi

echo ""
echo "[codespaces] Development environment ready!"
