#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
echo "Fixing permissions under: $ROOT"

# ensure you own the tree (ignore failures where sudo isn't allowed)
( sudo chown -R "$(id -un)":"$(id -gn)" "$ROOT" ) 2>/dev/null || true

# remove macOS quarantine bit (common when zips downloaded)
xattr -dr com.apple.quarantine "$ROOT" 2>/dev/null || true

# clear immutable flags if any (rare but fatal)
chflags -R nouchg,noschg "$ROOT" 2>/dev/null || true

# add user rw + execute on dirs
chmod -R u+rwX "$ROOT" 2>/dev/null || true

echo "Done."
