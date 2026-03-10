#!/usr/bin/env bash
set -euo pipefail

: "${DESIGN_SYSTEM_URL:=https://raw.githubusercontent.com/Insightpulseai-net/.github/main/templates/odoo-fluent/AGENT_PROMPT.md}"
: "${OUT:=docs/design-system/ODOO_FLUENT_DESIGN_SYSTEM.md}"

mkdir -p "$(dirname "$OUT")"

tmp="$(mktemp)"
curl -sfL "$DESIGN_SYSTEM_URL" -o "$tmp"

# Verify expected content
if ! head -5 "$tmp" | grep -q "CLAUDE.md — Odoo CE E-Commerce (Fluent Design System)"; then
  echo "WARN: fetched content does not match expected heading; still writing."
fi

cat > "$OUT" <<EOF
<!--
SSOT: Odoo-Fluent Design System
Source: $DESIGN_SYSTEM_URL
Policy: Do not edit downstream copies; update upstream template then re-sync.
-->
EOF
cat "$tmp" >> "$OUT"
rm -f "$tmp"

echo "OK: synced -> $OUT"
