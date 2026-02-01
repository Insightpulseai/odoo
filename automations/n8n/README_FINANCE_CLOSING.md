# Finance Month-End Closing - n8n Automation

## Overview

Automated workflows for Finance Month-End Closing based on `ipai_finance_closing` Odoo module.

**Scope**: Automation for Day 1, 5, and 10 reminders. **Does not include** BIR tax filing (separate workflow).

---

## Workflows

### 1. `finance_closing_automation.json`

**Purpose**: Core month-end closing automation with 4 scheduled triggers

**Triggers**:
| Schedule | Action | Description |
|----------|--------|-------------|
| Day 1, 00:01 AM | Reverse Accruals | Auto-reverse prior month accrual entries |
| Day 1, 06:00 AM | Update FX Rates | Fetch BSP (Bangko Sentral) exchange rates |
| Day 5, 09:00 AM | Period Lock Reminder | Alert Finance Director of incomplete tasks |
| Day 10, 08:00 AM | BIR Filing Alerts | Remind Tax Specialist of filing deadlines |

**Requirements**:
- Environment variables: `ODOO_ADMIN_PASSWORD`, `MATTERMOST_WEBHOOK_URL`
- Odoo XML-RPC access to `odoo_core` database (port 8069)
- Mattermost webhook configured

**Nodes**:
1. **Schedule Triggers** (4): Cron-based triggers for each automation
2. **Odoo XML-RPC Calls** (4): Query/execute Odoo operations
3. **Mattermost Notifications** (4): Send alerts to #finance-close channel

### 2. `bir_deadline_reminder_workflow.json` (Existing)

**Purpose**: BIR filing deadline reminders triggered by webhook

**Trigger**: Webhook `POST /webhook/bir-reminder`

**Payload**:
```json
{
  "bir_form": "1601-C",
  "period": "2025-12",
  "deadline": "2026-01-10",
  "status": "not_started",
  "responsible_email": "jhoee.oliva@omc.com",
  "reminder_type": "due_date_9am"
}
```

**Notifications**:
- Mattermost message to #finance-close
- Email backup to responsible user

---

## Installation

### Prerequisites

1. **n8n Server**: https://ipa.insightpulseai.com
2. **Credentials**:
   - n8n API Key (JWT token)
   - Odoo admin password
   - Mattermost webhook URL

3. **Environment Variables** (set in n8n):
   ```bash
   ODOO_ADMIN_PASSWORD=<odoo_admin_password>
   MATTERMOST_WEBHOOK_URL=https://mattermost.insightpulseai.com/hooks/...
   ```

### Import Workflows

**Option 1: n8n UI (Recommended)**

1. **Login** to n8n: https://ipa.insightpulseai.com
2. **Navigate**: Workflows → Import from File
3. **Upload**: `finance_closing_automation.json`
4. **Configure**:
   - Set credentials (Odoo XML-RPC, Mattermost)
   - Verify environment variables
5. **Activate**: Toggle workflow to active state

**Option 2: n8n API**

```bash
# Set n8n API credentials
export N8N_BASE_URL="https://ipa.insightpulseai.com"
export N8N_API_KEY="<jwt_token>"

# Import workflow
curl -X POST "${N8N_BASE_URL}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @finance_closing_automation.json

# List workflows
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "${N8N_BASE_URL}/api/v1/workflows" | jq '.data[] | {id, name, active}'
```

### Verify Installation

1. **Check Workflow Status**:
   ```bash
   curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
     "${N8N_BASE_URL}/api/v1/workflows" \
     | jq '.data[] | select(.name | contains("Finance Month-End"))'
   ```

2. **Test Manual Execution**:
   - n8n UI → Workflows → "Finance Month-End Closing - Automation"
   - Click "Execute Workflow" on any trigger node
   - Verify Mattermost notification received

3. **Verify Cron Schedules**:
   - Day 1 00:01: `1 0 1 * *` (Reverse Accruals)
   - Day 1 06:00: `0 6 1 * *` (FX Rates)
   - Day 5 09:00: `0 9 5 * *` (Period Lock)
   - Day 10 08:00: `0 8 10 * *` (BIR Alerts)

---

## Configuration

### Odoo XML-RPC Connection

**Endpoint**: `http://159.223.75.148:8069/xmlrpc/2/object`

**Authentication**:
- Database: `odoo_core`
- UID: 2 (admin user)
- Password: `{{ $env.ODOO_ADMIN_PASSWORD }}`

**Test Connection**:
```bash
python3 << 'EOF'
import xmlrpc.client

url = "http://159.223.75.148:8069"
db = "odoo_core"
uid = 2
password = "admin"  # Replace with actual password

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Test query: Get incomplete month-end tasks
tasks = models.execute_kw(db, uid, password,
    'project.task', 'search_read',
    [[('project_id.name', 'ilike', 'Month-End Close')]],
    {'fields': ['name', 'stage_id'], 'limit': 5}
)

print(f"Found {len(tasks)} month-end tasks")
for task in tasks:
    print(f"  - {task['name']}")
EOF
```

### Mattermost Webhook

**Channel**: #finance-close

**Webhook URL**: Set in n8n environment variables

**Test Notification**:
```bash
curl -X POST "${MATTERMOST_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🧪 Test notification from Finance Closing automation",
    "username": "n8n Finance Bot",
    "icon_emoji": ":calendar:"
  }'
```

---

## Workflow Logic

### 1. Reverse Accruals (Day 1, 00:01 AM)

```yaml
Trigger: Day 1 of month at 00:01
↓
Query Odoo: Find accruals to reverse
  - Search: state=posted, auto_reverse=true, not yet reversed
↓
Notify Mattermost: "X entries reversed"
```

**Odoo XML-RPC Call**:
```python
models.execute_kw('odoo_core', 2, password,
    'account.move', 'search_read',
    [[
        ('state', '=', 'posted'),
        ('auto_reverse', '=', True),
        ('reversed_entry_id', '=', False)
    ]],
    ['id', 'name', 'date']
)
```

### 2. Update FX Rates (Day 1, 06:00 AM)

```yaml
Trigger: Day 1 of month at 06:00
↓
Call Odoo: Update currency rates from BSP
  - Method: res.currency.cron_update_currency_rates
↓
Notify Mattermost: "FX rates updated"
```

### 3. Period Lock Reminder (Day 5, 09:00 AM)

```yaml
Trigger: Day 5 of month at 09:00
↓
Query Odoo: Check incomplete month-end tasks
  - Filter: project.name ilike "Month-End Close", stage != Done
↓
Notify Mattermost: "X incomplete tasks" + task list
  - cc: @finance-director
```

### 4. BIR Filing Alerts (Day 10, 08:00 AM)

```yaml
Trigger: Day 10 of month at 08:00
↓
Query Odoo: Check pending BIR tasks
  - Filter: name ilike "BIR", stage != Done
↓
Notify Mattermost: "BIR forms due today" + task list
  - cc: @tax-specialist @finance-director
```

---

## Monitoring

### n8n Execution History

**View Executions**:
1. n8n UI → Executions
2. Filter by workflow: "Finance Month-End Closing - Automation"
3. Review success/failure status

**Check Logs**:
```bash
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "${N8N_BASE_URL}/api/v1/executions" \
  | jq '.data[] | select(.workflowData.name | contains("Finance")) | {id, status, startedAt}'
```

### Mattermost Alerts

**Expected Notifications**:
- Day 1, 00:01: "✅ Accrual Reversal Complete"
- Day 1, 06:00: "💱 FX Rates Updated"
- Day 5, 09:00: "⏰ Period Lock Reminder"
- Day 10, 08:00: "📋 BIR Filing Deadline Alerts"

---

## Troubleshooting

### Problem: Workflow Not Executing

**Check**:
1. Workflow is **Active** (toggle in n8n UI)
2. Cron expression is correct (use https://crontab.guru)
3. n8n server timezone matches expectations (UTC vs PHT)

**Fix Timezone**:
```bash
# If n8n runs in UTC, adjust cron for PHT (UTC+8)
# Example: 00:01 PHT = 16:01 UTC (previous day)
# Cron: "1 16 * * *" (triggers at Day 0, 16:01 UTC = Day 1, 00:01 PHT)
```

### Problem: Odoo XML-RPC Connection Failed

**Symptoms**: "Connection refused" or "Authentication failed"

**Solution**:
```bash
# Test Odoo reachability
curl -s http://159.223.75.148:8069/web/database/selector | grep -q "odoo_core" && echo "Odoo accessible"

# Verify credentials
python3 << 'EOF'
import xmlrpc.client
common = xmlrpc.client.ServerProxy("http://159.223.75.148:8069/xmlrpc/2/common")
uid = common.authenticate("odoo_core", "admin", "admin", {})
print(f"UID: {uid}" if uid else "Authentication failed")
EOF
```

### Problem: Mattermost Notifications Not Sent

**Check**:
1. `MATTERMOST_WEBHOOK_URL` environment variable set in n8n
2. Webhook URL is valid (test with curl)
3. Mattermost channel exists (#finance-close)

**Test Webhook**:
```bash
curl -X POST "${MATTERMOST_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test from n8n troubleshooting"}'
```

---

## Maintenance

### Monthly Tasks

1. **Review Execution Logs**: Check for failures in previous month
2. **Update BIR Deadlines**: Verify Day 10/15/20/25 schedules match BIR calendar
3. **Test Notifications**: Manually execute workflows to verify Mattermost alerts

### Quarterly Tasks

1. **Review Automation Effectiveness**: Survey Finance team on reminder usefulness
2. **Update Task Queries**: Adjust Odoo queries if task names change
3. **Optimize Cron Schedules**: Move times if conflicts with other operations

---

## Integration with Odoo Module

**Module**: `ipai_finance_closing` (installed in odoo_core)

**Dependencies**:
- Project template: "Month-End Close Template" (ID: 15)
- 26 tasks with role-based assignments
- Task stages: Backlog, In Progress, Done

**n8n → Odoo Data Flow**:
```
n8n Trigger (Cron)
  ↓
XML-RPC Query (search_read)
  ↓
Process Results (filter, transform)
  ↓
Mattermost Notification (formatted message)
```

**Odoo → n8n Data Flow** (Future Enhancement):
```
Odoo Automated Action (task completion)
  ↓
Webhook Trigger (POST /webhook/task-complete)
  ↓
n8n Updates Task Dependencies
  ↓
Notify Next Assignee
```

---

## Future Enhancements

### Phase 4: CI/CD Orchestrator
- GitHub webhook → n8n → Deploy validation
- Notify #devops on deploy success/failure

### Phase 5: Health Monitoring
- Service health checks every 5 minutes
- Alert #devops on failures
- Auto-restart services after 3 failures

### Phase 6: BIR Tax Filing Workflow
- **NOT** in month-end close scope
- Separate workflow for Days 10-25
- DAT file generation
- eBIRForms submission tracking
- Payment confirmation

---

## Support

**Issues**: https://github.com/jgtolentino/odoo-ce/issues
**n8n Docs**: https://docs.n8n.io
**Maintainer**: Finance Director + IT Market Director

---

**Last Updated**: 2025-12-30
**Version**: 1.0.0
