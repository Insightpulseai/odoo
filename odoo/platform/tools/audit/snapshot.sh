#!/usr/bin/env bash
# Environment Snapshot Script
# Collects environment state for audit verification.
# Every audit must include this snapshot output as evidence.
#
# Usage: ./tools/audit/snapshot.sh [output_dir]
#   output_dir: Directory to write snapshot files (default: audit/)

set -euo pipefail

OUTPUT_DIR="${1:-audit}"
mkdir -p "$OUTPUT_DIR"
SNAPSHOT_FILE="$OUTPUT_DIR/snapshot.txt"
SNAPSHOT_JSON="$OUTPUT_DIR/snapshot.json"

# Generate text snapshot
{
    echo "=== AUDIT SNAPSHOT ==="
    echo "Generated at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""

    echo "=== GIT STATE ==="
    echo "Remote:"
    git remote -v 2>/dev/null || echo "  (not a git repository)"
    echo ""
    echo "Branch:"
    git branch --show-current 2>/dev/null || echo "  (detached or not a repo)"
    echo ""
    echo "Commit SHA:"
    git rev-parse HEAD 2>/dev/null || echo "  (not available)"
    echo ""
    echo "Status (dirty check):"
    git status --porcelain 2>/dev/null || echo "  (not available)"
    echo ""

    echo "=== SUBMODULES ==="
    git submodule status --recursive 2>/dev/null || echo "  (no submodules or not a repo)"
    echo ""

    echo "=== PYTHON/ODOO VERSION ==="
    echo "Python:"
    python3 -V 2>/dev/null || echo "  (python3 not found)"
    echo ""
    echo "Odoo version:"
    python3 -c "import odoo; print('  ', odoo.release.version)" 2>/dev/null || echo "  (odoo not importable)"
    echo ""

    echo "=== ENVIRONMENT VARIABLES ==="
    echo "ODOO_ADDONS_PATH=${ODOO_ADDONS_PATH:-<not set>}"
    echo "ODOO_RC=${ODOO_RC:-<not set>}"
    echo "ODOO_DATA_DIR=${ODOO_DATA_DIR:-<not set>}"
    echo "PGHOST=${PGHOST:-<not set>}"
    echo "PGDATABASE=${PGDATABASE:-<not set>}"
    echo ""

    echo "=== ODOO CONFIG ==="
    if [[ -n "${ODOO_RC:-}" ]] && [[ -f "${ODOO_RC}" ]]; then
        echo "Config file: ${ODOO_RC}"
        echo "--- First 50 lines (sensitive values masked) ---"
        head -n 50 "${ODOO_RC}" 2>/dev/null | sed -E 's/(password|secret|key|token)\s*=\s*.*/\1 = ***MASKED***/gi' || echo "  (could not read)"
    elif [[ -f "/etc/odoo/odoo.conf" ]]; then
        echo "Config file: /etc/odoo/odoo.conf (default location)"
        head -n 50 "/etc/odoo/odoo.conf" 2>/dev/null | sed -E 's/(password|secret|key|token)\s*=\s*.*/\1 = ***MASKED***/gi' || echo "  (could not read)"
    else
        echo "  (no config file found)"
    fi
    echo ""

    echo "=== ADDONS PATH RESOLUTION ==="
    # Try to determine actual addons path
    if [[ -d "addons" ]]; then
        echo "Local addons/ directory:"
        ls -la addons/ 2>/dev/null | head -20 || echo "  (could not list)"
        echo ""
        echo "IPAI modules:"
        find addons -maxdepth 1 -type d -name "ipai_*" 2>/dev/null | sort || echo "  (no ipai modules found)"
    fi
    if [[ -d "addons/oca" ]]; then
        echo ""
        echo "OCA modules (addons/oca):"
        ls -la addons/oca/ 2>/dev/null | head -20 || echo "  (could not list)"
    fi
    echo ""

    echo "=== DOCKER STATUS ==="
    if command -v docker &>/dev/null; then
        echo "Docker containers:"
        docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "  (docker not accessible)"
        echo ""
        echo "Docker images (odoo-related):"
        docker images 2>/dev/null | grep -i odoo || echo "  (no odoo images found)"
    else
        echo "  (docker not installed)"
    fi
    echo ""

    echo "=== SYSTEM INFO ==="
    echo "Hostname: $(hostname 2>/dev/null || echo 'unknown')"
    echo "OS: $(uname -a 2>/dev/null || echo 'unknown')"
    echo "Memory: $(free -h 2>/dev/null | grep Mem || echo 'unknown')"
    echo "Disk: $(df -h . 2>/dev/null | tail -1 || echo 'unknown')"
    echo ""

    echo "=== END SNAPSHOT ==="
} > "$SNAPSHOT_FILE"

# Generate JSON snapshot
cat > "$SNAPSHOT_JSON" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git": {
    "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'N/A')",
    "branch": "$(git branch --show-current 2>/dev/null || echo 'N/A')",
    "dirty": $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  },
  "python_version": "$(python3 -V 2>/dev/null | cut -d' ' -f2 || echo 'N/A')",
  "ipai_modules": $(find addons -maxdepth 1 -type d -name "ipai_*" 2>/dev/null | sort | sed 's/addons\//"/g' | sed 's/$/"/' | tr '\n' ',' | sed 's/,$//' | sed 's/^/[/' | sed 's/$/]/' || echo '[]')
}
EOF

echo "Snapshot written to: $SNAPSHOT_FILE"
echo "JSON snapshot written to: $SNAPSHOT_JSON"
