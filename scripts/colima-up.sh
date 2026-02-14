#!/usr/bin/env bash
set -euo pipefail

# Colima startup script - deterministic Docker daemon for Odoo development
# Part of enterprise Docker/DevContainer standards

PROFILE="odoo"
PROFILE_PATH=".colima/${PROFILE}.yaml"

echo "🚀 Starting Colima with profile: ${PROFILE}"

# Check if profile exists
if [[ ! -f "${PROFILE_PATH}" ]]; then
  echo "❌ Profile not found: ${PROFILE_PATH}"
  echo "Expected profile at project root"
  exit 1
fi

# Check if Colima is already running with this profile
if colima status -p "${PROFILE}" &>/dev/null; then
  echo "✅ Colima '${PROFILE}' already running"
  colima status -p "${PROFILE}"
else
  echo "📦 Starting Colima with profile: ${PROFILE_PATH}"
  colima start -p "${PROFILE}" --edit=false "${PROFILE_PATH}"

  # Verify startup
  if colima status -p "${PROFILE}" &>/dev/null; then
    echo "✅ Colima '${PROFILE}' started successfully"
    colima status -p "${PROFILE}"
  else
    echo "❌ Colima failed to start"
    exit 1
  fi
fi

# Verify Docker connection
echo ""
echo "🔍 Verifying Docker connection..."
if docker info &>/dev/null; then
  echo "✅ Docker daemon connected"
  docker version --format 'Docker: {{.Server.Version}} (Colima runtime)'
else
  echo "❌ Docker daemon not accessible"
  echo "Run: colima status -p ${PROFILE}"
  exit 1
fi

# Show Docker Compose project status
echo ""
echo "📊 Docker Compose status:"
if docker compose ps --format table 2>/dev/null | grep -q "ipai"; then
  docker compose ps --format table
else
  echo "ℹ️  No services running (use 'make up' or 'docker compose up')"
fi

echo ""
echo "✨ Ready for development!"
echo "   - Colima profile: ${PROFILE}"
echo "   - Docker context: colima-${PROFILE}"
echo "   - VM resources: $(colima list -p "${PROFILE}" 2>/dev/null | tail -1 | awk '{print $3" CPU, "$4" RAM, "$5" disk"}' || echo "4 CPU, 8GiB RAM, 60GiB disk")"
