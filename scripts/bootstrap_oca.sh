#!/bin/bash
# File: scripts/bootstrap_oca.sh
# Purpose: Clone OCA repositories and symlink modules for Odoo 19

set -euo pipefail

OCA_BASE_DIR="$(pwd)/addons/oca"
OCA_BRANCH="${OCA_BRANCH:-19.0}"  # Fallback to 18.0 if 19.0 doesn't exist

echo "🚀 Starting OCA bootstrap for Odoo 19..."
echo "📁 Target directory: $OCA_BASE_DIR"
echo "🌿 Target branch: $OCA_BRANCH"

# Create OCA directory
mkdir -p "$OCA_BASE_DIR"

# OCA repositories to clone
declare -A OCA_REPOS=(
  ["account-financial-tools"]="https://github.com/OCA/account-financial-tools.git"
  ["account-financial-reporting"]="https://github.com/OCA/account-financial-reporting.git"
  ["account-invoicing"]="https://github.com/OCA/account-invoicing.git"
  ["account-reconcile"]="https://github.com/OCA/account-reconcile.git"
  ["server-tools"]="https://github.com/OCA/server-tools.git"
  ["web"]="https://github.com/OCA/web.git"
  ["project"]="https://github.com/OCA/project.git"
  ["hr"]="https://github.com/OCA/hr.git"
  ["dms"]="https://github.com/OCA/dms.git"
  ["social"]="https://github.com/OCA/social.git"
)

# Clone repositories
echo ""
echo "📦 Cloning OCA repositories..."
for repo_name in "${!OCA_REPOS[@]}"; do
  repo_url="${OCA_REPOS[$repo_name]}"
  repo_dir="$OCA_BASE_DIR/$repo_name"

  if [ -d "$repo_dir" ]; then
    echo "✅ $repo_name already cloned, pulling latest..."
    (cd "$repo_dir" && git pull --ff-only)
  else
    echo "📦 Cloning $repo_name..."
    if ! git clone --branch "$OCA_BRANCH" --depth 1 "$repo_url" "$repo_dir" 2>/dev/null; then
      echo "⚠️  Branch $OCA_BRANCH not found for $repo_name, trying 18.0..."
      git clone --branch 18.0 --depth 1 "$repo_url" "$repo_dir" || {
        echo "❌ Failed to clone $repo_name (both 19.0 and 18.0 branches)"
        continue
      }
    fi
  fi
done

# Required modules (symlink to flat addons/oca/modules/ structure for Odoo)
declare -a REQUIRED_MODULES=(
  # Account (Financial Tools)
  "account-financial-tools/account_asset_management"
  "account-financial-tools/account_budget"
  "account-financial-tools/account_cost_center"
  "account-financial-tools/account_move_budget"

  # Account (Financial Reporting)
  "account-financial-reporting/account_financial_report"
  "account-financial-reporting/mis_builder"

  # Account (Invoicing)
  "account-invoicing/account_invoice_triple_discount"
  "account-invoicing/sale_order_invoicing_grouping_criteria"

  # Account (Reconciliation)
  "account-reconcile/account_reconcile_oca"
  "account-reconcile/base_bank_account_number_unique"

  # Server Tools
  "server-tools/base_automation"
  "server-tools/base_technical_features"
  "server-tools/database_cleanup"
  "server-tools/base_search_fuzzy"

  # Web
  "web/web_timeline"
  "web/web_widget_x2many_2d_matrix"
  "web/web_advanced_search"
  "web/web_domain_field"

  # Project
  "project/project_task_default_stage"
  "project/project_template"
  "project/project_timesheet_time_control"
  "project/project_status"

  # HR
  "hr/hr_employee_document"
  "hr/hr_employee_service"
  "hr/hr_holidays_public"

  # DMS (Document Management)
  "dms/dms"
  "dms/dms_field"

  # Social (Marketing)
  "social/mass_mailing_event"
  "social/mail_tracking"
)

# Create flat symlink structure
echo ""
echo "🔗 Creating module symlinks..."
mkdir -p "$OCA_BASE_DIR/modules"

LINKED=0
MISSING=0

for module_path in "${REQUIRED_MODULES[@]}"; do
  module_name="$(basename "$module_path")"
  source_path="$OCA_BASE_DIR/$module_path"
  target_path="$OCA_BASE_DIR/modules/$module_name"

  if [ -d "$source_path" ]; then
    ln -sf "$(realpath "$source_path")" "$target_path"
    echo "  ✅ $module_name"
    ((LINKED++))
  else
    echo "  ❌ $module_name (not found in $(dirname "$module_path"))"
    ((MISSING++))
  fi
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ OCA Bootstrap Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Statistics:"
echo "   - Repositories cloned: ${#OCA_REPOS[@]}"
echo "   - Modules linked: $LINKED"
echo "   - Modules missing: $MISSING"
echo ""
echo "📁 Modules available in: $OCA_BASE_DIR/modules"
echo ""

if [ $MISSING -gt 0 ]; then
  echo "⚠️  Warning: $MISSING modules are missing (may not exist in this OCA branch)"
  echo "   Check the output above for details"
  echo ""
fi

echo "Next steps:"
echo "  1. Review module availability: ls -1 $OCA_BASE_DIR/modules"
echo "  2. Run bootstrap_ipai_bridge.sh to create bridge module"
echo "  3. Test with: docker compose -f docker-compose.odoo19.yml up -d"
echo ""
