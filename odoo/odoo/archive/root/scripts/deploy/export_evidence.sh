#!/bin/bash
set -e

ENV=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="docs/ops/evidence/$ENV/$TIMESTAMP"

if [[ -z "$ENV" ]]; then
  echo "Usage: ./export_evidence.sh <env>"
  exit 1
fi

mkdir -p $OUTPUT_DIR

echo "📄 Exporting evidence for $ENV..."

# 1. Module Status
docker compose -f docker/compose/$ENV.yml exec odoo-$ENV odoo shell --shell-interface=python --stop-after-init <<EOF > $OUTPUT_DIR/module_status.txt
from odoo import api, SUPERUSER_ID
env = api.Environment(env.cr, SUPERUSER_ID, {})
modules = env['ir.module.module'].search([('state', 'in', ['installed', 'to upgrade', 'to install'])])
for m in modules:
    print(f"{m.name}: {m.state}")
EOF

# 2. Healthcheck Result
curl -s http://localhost:8069/web/health > $OUTPUT_DIR/healthcheck.txt || echo "Healthcheck failed" > $OUTPUT_DIR/healthcheck.txt

# 3. Build Metadata
echo "SHA: ${GITHUB_SHA:-local}" > $OUTPUT_DIR/metadata.json
echo "DEPLOYED_AT: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $OUTPUT_DIR/metadata.json

echo "✅ Evidence exported to $OUTPUT_DIR"
