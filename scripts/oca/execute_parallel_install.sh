#!/usr/bin/env bash
# =============================================================================
# OCA Parallel Installation Executor
# =============================================================================
# Run this locally to execute the parallel OCA installation.
# Expected time: 30-45 minutes
#
# Usage:
#   ./scripts/oca/execute_parallel_install.sh
# =============================================================================

set -euo pipefail

echo "═══════════════════════════════════════════════════════════"
echo "  OCA Parallel Installation - Execution Wrapper"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Step 1: Verify Docker is running
echo "Step 1/5: Verifying Docker environment..."
if ! docker compose ps &>/dev/null; then
  echo "❌ Docker Compose not accessible. Start Docker first:"
  echo "   docker compose up -d"
  exit 1
fi
echo "✅ Docker environment OK"
echo ""

# Step 2: Backup database
echo "Step 2/5: Backing up database..."
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/pre_oca_install_$(date +%Y%m%d_%H%M).dump"

docker compose exec -T db pg_dump -U odoo odoo > "$BACKUP_FILE"

if [[ -f "$BACKUP_FILE" ]]; then
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup created: $BACKUP_FILE ($BACKUP_SIZE)"
else
  echo "❌ Backup failed"
  exit 1
fi
echo ""

# Step 3: Verify Odoo is running
echo "Step 3/5: Verifying Odoo server..."
if ! curl -fsS http://localhost:8069/web/database/selector &>/dev/null; then
  echo "⚠️  Odoo not responding. Starting services..."
  docker compose up -d
  echo "Waiting 30 seconds for Odoo to start..."
  sleep 30
fi

if curl -fsS http://localhost:8069/web/database/selector &>/dev/null; then
  echo "✅ Odoo server responding"
else
  echo "❌ Odoo server not accessible"
  exit 1
fi
echo ""

# Step 4a: Install base CE 19 core modules
echo "Step 4a/6: Installing base Odoo CE 19 core modules..."
echo ""

BASE_MODULES="sale,sale_management,purchase,stock,mrp,account,account_accountant,crm,project,hr,hr_attendance,hr_holidays,website,website_sale,point_of_sale,calendar,contacts,fleet,lunch,maintenance,mass_mailing,note,survey,helpdesk"

docker compose exec odoo odoo-bin \
  -d odoo_dev \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/ipai,/mnt/extra-addons/third_party/oca/* \
  -i "$BASE_MODULES" \
  --stop-after-init \
  --log-level=info \
  --without-demo=all

echo "✅ Base CE modules installed"
echo ""

# Step 4b: Execute parallel OCA installation
echo "Step 4b/6: Executing parallel OCA installation..."
echo "This will take 30-45 minutes. Log file: logs/oca_install/install_$(date +%Y%m%d_%H%M%S).log"
echo ""

docker compose exec odoo bash -c "cd /mnt/workspace && ./scripts/oca/install_oca_parallel.sh --docker-exec 'docker compose exec -T odoo'"

echo ""
echo "✅ Installation complete"
echo ""

# Step 5: Validation
echo "Step 5/5: Validating installation..."
docker compose exec odoo python3 /mnt/workspace/scripts/oca/validate_installation.py \
  --db odoo_dev \
  --url http://localhost:8069 \
  --output /mnt/workspace/docs/evidence/$(date +%Y%m%d-%H%M)/oca_validation.json

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Installation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review validation results in docs/evidence/"
echo "  2. Generate EE parity report: python scripts/test_ee_parity.py"
echo "  3. Commit changes: git add -A && git commit -m 'feat(oca): parallel installation complete'"
echo ""
