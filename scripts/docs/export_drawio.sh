#!/usr/bin/env bash
set -euo pipefail
# export_drawio.sh — Render .drawio files to .png deterministically.
#
# Usage:
#   ./scripts/docs/export_drawio.sh                          # all diagrams
#   ./scripts/docs/export_drawio.sh path/to/diagram.drawio   # single diagram
#
# Supports:
#   - macOS: draw.io desktop app (/Applications/draw.io.app)
#   - Linux/CI: draw.io CLI via xvfb-run (apt install drawio xvfb)
#   - Any: drawio CLI on PATH (npm install -g draw.io-export or brew install --cask drawio)
#
# Install (local):
#   brew install --cask drawio
#
# Install (CI / Linux):
#   sudo apt-get update && sudo apt-get install -y xvfb
#   curl -fsSL https://github.com/jgraph/drawio-desktop/releases/download/v24.7.17/drawio-amd64-24.7.17.deb -o /tmp/drawio.deb
#   sudo dpkg -i /tmp/drawio.deb || sudo apt-get install -f -y

REPO_ROOT="$(git rev-parse --show-toplevel)"
DIAGRAM_DIR="${REPO_ROOT}/docs/architecture/diagrams"

# Locate draw.io binary — try in order: PATH, macOS app, xvfb-wrapped
resolve_drawio() {
  if command -v drawio &>/dev/null; then
    echo "drawio"
  elif [ -f "/Applications/draw.io.app/Contents/MacOS/draw.io" ]; then
    echo "/Applications/draw.io.app/Contents/MacOS/draw.io"
  elif command -v xvfb-run &>/dev/null; then
    # Linux CI: find drawio binary and wrap with xvfb
    local drawio_path
    drawio_path=$(command -v drawio 2>/dev/null || echo "/usr/bin/drawio")
    if [ -f "$drawio_path" ]; then
      echo "xvfb-run -a $drawio_path"
    else
      echo ""
    fi
  else
    echo ""
  fi
}

DRAWIO_BIN=$(resolve_drawio)

if [ -z "$DRAWIO_BIN" ]; then
  echo "ERROR: draw.io CLI not found."
  echo ""
  echo "Install options:"
  echo "  macOS:  brew install --cask drawio"
  echo "  Linux:  sudo apt-get install drawio xvfb"
  echo "  CI:     see comments in this script"
  exit 1
fi

echo "Using: ${DRAWIO_BIN}"

export_one() {
  local src="$1"
  local dst="${src%.drawio}.png"
  echo "Exporting: ${src} → ${dst}"
  $DRAWIO_BIN --export --format png --scale 2 --border 20 --output "$dst" "$src"
}

if [ $# -ge 1 ]; then
  # Single file mode
  if [ ! -f "$1" ]; then
    echo "ERROR: File not found: $1"
    exit 1
  fi
  export_one "$1"
else
  # All diagrams mode
  found=0
  for drawio_file in "${DIAGRAM_DIR}"/*.drawio; do
    [ -f "$drawio_file" ] || continue
    export_one "$drawio_file"
    found=$((found + 1))
  done
  if [ "$found" -eq 0 ]; then
    echo "No .drawio files found in ${DIAGRAM_DIR}"
    exit 0
  fi
  echo "Exported ${found} diagram(s)."
fi
