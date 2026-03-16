#!/usr/bin/env bash
# =============================================================================
# install-github-runner.sh — Install GitHub Actions self-hosted runner
# =============================================================================
# Idempotent: safe to re-run. Installs runner as systemd service.
#
# Prerequisites:
#   - GITHUB_TOKEN env var with admin:org scope (or repo scope for repo-level)
#   - curl, jq installed on target host
#
# Usage:
#   GITHUB_TOKEN=ghp_... bash scripts/ci/install-github-runner.sh
#   # or via SSH:
#   ssh root@178.128.112.214 "GITHUB_TOKEN=\$GITHUB_TOKEN bash /opt/odoo/repo/scripts/ci/install-github-runner.sh"
# =============================================================================
set -euo pipefail

REPO="Insightpulseai/odoo"
RUNNER_USER="github-runner"
RUNNER_DIR="/opt/actions-runner"
RUNNER_NAME="${RUNNER_NAME:-odoo-prod-runner}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,Linux,X64,odoo-prod}"

# --- Validate prerequisites ---
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "ERROR: GITHUB_TOKEN env var required (repo or admin:org scope)"
  exit 1
fi

command -v curl >/dev/null || { echo "ERROR: curl not found"; exit 1; }
command -v jq >/dev/null || { echo "ERROR: jq not found"; exit 1; }

# --- Check if runner already registered ---
EXISTING=$(curl -sf \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/actions/runners" \
  | jq -r ".runners[] | select(.name == \"${RUNNER_NAME}\") | .status" 2>/dev/null || echo "")

if [ "$EXISTING" = "online" ]; then
  echo "Runner '${RUNNER_NAME}' already registered and online. Nothing to do."
  exit 0
fi

# --- Create runner user ---
if ! id "$RUNNER_USER" &>/dev/null; then
  echo "Creating user: ${RUNNER_USER}"
  useradd -m -s /bin/bash "$RUNNER_USER"
fi

# Add to docker group (required for deploy workflows)
usermod -aG docker "$RUNNER_USER" 2>/dev/null || true

# --- Get registration token ---
echo "Requesting registration token..."
REG_TOKEN=$(curl -sf \
  -X POST \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/actions/runners/registration-token" \
  | jq -r '.token')

if [ -z "$REG_TOKEN" ] || [ "$REG_TOKEN" = "null" ]; then
  echo "ERROR: Failed to get registration token. Check GITHUB_TOKEN permissions."
  exit 1
fi

# --- Download runner ---
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

RUNNER_VERSION=$(curl -sf \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/actions/runner/releases/latest" \
  | jq -r '.tag_name' | sed 's/^v//')

RUNNER_ARCH="linux-x64"
RUNNER_TAR="actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"

if [ ! -f ".runner" ] || [ "$EXISTING" != "online" ]; then
  echo "Downloading runner v${RUNNER_VERSION}..."
  curl -sfL -o "$RUNNER_TAR" \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_TAR}"
  tar xzf "$RUNNER_TAR"
  rm -f "$RUNNER_TAR"
fi

# --- Configure runner ---
echo "Configuring runner: ${RUNNER_NAME} (labels: ${RUNNER_LABELS})"
chown -R "$RUNNER_USER:$RUNNER_USER" "$RUNNER_DIR"

sudo -u "$RUNNER_USER" ./config.sh \
  --url "https://github.com/${REPO}" \
  --token "$REG_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$RUNNER_LABELS" \
  --unattended \
  --replace

# --- Install as systemd service ---
echo "Installing systemd service..."
./svc.sh install "$RUNNER_USER"
./svc.sh start

echo "Enabling auto-start on boot..."
./svc.sh status

# --- Verify ---
echo ""
echo "=== Runner Installation Complete ==="
echo "Name:   ${RUNNER_NAME}"
echo "Labels: ${RUNNER_LABELS}"
echo "Dir:    ${RUNNER_DIR}"
echo "User:   ${RUNNER_USER}"
echo ""
echo "Verify with:"
echo "  gh api repos/${REPO}/actions/runners --jq '.runners[] | \"\\(.name) \\(.status)\"'"
