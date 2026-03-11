#!/bin/bash
# deploy-december-2025-bir-tasks.sh
# Automated deployment of December 2025 BIR schedule tasks to production Odoo
#
# Purpose: Replace duplicate December 2025 BIR tasks with properly assigned tasks
# Target: Project 6 (BIR Tax Filing), Project 7 (Month-end closing)
#
# Usage: ./scripts/deploy-december-2025-bir-tasks.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROD_HOST="root@159.223.75.148"
ODOO_CONTAINER="odoo-core"
POSTGRES_CONTAINER="odoo-postgres"
DB_NAME="odoo_core"

echo -e "${GREEN}=== December 2025 BIR Task Deployment ===${NC}"
echo ""

# 1. Copy files to production server
echo -e "${YELLOW}Step 1: Copying files to production server...${NC}"
scp scripts/cleanup-duplicate-dec2025-tasks.sql "$PROD_HOST:/tmp/"
scp scripts/insert-december-2025-tasks.sql "$PROD_HOST:/tmp/"

# 2. Cleanup duplicate tasks
echo -e "${YELLOW}Step 2: Cleaning up duplicate December 2025 tasks...${NC}"
ssh "$PROD_HOST" "docker cp /tmp/cleanup-duplicate-dec2025-tasks.sql $POSTGRES_CONTAINER:/tmp/"
ssh "$PROD_HOST" "docker exec $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -f /tmp/cleanup-duplicate-dec2025-tasks.sql"

# 3. Verify cleanup
echo -e "${YELLOW}Step 3: Verifying cleanup...${NC}"
duplicate_count=$(ssh "$PROD_HOST" "docker exec -t $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -t -c \"SELECT COUNT(*) FROM project_task WHERE id IN (178, 186, 242, 243);\"" | tr -d '[:space:]')

if [ "$duplicate_count" != "0" ]; then
    echo -e "${RED}ERROR: Duplicate tasks still exist (count: $duplicate_count)${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Duplicates removed successfully${NC}"

# 4. Import December 2025 tasks
echo -e "${YELLOW}Step 4: Importing December 2025 BIR schedule tasks...${NC}"
ssh "$PROD_HOST" "docker cp /tmp/insert-december-2025-tasks.sql $POSTGRES_CONTAINER:/tmp/"
ssh "$PROD_HOST" "docker exec $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -f /tmp/insert-december-2025-tasks.sql"

# 5. Verify import
echo -e "${YELLOW}Step 5: Verifying import...${NC}"

# Check BIR tasks (Project 6)
bir_task_count=$(ssh "$PROD_HOST" "docker exec -t $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -t -c \"SELECT COUNT(*) FROM project_task WHERE project_id=6 AND (name LIKE '%JAN-10%' OR name LIKE '%JAN-25%') AND date_deadline >= '2026-01-01';\"" | tr -d '[:space:]')

echo -e "${GREEN}  ✓ BIR Tax Filing tasks (Project 6): $bir_task_count${NC}"
echo -e "${GREEN}    Expected: 6 tasks (3× 1601-C + 3× 2550Q)${NC}"

# Check closing tasks (Project 7)
closing_task_count=$(ssh "$PROD_HOST" "docker exec -t $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -t -c \"SELECT COUNT(*) FROM project_task WHERE project_id=7 AND name LIKE '%December 2025%';\"" | tr -d '[:space:]')

echo -e "${GREEN}  ✓ Month-end closing tasks (Project 7): $closing_task_count${NC}"
echo -e "${GREEN}    Expected: 4 tasks (Bank Recon + GL Recon + Financials + Sign-off)${NC}"

# 6. Display task assignments
echo -e "${YELLOW}Step 6: Displaying task assignments...${NC}"
ssh "$PROD_HOST" "docker exec $POSTGRES_CONTAINER psql -U odoo -d $DB_NAME -c \"
SELECT
    t.name as task_name,
    t.date_deadline,
    p.name as assigned_to
FROM project_task t
LEFT JOIN res_users u ON u.id = ANY(t.user_ids)
LEFT JOIN res_partner p ON u.partner_id = p.id
WHERE t.project_id IN (6, 7)
  AND t.date_deadline >= '2026-01-01'
  AND t.date_deadline <= '2026-01-31'
ORDER BY t.project_id, t.date_deadline;
\""

# 7. Summary
echo ""
echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo -e "${GREEN}✓ Duplicate tasks removed: 4${NC}"
echo -e "${GREEN}✓ BIR tasks created (Project 6): $bir_task_count${NC}"
echo -e "${GREEN}✓ Closing tasks created (Project 7): $closing_task_count${NC}"
echo ""
echo -e "${GREEN}Total December 2025 tasks: $(($bir_task_count + $closing_task_count))${NC}"
echo ""
echo -e "${YELLOW}Task Assignment Summary:${NC}"
echo -e "  • Jerald Loterte (GL): 1601-C Prep, GL Reconciliation"
echo -e "  • Khalil Veracruz (Finance Manager): 1601-C Review, 2550Q Review, Financials"
echo -e "  • Rey Meran (Finance Director): 1601-C Approval, 2550Q Approval, Sign-off"
echo -e "  • Jhoee Oliva (Tax Specialist): 2550Q Prep"
echo -e "  • Joana Maravillas (Reconciliation): Bank Reconciliation"
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo "Access tasks: http://159.223.75.148:8069/odoo/project?view_type=list"
