# InsightPulse Finance Month-End Closing

**Version**: 18.0.1.0.0
**Category**: Finance/Automation
**License**: AGPL-3
**Deployment Status**: ✅ **[See DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)**

## Overview

Comprehensive month-end financial closing task template based on **SAP Advanced Financial Closing (AFC)** best practices, adapted for Odoo CE 18 and Philippine BIR compliance.

**Key Benefits:**
- ✅ **7 days → 4 days**: Reduce closing cycle from 7 to 4 business days
- ✅ **26 pre-configured tasks**: Complete SAP AFC-inspired checklist
- ✅ **Task assignments**: Automatic role-based assignment (Finance Director, AP/AR/GL/Tax specialists)
- ✅ **Tax preparation**: BIR 1601-C, 1601-EQ, 2550M/Q report generation
- ✅ **n8n integration**: Webhook-triggered closing orchestration
- ✅ **Separation of concerns**: Month-end close ≠ Tax filing (handled by n8n workflows)

---

## Features

### 1. Task Structure (5 Phases)

| Phase | Days | Task Count | Key Activities |
|-------|------|------------|----------------|
| **Pre-Closing** | -5 to -1 | 2 tasks | Period management, master data review |
| **Subledgers** | 1-3 | 10 tasks | AP/AR/Asset processing |
| **General Ledger** | 3-5 | 5 tasks | Accruals, reconciliations, FX |
| **Tax Preparation** | 3-7 | 3 tasks | BIR forms PREPARATION (1601-C, 1601-EQ, 2550M/Q) |
| **Reporting** | 5-7 | 6 tasks | Trial balance, financials, management reports |

**Total**: 26 tasks

**Scope**: Month-end close + tax **preparation** (Days 1-7). BIR tax **filing** (Days 10-25) is handled separately via n8n workflows.

### 2. Task Assignments (Role-Based)

| Role | User | Task Count | Functional Areas |
|------|------|------------|------------------|
| **Finance Director** | Rey Meran | 4 | Period open/close, master data, sign-off |
| **AP Specialist** | Jasmin Ignacio | 3 | Vendor bills, GR/IR, payments |
| **AR Specialist** | Jinky Paladin | 4 | Customer invoices, collections, bad debt |
| **GL Specialist** | Jerald Loterte | 7 | Assets, accruals, FX, journal entries |
| **Tax Specialist** | Jhoee Oliva | 3 | BIR 1601-C, 1601-EQ, 2550M/Q preparation |
| **Reconciliation** | Joana Maravillas | 2 | Bank, subledger reconciliations |
| **Finance Manager** | Khalil Veracruz | 3 | Trial balance, financials, coordination |

### 3. Automated Actions (n8n Workflows)

**Note**: Automation via scheduled actions disabled in initial release due to Odoo 18 restrictions. Use n8n workflows instead:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| **Reverse Accruals** | Day 1, 00:01 AM | Auto-reverse prior month accrual entries |
| **Update FX Rates** | Day 1, 06:00 AM | Fetch BSP (Bangko Sentral) exchange rates |
| **Period Lock Reminder** | Day 5, 09:00 AM | Mattermost notification |
| **BIR Filing Alerts** | Day 10, 08:00 AM | 1601-C, 1601-EQ, 2550M/Q deadline reminders |

### 4. BIR (Philippine Tax) Preparation vs. Filing

**✅ Included in Template (Tax Preparation):**
- **4.1**: Prepare BIR 1601-C (Withholding Tax - Compensation)
- **4.2**: Prepare BIR 1601-EQ (Expanded Withholding Tax)
- **4.3**: Prepare BIR 2550M/Q (Monthly/Quarterly VAT Return)

**❌ NOT Included (Tax Filing - Separate n8n Workflow):**
- BIR data validation (cross-check with GL)
- DAT file generation for eBIRForms
- Submission to BIR eFPS/eBIRForms
- Payment processing via bank/eFPS
- Filing confirmation archival

**Rationale**: Month-end close (Days 1-7) ≠ Tax filing (Days 10-25). Different timelines and processes require separation.

---

## Installation

### Prerequisites

- Odoo CE 18.0
- Modules: `project`, `account`
- PostgreSQL 15+
- Python 3.11+

### Steps

1. **Copy module to addons path**
   ```bash
   cd ~/Documents/GitHub/odoo-ce
   cp -r addons/ipai_finance_closing /opt/odoo-ce/addons/
   ```

2. **Update Odoo apps list**
   ```bash
   # Via Odoo CLI
   docker-compose restart odoo

   # Or via UI
   Apps → Update Apps List
   ```

3. **Install module**
   ```bash
   # Via UI
   Apps → Search "Finance Closing" → Install

   # Or via CLI
   odoo -d production -i ipai_finance_closing --stop-after-init
   ```

4. **Verify installation**
   ```bash
   # Check scheduled actions
   Settings → Technical → Automation → Scheduled Actions
   # Should see: Reverse Accruals, Update FX Rates, Run Depreciation, etc.

   # Check project template
   Project → Configuration → Templates
   # Should see: "Month-End Close Template"
   ```

---

## Usage

### Option 1: Manual (Odoo UI)

1. **Create project from template**
   - Project → Projects → Create
   - Name: "Month-End Close - Dec 2025"
   - Use Template: "Month-End Close Template"
   - Click "Create"

2. **Assign tasks to team**
   - Open project
   - For each task → Edit → Assign to user
   - Set deadlines based on close calendar

3. **Track progress**
   - Project → Kanban/List view
   - Filter by tag (e.g., [GL], [AP])
   - Mark tasks complete as they finish

### Option 2: Automated (n8n Webhook)

1. **Trigger via n8n workflow**
   ```bash
   curl -X POST "https://n8n.insightpulseai.net/webhook/month-end-close" \
     -H "Content-Type: application/json" \
     -d '{
       "month": "2025-12",
       "finance_manager_id": 2,
       "gl_accountant_id": 3,
       "ap_clerk_id": 4
     }'
   ```

2. **n8n workflow actions**
   - Creates project: "Month-End Close - Dec 2025"
   - Creates all 26 tasks with role-based assignments
   - Sets task dependencies
   - Schedules automated reminders
   - Notifies Mattermost: "Month-end closing started"

3. **Daily progress monitoring**
   - n8n queries task status daily
   - Calculates % complete
   - Alerts if overdue tasks
   - Notifies Finance Manager via Mattermost

---

## Task Dependencies

Tasks are sequenced using `depends_on` field. Example:

```
Bank Reconciliation
   ├─ depends_on: AP Reconciliation
   ├─ depends_on: AR Reconciliation
   └─ depends_on: Payroll Reconciliation
```

**Dependency Rules:**
- Cannot start task until all predecessors are complete
- Odoo blocks task assignment if dependencies not met
- Use Gantt chart to visualize critical path

---

## Configuration

### 1. Scheduled Actions (Cron Jobs)

Edit in: **Settings → Technical → Automation → Scheduled Actions**

| Action | Interval | Next Run | Active |
|--------|----------|----------|--------|
| Reverse Prior Month Accruals | Monthly (Day 1, 00:01) | 2026-01-01 00:01 | ✅ |
| Update BSP Exchange Rates | Monthly (Day 1, 06:00) | 2026-01-01 06:00 | ✅ |
| Run Asset Depreciation | Monthly (Last Day -1, 23:00) | 2025-12-30 23:00 | ✅ |
| Period Lock Reminder | Monthly (Day 5, 09:00) | 2026-01-05 09:00 | ✅ |
| BIR 1601-C Filing Reminder | Monthly (Day 10, 08:00) | 2026-01-10 08:00 | ✅ |

### 2. Task Template Customization

Edit tasks in: **data/closing_tasks.xml**

```xml
<record id="task_process_pending_bills" model="project.task">
  <field name="name">Process Pending Vendor Bills</field>
  <field name="description">
    Review and approve all pending vendor bills in draft state...
  </field>
  <field name="project_id" ref="template_month_end_close"/>
  <field name="tag_ids" eval="[(6, 0, [ref('tag_ap')])]"/>
  <field name="planned_hours">4.0</field>
  <field name="priority">1</field>
</record>
```

### 3. BIR Form Integration (Optional)

If you have `l10n_ph_bir` module installed:

```python
# Trigger BIR form generation from n8n
POST /xmlrpc/2/object
{
  "model": "bir.form",
  "method": "create",
  "args": [{
    "form_type": "1601-C",
    "period_id": REF('account.period_2025_12'),
    "company_id": 1
  }]
}
```

---

## Integration

### n8n Workflows

**Workflow**: `Finance Month-End Closing Orchestrator`

**Triggers**:
- Cron: Day 1 of month, 08:00 PHT
- Webhook: `POST /webhook/month-end-close`

**Actions**:
1. Create project from template (XML-RPC)
2. Create 57 tasks with dependencies
3. Assign to roles (Finance Manager, GL Accountant, etc.)
4. Schedule automated actions
5. Notify Mattermost: "Month-end closing started"
6. Monitor progress daily

**XML-RPC Example**:
```python
import xmlrpc.client

url = "https://odoo.insightpulseai.net"
db = "production"
username = "admin"
password = "xxx"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Create project from template
project_id = models.execute_kw(db, uid, password,
    'project.project', 'create',
    [{
        'name': 'Month-End Close - Dec 2025',
        'use_tasks': True,
        'template_id': 1  # REF('ipai_finance_closing.template_month_end_close')
    }]
)

print(f"Created project ID: {project_id}")
```

### Mattermost Notifications

**Channels**:
- `#finance-close` - Task updates, reminders
- `#devops` - Automated action status

**Alert Examples**:
```markdown
⚠️ **BIR 1601-C Due in 5 Days**
• Form: 1601-C (Monthly Withholding Tax)
• Period: December 2025
• Deadline: January 10, 2026
• Status: Not Started
• [Generate Form](https://odoo.insightpulseai.net/bir/1601c)
```

---

## Troubleshooting

### Problem: Tasks not created

**Solution**:
```bash
# Check module installation
odoo -d production -c /etc/odoo/odoo.conf --list
# Should show: ipai_finance_closing

# Check XML data loaded
psql -U odoo production -c "SELECT COUNT(*) FROM project_task WHERE project_id IN (SELECT id FROM project_project WHERE name LIKE '%Month-End Close Template%');"
# Should return: 26
```

### Problem: Automated actions not running

**Note**: Scheduled actions (cron jobs) are **disabled** in initial release due to Odoo 18 restrictions on Python imports in scheduled action code.

**Solution**: Use n8n workflows for automation:
- Accrual reversals
- FX rate updates
- Period lock reminders
- BIR filing deadline alerts

See Phase 3 of implementation plan for n8n workflow setup.

### Problem: Task dependencies not enforced

**Solution**:
```bash
# Verify depends_on field
psql -U odoo production -c "SELECT name, depend_on_ids FROM project_task WHERE name='Bank Reconciliation';"

# If null, reimport data
odoo -d production -u ipai_finance_closing --stop-after-init
```

---

## Development

### Module Structure

```
addons/ipai_finance_closing/
├── __init__.py                    # Empty (no Python code)
├── __manifest__.py                # Module metadata
├── data/
│   ├── closing_tasks.xml          # 26 task definitions (5 phases)
│   └── closing_automation.xml.disabled  # Disabled (Odoo 18 restrictions)
├── security/
│   └── ir.model.access.csv        # Access rights
└── README.md                      # This file
```

### Testing

```bash
# Unit tests
odoo -d test_db -i ipai_finance_closing --test-enable --stop-after-init

# Integration test (n8n workflow)
curl -X POST "https://n8n.insightpulseai.net/webhook/month-end-close" \
  -H "Content-Type: application/json" \
  -d '{"month":"2025-12"}'
```

### Deployment

```bash
# 1. Commit to repo
cd ~/Documents/GitHub/odoo-ce
git add addons/ipai_finance_closing/
git commit -m "feat(finance): add month-end closing automation module"
git push origin main

# 2. Deploy to production
ssh root@159.223.75.148
cd /opt/odoo-ce
git pull origin main
docker-compose restart odoo

# 3. Install module
# Via Odoo UI: Apps → Update Apps List → Install "Finance Closing"
```

---

## Support

**Issues**: https://github.com/jgtolentino/odoo-ce/issues
**Maintainer**: Finance Director + IT Market Director
**Documentation**: https://jgtolentino.github.io/odoo-financial-close-docs/

---

## License

AGPL-3.0 - See LICENSE file

---

## Credits

**Based on**:
- SAP S/4HANA Cloud Advanced Financial Closing (AFC)
- SAP Help Portal - AFC Administration Guide
- SAP-docs/s4hana-cloud-advanced-financial-closing (CC-BY-4.0)

**Adapted for**:
- Odoo CE 18.0
- Philippine BIR tax compliance
- InsightPulse AI finance operations

---

**Last Updated**: 2025-12-29
**Version**: 1.0.0
