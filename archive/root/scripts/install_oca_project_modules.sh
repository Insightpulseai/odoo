#!/bin/bash
# =============================================================================
# OCA Project Module Installation Script
# =============================================================================
# Installs OCA project management modules for Odoo 18 CE
# Compatible with Finance PPM workflow (Month-End Close, Tax Filing)
#
# Run from repository root: ./scripts/install_oca_project_modules.sh
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OCA_DIR="${OCA_DIR:-${REPO_ROOT}/addons/oca}"
BRANCH="${BRANCH:-18.0}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB_NAME="${DB_NAME:-odoo_core}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}OCA Project Module Installation${NC}"
echo -e "${BLUE}===========================================${NC}"
echo "Branch: ${BRANCH}"
echo "OCA Directory: ${OCA_DIR}"
echo "Database: ${DB_NAME}"
echo ""

# -----------------------------------------------------------------------------
# Function: Clone or update OCA repository
# -----------------------------------------------------------------------------
clone_or_update() {
    local repo=$1
    local dir_name=$(basename "$repo")
    local target="${OCA_DIR}/${dir_name}"

    if [ -d "$target" ]; then
        echo -e "${YELLOW}[UPDATE]${NC} ${dir_name}"
        cd "$target"
        git fetch origin
        git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}" "origin/${BRANCH}"
        git pull origin "${BRANCH}" || true
        cd - > /dev/null
    else
        echo -e "${GREEN}[CLONE]${NC} ${dir_name}"
        git clone -b "${BRANCH}" --depth 1 "https://github.com/OCA/${repo}.git" "$target" || {
            echo -e "${RED}[WARN]${NC} Branch ${BRANCH} not found, trying 17.0..."
            git clone -b "17.0" --depth 1 "https://github.com/OCA/${repo}.git" "$target"
        }
    fi
}

# Create OCA directory
mkdir -p "${OCA_DIR}"

# -----------------------------------------------------------------------------
# Clone OCA Project Repository
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}=== Cloning OCA Project Repository ===${NC}"
clone_or_update "project"

# -----------------------------------------------------------------------------
# List Available OCA Project Modules
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}=== Available OCA Project Modules ===${NC}"

PROJECT_MODULES=(
    # Core Project Modules (verified 18.0)
    "project_template:18.0:Project Templates"
    "project_timeline:18.0:Timeline view for projects"
    "project_timeline_hr_timesheet:18.0:Shows progress on timeline view"
    "project_timesheet_time_control:18.0:Timesheet time control"
    "project_type:18.0:Project Types"
    "project_version:18.0:Project Version"
    # Stage Management (may need porting from 17.0)
    "project_stage_closed:17.0:Locks stages in Kanban view"
    "project_stage_state:17.0:Maps stages to states (draft/open/pending/done)"
    "project_task_stage_mgmt:17.0:Assign/create task stages when creating project"
    # Task Management
    "project_task_code:18.0:Task coding/numbering"
    "project_task_default_stage:18.0:Default stage assignment"
    "project_task_dependency:18.0:Task dependencies (FS/SS/FF/SF)"
    "project_task_recurring:18.0:Recurring tasks"
    "project_task_template:18.0:Task templates"
    # Advanced (may need porting)
    "project_wbs:17.0:Work Breakdown Structure"
)

printf "%-35s %-8s %s\n" "Module" "Version" "Description"
printf "%-35s %-8s %s\n" "------" "-------" "-----------"
for module_info in "${PROJECT_MODULES[@]}"; do
    IFS=':' read -r module_name version desc <<< "$module_info"
    printf "%-35s %-8s %s\n" "$module_name" "$version" "$desc"
done

# -----------------------------------------------------------------------------
# Recommended Installation Order (Finance PPM)
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}=== Recommended Installation Order for Finance PPM ===${NC}"

cat << 'EOF'

TIER 1 - Core (Install First):
  docker compose exec odoo-core odoo -d odoo_core -i \
    project_template,project_type,project_task_code \
    --stop-after-init

TIER 2 - Stage Management:
  docker compose exec odoo-core odoo -d odoo_core -i \
    project_stage_closed,project_task_default_stage \
    --stop-after-init

TIER 3 - Timeline & Dependencies:
  docker compose exec odoo-core odoo -d odoo_core -i \
    project_timeline,project_task_dependency \
    --stop-after-init

TIER 4 - Templates & Recurring:
  docker compose exec odoo-core odoo -d odoo_core -i \
    project_task_template,project_task_recurring \
    --stop-after-init

EOF

# -----------------------------------------------------------------------------
# Verification Commands
# -----------------------------------------------------------------------------
echo -e "${BLUE}=== Verification Commands ===${NC}"

cat << 'EOF'

Check installed modules:
  docker compose exec odoo-core odoo shell -d odoo_core << PYTHON
env['ir.module.module'].search([
    ('name', 'ilike', 'project_%'),
    ('state', '=', 'installed')
]).mapped('name')
PYTHON

Verify stages created:
  docker compose exec odoo-core odoo shell -d odoo_core << PYTHON
for stage in env['project.task.type'].search([]):
    print(f"{stage.sequence}: {stage.name} (fold={stage.fold})")
PYTHON

Health check:
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health

EOF

# -----------------------------------------------------------------------------
# IPAI Module Installation
# -----------------------------------------------------------------------------
echo -e "${BLUE}=== IPAI Finance PPM Module Installation ===${NC}"

cat << 'EOF'

Install IPAI Project Program module (includes OCA-compatible stages):
  docker compose exec odoo-core odoo -d odoo_core -i \
    ipai_project_program \
    --stop-after-init

Install complete Finance PPM stack:
  docker compose exec odoo-core odoo -d odoo_core -i \
    ipai_project_program,ipai_finance_ppm \
    --stop-after-init

EOF

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Configuration Complete!${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo "OCA Project repository location: ${OCA_DIR}/project"
echo ""
echo "Standard Stages Created by ipai_project_program:"
echo "  1. To Do           (sequence=10, fold=false, state=draft)"
echo "  2. In Preparation  (sequence=20, fold=false, state=open)"
echo "  3. Under Review    (sequence=30, fold=false, state=open)"
echo "  4. Pending Approval(sequence=40, fold=false, state=pending)"
echo "  5. Done            (sequence=50, fold=true,  state=done)"
echo "  6. Cancelled       (sequence=60, fold=true,  state=cancelled)"
echo ""
echo "CSV Templates available at:"
echo "  - addons/ipai/ipai_project_program/data/templates/project_stage_import_template.csv"
echo "  - addons/ipai/ipai_project_program/data/templates/project_task_import_template.csv"
echo ""
