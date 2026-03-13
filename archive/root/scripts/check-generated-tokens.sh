#!/usr/bin/env bash
# ============================================================================
# Generated Tokens Determinism Check
#
# Ensures that token generation is deterministic by:
# 1. Running the token generation command (if available)
# 2. Checking for uncommitted changes in generated files
#
# This prevents drift between generated and committed token files.
# ============================================================================
set -euo pipefail

die() {
  echo "[tokens-check] FAIL: $*" >&2
  exit 1
}

# Check if package.json exists (Node.js project)
if [ ! -f package.json ]; then
  echo "[tokens-check] No package.json found; skipping token generation check"
  exit 0
fi

# Check if tokens:gen script exists
if command -v npm &> /dev/null; then
  if npm run 2>/dev/null | grep -q 'tokens:gen'; then
    echo "[tokens-check] Found tokens:gen script, running..."
    npm run tokens:gen || true

    # Check for uncommitted changes
    if ! git diff --quiet; then
      echo "[tokens-check] Generated token outputs are not committed or not deterministic"
      echo "[tokens-check] The following files have uncommitted changes:"
      git diff --name-only
      die "Token generation produced uncommitted changes"
    fi

    echo "[tokens-check] Token outputs are deterministic and committed"
  else
    echo "[tokens-check] No tokens:gen script found in package.json; skipping"
  fi
else
  echo "[tokens-check] npm not available; skipping token generation check"
fi

echo "[tokens-check] OK"
