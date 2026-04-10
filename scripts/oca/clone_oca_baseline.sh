#!/usr/bin/env bash
# Clone OCA baseline modules (sparse checkout, 18.0 branch only)
# Source: ssot/odoo/oca-baseline.yaml
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OCA_DIR="${REPO_ROOT}/addons/oca"
BRANCH="18.0"
GH_ORG="https://github.com/OCA"

mkdir -p "$OCA_DIR"

clone_sparse() {
  local repo="$1"
  shift
  local modules=("$@")
  local dest="${OCA_DIR}/${repo}"

  if [ -d "$dest/.git" ]; then
    echo "== ${repo}: already cloned, updating sparse set =="
    cd "$dest"
    git sparse-checkout set "${modules[@]}" setup.cfg 2>/dev/null || true
    git pull --ff-only origin "$BRANCH" 2>/dev/null || true
    cd "$REPO_ROOT"
    return
  fi

  echo "== Cloning OCA/${repo} (branch ${BRANCH}, sparse: ${modules[*]}) =="
  git clone --filter=blob:none --sparse --branch "$BRANCH" --single-branch --depth 1 \
    "${GH_ORG}/${repo}.git" "$dest" 2>&1 || {
      echo "WARN: OCA/${repo} has no ${BRANCH} branch, skipping"
      rm -rf "$dest"
      return
    }

  cd "$dest"
  git sparse-checkout set "${modules[@]}" setup.cfg 2>/dev/null || true
  cd "$REPO_ROOT"
}

# ─── partner-contact ────────────────────────────────────────────────────────
clone_sparse "partner-contact" \
  partner_contact_access_link \
  partner_firstname

# ─── queue ──────────────────────────────────────────────────────────────────
clone_sparse "queue" \
  queue_job \
  queue_job_cron

# ─── reporting-engine ───────────────────────────────────────────────────────
clone_sparse "reporting-engine" \
  report_xlsx

# ─── server-auth ────────────────────────────────────────────────────────────
clone_sparse "server-auth" \
  password_security \
  auth_oidc \
  auth_oidc_environment \
  auth_session_timeout \
  auth_api_key

# ─── server-brand ───────────────────────────────────────────────────────────
clone_sparse "server-brand" \
  disable_odoo_online \
  remove_odoo_enterprise

# ─── server-tools ───────────────────────────────────────────────────────────
clone_sparse "server-tools" \
  auditlog \
  base_name_search_improved \
  base_exception \
  auto_backup

# ─── server-ux ──────────────────────────────────────────────────────────────
clone_sparse "server-ux" \
  date_range \
  server_action_mass_edit

# ─── web ────────────────────────────────────────────────────────────────────
clone_sparse "web" \
  web_advanced_search \
  web_dialog_size \
  web_environment_ribbon \
  web_favicon \
  web_listview_range_select \
  web_m2x_options \
  web_no_bubble \
  web_pivot_computed_measure \
  web_refresher \
  web_responsive \
  web_search_with_and \
  web_tree_many2one_clickable \
  web_timeline

# ─── social (mail modules) ─────────────────────────────────────────────────
clone_sparse "social" \
  mail_debrand \
  mail_tracking \
  base_search_mail_content \
  mail_activity_done \
  mail_composer_cc_bcc \
  mail_activity_plan

# ─── knowledge ──────────────────────────────────────────────────────────────
clone_sparse "knowledge" \
  document_url \
  document_page_approval \
  document_page_project

# ─── account-financial-tools ────────────────────────────────────────────────
clone_sparse "account-financial-tools" \
  account_asset_management \
  account_chart_update

# ─── account-financial-reporting ────────────────────────────────────────────
clone_sparse "account-financial-reporting" \
  account_financial_report \
  account_tax_balance \
  partner_statement

# ─── account-reconcile ─────────────────────────────────────────────────────
clone_sparse "account-reconcile" \
  account_move_base_import \
  account_in_payment

# ─── mis-builder ────────────────────────────────────────────────────────────
clone_sparse "mis-builder" \
  mis_builder \
  mis_builder_budget

# ─── project ────────────────────────────────────────────────────────────────
clone_sparse "project" \
  project_parent \
  project_group \
  project_department \
  project_stakeholder \
  project_reviewer \
  project_role \
  project_template \
  project_timeline \
  project_pivot \
  project_milestone_status \
  project_key \
  project_tag_hierarchy \
  project_task_ancestor \
  project_task_parent_completion_blocking \
  project_task_stage_mgmt \
  project_type

# ─── helpdesk ───────────────────────────────────────────────────────────────
clone_sparse "helpdesk" \
  helpdesk_mgmt \
  helpdesk_mgmt_project \
  helpdesk_mgmt_crm

# ─── sale-workflow ──────────────────────────────────────────────────────────
clone_sparse "sale-workflow" \
  portal_sale_order_search \
  sale_cancel_reason \
  sale_commercial_partner \
  sale_delivery_state \
  sale_fixed_discount \
  sale_order_archive \
  sale_order_line_delivery_state \
  sale_order_line_input \
  sale_order_line_menu \
  sale_order_line_price_history \
  sale_automatic_workflow \
  sale_automatic_workflow_job \
  sale_advance_payment

# ─── sale-reporting ─────────────────────────────────────────────────────────
clone_sparse "sale-reporting" \
  sale_report_salesperson_from_partner

# ─── purchase-workflow ──────────────────────────────────────────────────────
clone_sparse "purchase-workflow" \
  partner_supplierinfo_smartbutton \
  product_supplier_code_purchase \
  purchase_cancel_reason \
  purchase_default_terms_conditions \
  purchase_order_archive \
  purchase_order_line_menu \
  purchase_last_price_info \
  purchase_advance_payment \
  purchase_commercial_partner \
  purchase_order_line_stock_available \
  purchase_request \
  purchase_tag \
  purchase_blanket_order

# ─── dms ────────────────────────────────────────────────────────────────────
clone_sparse "dms" \
  dms \
  dms_field \
  dms_user_role

# ─── ai (evaluate only) ────────────────────────────────────────────────────
clone_sparse "ai" \
  ai_oca_bridge \
  ai_oca_bridge_chatter \
  ai_oca_bridge_document_page \
  ai_oca_bridge_extra_parameters \
  ai_oca_native_generate_ollama

echo ""
echo "=== OCA baseline clone complete ==="
echo "Repos cloned: $(ls -d ${OCA_DIR}/*/.git 2>/dev/null | wc -l | tr -d ' ')"
echo "Module dirs:  $(find ${OCA_DIR} -maxdepth 2 -name '__manifest__.py' | wc -l | tr -d ' ')"
