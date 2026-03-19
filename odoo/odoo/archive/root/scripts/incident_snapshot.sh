#!/usr/bin/env bash
###############################################################################
# incident_snapshot.sh - Capture comprehensive Odoo incident evidence
#
# Purpose: Auto-collect all diagnostic data when an error occurs
# Usage: bash scripts/incident_snapshot.sh
# Output: docs/incidents/<timestamp_utc>/
#
# What it captures:
# - Docker container status (ps)
# - Odoo container logs (last 2000 lines)
# - nginx container logs (last 2000 lines)
# - Odoo logfile from /var/lib/odoo/odoo.log (last 2000 lines)
# - Odoo configuration (with db_password redacted)
# - Docker mounts configuration (JSON)
#
# Run this immediately after an error occurs for post-mortem analysis.
###############################################################################

set -euo pipefail

# Configuration
REMOTE_HOST="178.128.112.214"
REMOTE_USER="root"
ODOO_CONTAINER="odoo-prod"
NGINX_CONTAINER="nginx-prod-v2"

# Generate timestamp (UTC)
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="/Users/tbwa/Documents/GitHub/odoo-ce/docs/incidents/$TS"

# Ensure output directory exists
mkdir -p "$OUT"

echo "🔍 Capturing incident snapshot at $TS..."

# 1. Docker container status
echo "== docker ps ==" > "$OUT/docker_ps.txt"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker ps" >> "$OUT/docker_ps.txt" 2>&1 || true

# 2. Odoo container logs (last 2000 lines)
echo "== odoo logs ==" > "$OUT/odoo_docker_logs.txt"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker logs --tail=2000 ${ODOO_CONTAINER}" >> "$OUT/odoo_docker_logs.txt" 2>&1 || true

# 3. nginx container logs (last 2000 lines)
echo "== nginx logs ==" > "$OUT/nginx_docker_logs.txt"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker logs --tail=2000 ${NGINX_CONTAINER}" >> "$OUT/nginx_docker_logs.txt" 2>&1 || true

# 4. Odoo logfile from /var/lib/odoo/odoo.log (last 2000 lines)
echo "== odoo logfile ==" > "$OUT/odoo_logfile_tail.txt"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker exec ${ODOO_CONTAINER} bash -lc 'tail -n 2000 /var/lib/odoo/odoo.log'" >> "$OUT/odoo_logfile_tail.txt" 2>&1 || true

# 5. Odoo configuration (with db_password redacted)
echo "== config ==" > "$OUT/odoo_conf.txt"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker exec ${ODOO_CONTAINER} bash -lc 'sed -E \"s/(db_password\s*=\s*).+/\1<REDACTED>/\" /etc/odoo/odoo.conf'" >> "$OUT/odoo_conf.txt" 2>&1 || true

# 6. Docker mounts configuration (JSON)
echo "== mounts ==" > "$OUT/mounts.json"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker inspect ${ODOO_CONTAINER} --format '{{json .Mounts}}'" > "$OUT/mounts.json" 2>&1 || true

# 7. Create metadata file
cat > "$OUT/metadata.json" <<EOF
{
  "timestamp_utc": "$TS",
  "host": "${REMOTE_HOST}",
  "odoo_container": "${ODOO_CONTAINER}",
  "nginx_container": "${NGINX_CONTAINER}",
  "captured_by": "incident_snapshot.sh",
  "files": [
    "docker_ps.txt",
    "odoo_docker_logs.txt",
    "nginx_docker_logs.txt",
    "odoo_logfile_tail.txt",
    "odoo_conf.txt",
    "mounts.json",
    "metadata.json"
  ]
}
EOF

echo "✅ Wrote incident snapshot: $OUT"
echo ""
echo "Files captured:"
ls -lh "$OUT"
echo ""
echo "Next steps:"
echo "1. Review logs in $OUT for error signatures"
echo "2. Create Error Envelope JSON (see docs/TROUBLESHOOTING.md)"
echo "3. Apply minimal fix"
echo "4. Commit incident docs + fix patch"
