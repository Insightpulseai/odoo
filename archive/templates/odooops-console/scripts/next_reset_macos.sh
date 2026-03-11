#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-$(pwd)}"

cd "$APP_DIR"

echo "==> Reset Next.js caches (macOS-safe) in: $APP_DIR"

# 1) Kill anything serving common dev ports (adjust if you use 3001)
for p in 3000 3001; do
  if lsof -tiTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "==> Killing processes on port $p"
    lsof -tiTCP:"$p" -sTCP:LISTEN | xargs -r kill -TERM || true
    sleep 1
    lsof -tiTCP:"$p" -sTCP:LISTEN | xargs -r kill -KILL || true
  fi
done

# 2) Show ownership + flags (helps debug)
if [ -d ".next" ]; then
  echo "==> Inspecting .next flags/ownership"
  ls -laO .next | head -n 50 || true
fi

# 3) Remove immutable flags (common reason for 'Operation not permitted')
if [ -d ".next" ]; then
  echo "==> Clearing macOS flags on .next (requires sudo if not owned)"
  if [ -w ".next" ]; then
    chflags -R nouchg,noschg .next || true
  else
    # Try with sudo if current user can't write, but this script is likely run as user
    # If this fails, user needs to run manually.
    # Attempting best-effort non-sudo first to avoid prompt if not needed.
    echo "Wait, checking write permission..."
  fi
  # Attempt chflags anyway (might work if owner matches)
  chflags -R nouchg,noschg .next || echo "!! Failed to chflags. If this persists, run 'sudo chflags -R nouchg,noschg .next'"
fi

# 4) Fix ownership + perms (in case .next was created by sudo / different user)
# Skipping aggressive sudo chown/chmod here to avoid password prompts in automated flows,
# unless explicitly needed. Users should own their dev directories.

# 5) Now remove caches
echo "==> Removing caches"
rm -rf .next .turbo node_modules/.cache || true

echo "==> Done. Reinstall + restart dev server."
