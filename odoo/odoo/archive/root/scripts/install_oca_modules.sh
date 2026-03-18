#!/bin/bash
# =============================================================================
# OCA Module Installation Script
# =============================================================================
# Installs OCA community modules for InsightPulse Finance SSC
# Run from repository root: ./scripts/install_oca_modules.sh
# =============================================================================

set -euo pipefail

# Configuration
OCA_DIR="${OCA_DIR:-./oca}"
BRANCH="${BRANCH:-18.0}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo}"
DB_NAME="${DB_NAME:-odoo}"

echo "=========================================="
echo "OCA Module Installation"
echo "=========================================="
echo "Branch: ${BRANCH}"
echo "OCA Directory: ${OCA_DIR}"
echo ""

# Create OCA directory
mkdir -p "${OCA_DIR}"

# -----------------------------------------------------------------------------
# Function: Clone or update OCA repository
# -----------------------------------------------------------------------------
clone_or_update() {
    local repo=$1
    local dir_name=$(basename "$repo")
    local target="${OCA_DIR}/${dir_name}"

    if [ -d "$target" ]; then
        echo "[UPDATE] ${dir_name}"
        cd "$target"
        git fetch origin
        git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}" "origin/${BRANCH}"
        git pull origin "${BRANCH}"
        cd - > /dev/null
    else
        echo "[CLONE] ${dir_name}"
        git clone -b "${BRANCH}" --depth 1 "https://github.com/OCA/${repo}.git" "$target"
    fi
}

# -----------------------------------------------------------------------------
# TIER 1: Core Finance
# -----------------------------------------------------------------------------
echo ""
echo "=== TIER 1: Core Finance ==="
clone_or_update "account-financial-tools"
clone_or_update "account-financial-reporting"
clone_or_update "account-reconcile"
clone_or_update "reporting-engine"

# -----------------------------------------------------------------------------
# TIER 2: Workflow & Operations
# -----------------------------------------------------------------------------
echo ""
echo "=== TIER 2: Workflow & Operations ==="
clone_or_update "purchase-workflow"
clone_or_update "sale-workflow"
clone_or_update "hr-expense"
clone_or_update "project"

# -----------------------------------------------------------------------------
# TIER 3: Integration & API
# -----------------------------------------------------------------------------
echo ""
echo "=== TIER 3: Integration & API ==="
clone_or_update "rest-framework"
clone_or_update "connector"
clone_or_update "storage"

# -----------------------------------------------------------------------------
# TIER 4: Reporting & BI
# -----------------------------------------------------------------------------
echo ""
echo "=== TIER 4: Reporting & BI ==="
clone_or_update "margin-analysis"
clone_or_update "purchase-reporting"
clone_or_update "management-system"

# -----------------------------------------------------------------------------
# Install Python dependencies
# -----------------------------------------------------------------------------
echo ""
echo "=== Installing Python Dependencies ==="

# Create requirements file for OCA modules
cat > "${OCA_DIR}/requirements-oca.txt" << 'EOF'
# OCA Module Dependencies
xlsxwriter>=3.0.0
xlrd>=2.0.0
openpyxl>=3.0.0
python-stdnum>=1.18
phonenumbers>=8.12.0
# REST Framework
cerberus>=1.3.4
pyquerystring>=1.1
# GraphQL
graphql-core>=3.0.0
EOF

if command -v pip &> /dev/null; then
    echo "Installing Python packages..."
    pip install -r "${OCA_DIR}/requirements-oca.txt" --quiet
fi

# -----------------------------------------------------------------------------
# Generate addons_path for odoo.conf
# -----------------------------------------------------------------------------
echo ""
echo "=== Generating addons_path ==="

ADDONS_PATH=""
for dir in "${OCA_DIR}"/*/; do
    if [ -d "$dir" ]; then
        ADDONS_PATH="${ADDONS_PATH},$(realpath "$dir")"
    fi
done

echo ""
echo "Add this to odoo.conf:"
echo "addons_path = /opt/odoo/addons${ADDONS_PATH}"

# -----------------------------------------------------------------------------
# Docker installation (if using Docker)
# -----------------------------------------------------------------------------
if command -v docker &> /dev/null && docker ps | grep -q "${ODOO_CONTAINER}"; then
    echo ""
    echo "=== Docker Installation ==="

    read -p "Install modules in Docker? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Install Tier 1 modules
        echo "Installing Tier 1 modules..."
        docker exec -it "${ODOO_CONTAINER}" odoo -d "${DB_NAME}" -i \
            account_lock_date,account_financial_report,report_xlsx \
            --stop-after-init

        echo "Tier 1 modules installed!"
        echo ""
        echo "To install additional modules, run:"
        echo "docker exec -it ${ODOO_CONTAINER} odoo -d ${DB_NAME} -i MODULE_NAME --stop-after-init"
    fi
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Repositories cloned:"
ls -1 "${OCA_DIR}"
echo ""
echo "Next steps:"
echo "1. Update odoo.conf with the addons_path above"
echo "2. Restart Odoo"
echo "3. Go to Apps → Update Apps List"
echo "4. Search and install required modules"
echo ""
echo "Priority modules to install:"
echo "  - account_financial_report (Trial Balance, GL)"
echo "  - account_lock_date (Period Locking)"
echo "  - account_reconcile_oca (Bank Reconciliation)"
echo "  - report_xlsx (Excel Exports)"
echo "  - base_rest (REST API)"
echo "  - hr_expense_advance_clearing (Expense Advances)"
