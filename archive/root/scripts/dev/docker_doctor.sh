#!/usr/bin/env bash
# =============================================================================
# scripts/dev/docker_doctor.sh
#
# Verifies that the Docker daemon is reachable on the requested context.
# Called by .devcontainer/devcontainer.json initializeCommand before build.
#
# Context resolution order (first match wins):
#   1. DOCKER_CONTEXT_OVERRIDE env var  — set by individual devs or CI
#   2. Positional argument $1           — useful in scripts
#   3. Default: "desktop-linux"         — Docker Desktop
#
# Usage:
#   bash scripts/dev/docker_doctor.sh                  # defaults to desktop-linux
#   bash scripts/dev/docker_doctor.sh colima           # Colima default profile
#   DOCKER_CONTEXT_OVERRIDE=colima bash scripts/dev/docker_doctor.sh
#
# Exit codes:
#   0 — daemon reachable, context set
#   1 — context not found or daemon unreachable
# =============================================================================
set -euo pipefail

# Resolve: env override → positional arg → default
WANT="${DOCKER_CONTEXT_OVERRIDE:-${1:-desktop-linux}}"

# Clear any ambient overrides that could shadow the requested context
unset DOCKER_HOST DOCKER_CONTEXT 2>/dev/null || true

# Check context exists
if ! docker context inspect "${WANT}" >/dev/null 2>&1; then
  echo "ERROR: Docker context '${WANT}' not found." >&2
  echo "" >&2
  echo "Available contexts:" >&2
  docker context ls 2>&1 >&2 || true
  echo "" >&2
  echo "For Docker Desktop:  docker context use desktop-linux" >&2
  echo "For Colima:          colima start && docker context use colima" >&2
  echo "" >&2
  echo "To override without editing files:" >&2
  echo "  export DOCKER_CONTEXT_OVERRIDE=colima" >&2
  exit 1
fi

# Switch to requested context
docker context use "${WANT}" >/dev/null

# Verify daemon is reachable (server version non-empty)
SERVER_VER=$(docker version --format '{{.Server.Version}}' 2>/dev/null || true)
if [[ -z "${SERVER_VER}" || "${SERVER_VER}" == "<nil>" ]]; then
  echo "ERROR: Docker daemon not reachable for context '${WANT}'." >&2
  echo "Server: null" >&2
  echo "" >&2
  docker version 2>&1 >&2 || true
  echo "" >&2
  echo "If using Docker Desktop: ensure it is running." >&2
  echo "If using Colima:         colima start [--profile <name>]" >&2
  echo "To try a different context: export DOCKER_CONTEXT_OVERRIDE=<context>" >&2
  exit 1
fi

CLIENT_VER=$(docker version --format '{{.Client.Version}}' 2>/dev/null || true)
echo "OK: Docker daemon reachable via context '${WANT}'"
echo "    Client=${CLIENT_VER}  Server=${SERVER_VER}"
