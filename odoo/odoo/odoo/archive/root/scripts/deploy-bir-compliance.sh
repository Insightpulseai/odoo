#!/bin/bash
#
# BIR Compliance System Deployment Script
# =========================================
# Deploys OKR scoring, reminder system, and lead time corrections
# to Odoo 18.0 CE IPAI Finance PPM module
#
# Prerequisites:
# - PostgreSQL access via POSTGRES_URL environment variable
# - Odoo instance access (for module upgrade)
# - n8n instance access (for workflow import)
# - Mattermost webhook URL
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BIR Compliance System Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# =============================================================================
# Step 1: Verify Prerequisites
# =============================================================================
echo -e "${YELLOW}[1/8] Verifying prerequisites...${NC}"

if [ -z "${POSTGRES_URL:-}" ]; then
    echo -e "${RED}ERROR: POSTGRES_URL environment variable not set${NC}"
    echo "Set it with: export POSTGRES_URL='postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require'"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo -e "${RED}ERROR: psql command not found${NC}"
    echo "Install PostgreSQL client tools"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites verified${NC}"
echo ""

# =============================================================================
# Step 2: Execute OKR Scoring SQL Functions
# =============================================================================
echo -e "${YELLOW}[2/8] Deploying OKR scoring SQL functions...${NC}"

SQL_FILE="$PROJECT_ROOT/addons/ipai/ipai_finance_ppm/data/okr_scoring_functions.sql"

if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}ERROR: OKR scoring SQL file not found at $SQL_FILE${NC}"
    exit 1
fi

psql "$POSTGRES_URL" -f "$SQL_FILE" -v ON_ERROR_STOP=1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ OKR scoring functions deployed${NC}"
else
    echo -e "${RED}✗ Failed to deploy OKR scoring functions${NC}"
    exit 1
fi
echo ""

# =============================================================================
# Step 3: Execute Lead Time Corrections SQL
# =============================================================================
echo -e "${YELLOW}[3/8] Applying lead time corrections...${NC}"

LEADTIME_SQL="$PROJECT_ROOT/claudedocs/bir-filing-lead-time-corrections.sql"

if [ ! -f "$LEADTIME_SQL" ]; then
    echo -e "${RED}ERROR: Lead time corrections SQL file not found at $LEADTIME_SQL${NC}"
    exit 1
fi

psql "$POSTGRES_URL" -f "$LEADTIME_SQL" -v ON_ERROR_STOP=1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Lead time corrections applied${NC}"
else
    echo -e "${RED}✗ Failed to apply lead time corrections${NC}"
    exit 1
fi
echo ""

# =============================================================================
# Step 4: Verify Reminder System Files
# =============================================================================
echo -e "${YELLOW}[4/8] Verifying reminder system files...${NC}"

FILES_TO_CHECK=(
    "$PROJECT_ROOT/addons/ipai/ipai_finance_ppm/models/bir_reminder_system.py"
    "$PROJECT_ROOT/addons/ipai/ipai_finance_ppm/data/reminder_system_cron.xml"
    "$PROJECT_ROOT/automations/n8n/bir_deadline_reminder_workflow.json"
    "$PROJECT_ROOT/automations/n8n/bir_overdue_nudge_workflow.json"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}ERROR: Required file not found: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ All reminder system files present${NC}"
echo ""

# =============================================================================
# Step 5: Upgrade Odoo Module
# =============================================================================
echo -e "${YELLOW}[5/8] Upgrading IPAI Finance PPM module...${NC}"
echo ""
echo -e "${YELLOW}MANUAL ACTION REQUIRED:${NC}"
echo "Run the following command on your Odoo server:"
echo ""
echo "  odoo -d production -u ipai_finance_ppm --stop-after-init"
echo ""
echo "OR if using docker:"
echo ""
echo "  docker exec odoo-erp-prod odoo -d production -u ipai_finance_ppm --stop-after-init"
echo ""
read -p "Press Enter once module upgrade is complete..."
echo -e "${GREEN}✓ Module upgrade acknowledged${NC}"
echo ""

# =============================================================================
# Step 6: Configure Mattermost Webhook
# =============================================================================
echo -e "${YELLOW}[6/8] Configuring Mattermost webhook...${NC}"
echo ""
echo -e "${YELLOW}MANUAL ACTION REQUIRED:${NC}"
echo "1. Go to Mattermost → Integrations → Incoming Webhooks"
echo "2. Create webhook for 'BIR Compliance Alerts' channel"
echo "3. Copy the webhook URL"
echo "4. Update Odoo system parameter:"
echo ""
echo "   Go to: Settings → Technical → Parameters → System Parameters"
echo "   Key: bir.reminder.mattermost.webhook"
echo "   Value: [paste webhook URL]"
echo ""
echo "5. Also set n8n webhook URL:"
echo "   Key: bir.reminder.n8n.webhook"
echo "   Value: https://ipa.insightpulseai.com/webhook/bir-reminder"
echo ""
echo "6. Set n8n overdue webhook URL:"
echo "   Key: bir.overdue.n8n.webhook"
echo "   Value: https://ipa.insightpulseai.com/webhook/bir-overdue-nudge"
echo ""
read -p "Press Enter once webhooks are configured..."
echo -e "${GREEN}✓ Webhook configuration acknowledged${NC}"
echo ""

# =============================================================================
# Step 7: Import n8n Workflows
# =============================================================================
echo -e "${YELLOW}[7/8] Importing n8n workflows...${NC}"
echo ""
echo -e "${YELLOW}MANUAL ACTION REQUIRED:${NC}"
echo "1. Open n8n at: https://ipa.insightpulseai.com"
echo "2. Import workflow files:"
echo "   - $PROJECT_ROOT/automations/n8n/bir_deadline_reminder_workflow.json"
echo "   - $PROJECT_ROOT/automations/n8n/bir_overdue_nudge_workflow.json"
echo ""
echo "3. For each workflow:"
echo "   a. Click 'Import from File'"
echo "   b. Select the JSON file"
echo "   c. Set environment variables:"
echo "      - MATTERMOST_WEBHOOK_URL (from step 6)"
echo "   d. Activate the workflow"
echo ""
read -p "Press Enter once n8n workflows are imported and activated..."
echo -e "${GREEN}✓ n8n workflow import acknowledged${NC}"
echo ""

# =============================================================================
# Step 8: Verification
# =============================================================================
echo -e "${YELLOW}[8/8] Running verification checks...${NC}"
echo ""

echo "Checking OKR scoring functions..."
psql "$POSTGRES_URL" -c "SELECT finance.calculate_kr_1_1_ontime_filing_rate(2025);" -t | head -1
echo ""

echo "Checking lead time corrections..."
psql "$POSTGRES_URL" -c "SELECT form_code, period, bir_deadline, prep_date, (bir_deadline - prep_date) AS lead_days FROM ipai_bir_form_schedule WHERE form_code IN ('2550Q', '1702-RT') ORDER BY bir_deadline DESC LIMIT 5;" -t
echo ""

echo "Checking reminder system fields..."
psql "$POSTGRES_URL" -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ipai_bir_form_schedule' AND column_name IN ('status', 'last_reminder_sent', 'reminder_count', 'filing_date');" -t
echo ""

echo -e "${YELLOW}Verify cron jobs in Odoo:${NC}"
echo "Go to: Settings → Technical → Automation → Scheduled Actions"
echo "Look for:"
echo "  - BIR Deadline Reminder - 9AM"
echo "  - BIR Deadline Reminder - 5PM"
echo "  - BIR Overdue Daily Nudge"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Test reminder system by creating a BIR form due today"
echo "2. Monitor Mattermost for reminder messages"
echo "3. Verify OKR scores are calculated correctly"
echo "4. Check lead times are within targets (D-6, D-60, D-90)"
echo ""
