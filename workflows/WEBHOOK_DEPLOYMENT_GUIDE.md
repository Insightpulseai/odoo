# n8n Webhook Deployment Guide - TBWA Finance SSC

**Stack**: Odoo CE 18 + n8n (ipa.insightpulseai.com) + Supabase + Mattermost

---

## Overview

This guide covers deploying 3 production-ready n8n webhooks for TBWA Finance SSC operations:

1. **OCR Expense Webhook** - Auto-create expenses from OCR results
2. **BIR Deadline Webhook** - Alert system for tax filing deadlines
3. **Scout Sync Webhook** - ETL pipeline to Supabase Bronze layer

---

## Prerequisites

### n8n Credentials Setup

Before importing workflows, create these credentials in n8n:

#### 1. Odoo API Credential
- **Name**: `Odoo Production (erp.insightpulseai.com)`
- **URL**: `https://erp.insightpulseai.com`
- **Database**: `production`
- **Username**: Your Odoo admin email
- **Password**: Your Odoo password

#### 2. Supabase API Credential
- **Name**: `Supabase (xkxyvboeubffxxbebsll)`
- **Host**: `https://xkxyvboeubffxxbebsll.supabase.co`
- **Service Role Key**: (from `~/.zshrc` → `$SUPABASE_SERVICE_ROLE_KEY`)

#### 3. Mattermost API Credential
- **Name**: `Mattermost (ipa.insightpulseai.com)`
- **Base URL**: `https://ipa.insightpulseai.com`
- **Access Token**: (from Mattermost → Integrations → Bot Accounts)

### Environment Variables (n8n)

Set these in n8n Settings → Variables:

```bash
FINANCE_PPM_PROJECT_ID=<project_id>         # From Odoo Finance PPM project
FINANCE_SUPERVISOR_USER_ID=<user_id>        # BOM's Odoo user ID
BIR_TASK_TAG_ID=<tag_id>                    # "BIR Filing" tag ID
```

To find these IDs:
```bash
# Get Finance PPM project ID
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])
with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    project = env['project.project'].search([('name', 'ilike', 'Finance PPM')], limit=1)
    print(f'FINANCE_PPM_PROJECT_ID={project.id}')
\""

# Get BOM user ID (Finance Supervisor)
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])
with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    user = env['res.users'].search([('login', 'ilike', 'beng')], limit=1)
    print(f'FINANCE_SUPERVISOR_USER_ID={user.id}')
\""
```

---

## Deployment Steps

### 1. Import Workflows to n8n

```bash
# Upload workflow JSON files to n8n server
scp workflows/n8n_*.json root@<n8n-server>:/tmp/

# Import via n8n UI:
# 1. Open n8n (https://ipa.insightpulseai.com)
# 2. Click "Workflows" → "Import from File"
# 3. Select each JSON file
# 4. Update credentials to match your setup
# 5. Activate workflow (toggle switch)
```

### 2. Get Webhook URLs

After importing, each workflow will have a unique URL:

**Format**: `https://ipa.insightpulseai.com/webhook/<path>`

Example URLs:
- **OCR Expense**: `https://ipa.insightpulseai.com/webhook/ocr-expense`
- **BIR Deadline**: `https://ipa.insightpulseai.com/webhook/bir-deadline`
- **Scout Sync**: `https://ipa.insightpulseai.com/webhook/scout-sync`

---

## Test Payloads

### 1. OCR Expense Webhook

**High Confidence (Auto-Create)**:
```bash
curl -X POST https://ipa.insightpulseai.com/webhook/ocr-expense \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "SM Supermarket",
    "amount": 1250.50,
    "date": "2025-11-25",
    "confidence": 0.87,
    "receipt_id": "REC-2025-001",
    "employee_id": 4,
    "category_id": 1
  }'
```

**Expected Response**:
```json
{
  "status": "ok",
  "expense_id": 42,
  "message": "Expense created successfully"
}
```

**Low Confidence (Review Required)**:
```bash
curl -X POST https://ipa.insightpulseai.com/webhook/ocr-expense \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Unknown Vendor",
    "amount": 500.00,
    "date": "2025-11-25",
    "confidence": 0.45,
    "receipt_id": "REC-2025-002",
    "employee_id": 4
  }'
```

**Expected Response**:
```json
{
  "status": "review",
  "message": "Low confidence - manual review required",
  "task_id": 123
}
```

### 2. BIR Deadline Webhook

**Urgent Deadline (≤7 days)**:
```bash
curl -X POST https://ipa.insightpulseai.com/webhook/bir-deadline \
  -H "Content-Type: application/json" \
  -d '{
    "bir_form": "1601-C",
    "deadline": "2025-12-10",
    "period": "November 2025"
  }'
```

**Expected Response**:
```json
{
  "status": "ok",
  "task_id": 456,
  "message": "BIR task created successfully"
}
```

**Standard Deadline (>7 days)**:
```bash
curl -X POST https://ipa.insightpulseai.com/webhook/bir-deadline \
  -H "Content-Type: application/json" \
  -d '{
    "bir_form": "2550Q",
    "deadline": "2026-02-28",
    "period": "Q4 2025"
  }'
```

### 3. Scout Sync Webhook

**Multi-Transaction Sync**:
```bash
curl -X POST https://ipa.insightpulseai.com/webhook/scout-sync \
  -H "Content-Type: application/json" \
  -d '{
    "employee_code": "RIM",
    "transactions": [
      {
        "id": "TXN-001",
        "date": "2025-11-20",
        "vendor": "Office Depot",
        "category": "Office Supplies",
        "amount": 2500.00,
        "currency": "PHP",
        "payment_method": "Corporate Card"
      },
      {
        "id": "TXN-002",
        "date": "2025-11-21",
        "vendor": "Grab",
        "category": "Transportation",
        "amount": 350.00,
        "currency": "PHP",
        "payment_method": "Cash"
      },
      {
        "id": "TXN-003",
        "date": "2025-11-22",
        "vendor": "Starbucks",
        "category": "Meals",
        "amount": 420.00,
        "currency": "PHP",
        "payment_method": "Personal"
      }
    ]
  }'
```

**Expected Response**:
```json
{
  "status": "ok",
  "synced": 3,
  "failed": 0,
  "message": "Scout transactions synced to Bronze layer"
}
```

---

## Odoo Outbound Automation (Odoo → n8n)

This automation sends data FROM Odoo TO an external webhook when a record changes.

### Example: Notify n8n when Expense is Approved

**Setup in Odoo**:

1. Go to **Settings → Technical → Automation → Automated Actions**
2. Click **Create**
3. Configure:

**Automated Action Configuration**:
```
Name: Send Expense Approval to n8n
Model: Expense (hr.expense)
Trigger: On Update
Apply On: state = 'approve'
Action: Execute Python Code
```

**Python Code**:
```python
import requests
import json

webhook_url = "https://ipa.insightpulseai.com/webhook/expense-approved"

payload = {
    "expense_id": record.id,
    "expense_name": record.name,
    "employee_code": record.employee_id.employee_code or 'Unknown',
    "amount": record.total_amount,
    "approval_date": fields.Date.today().isoformat(),
    "approved_by": env.user.name
}

try:
    response = requests.post(webhook_url, json=payload, timeout=5)
    if response.status_code == 200:
        env['ir.logging'].sudo().create({
            'name': 'Expense Approval Webhook',
            'type': 'server',
            'level': 'info',
            'message': f'Expense {record.id} notification sent successfully'
        })
except Exception as e:
    # Log error silently to avoid blocking user
    env['ir.logging'].sudo().create({
        'name': 'Expense Approval Webhook',
        'type': 'server',
        'level': 'error',
        'message': f'Webhook failed: {str(e)}'
    })
```

**n8n Workflow to Receive** (create this in n8n):
```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "expense-approved",
        "responseMode": "lastNode"
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "channel": "#finance-approvals",
        "text": "✅ Expense approved: {{ $json.body.expense_name }} ({{ $json.body.employee_code }}) - ${{ $json.body.amount }}"
      },
      "name": "Notify Mattermost",
      "type": "n8n-nodes-base.mattermost"
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [[{"node": "Notify Mattermost"}]]
    }
  }
}
```

---

## Monitoring & Troubleshooting

### Check Webhook Execution History in n8n

1. Open n8n → Click workflow name
2. View **Executions** tab
3. Check for failed executions (red indicators)

### Common Issues

**Issue**: `401 Unauthorized` from Odoo
**Fix**: Re-enter Odoo credentials in n8n, ensure password is correct

**Issue**: `404 Not Found` on webhook URL
**Fix**: Ensure workflow is **activated** (toggle switch on)

**Issue**: Supabase insert fails
**Fix**: Check table schema matches payload fields, verify Service Role Key

**Issue**: No Mattermost notifications
**Fix**: Verify bot token has permission to post in target channel

### Enable Logging

In each workflow, add a **Set** node after critical steps:
```json
{
  "name": "Log Data",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "mode": "manual",
    "values": {
      "log_timestamp": "={{ $now }}",
      "log_data": "={{ JSON.stringify($json) }}"
    }
  }
}
```

---

## Production Readiness Checklist

- [ ] All n8n credentials configured and tested
- [ ] Environment variables set in n8n
- [ ] All workflows imported and activated
- [ ] Test payloads sent successfully for each webhook
- [ ] Mattermost channels created (#finance-alerts, #finance-tasks, #finance-data)
- [ ] Odoo users have correct employee codes
- [ ] Finance PPM project exists with correct ID
- [ ] Supabase tables created (scout_transactions_bronze, scout_etl_sync_log)
- [ ] Webhook URLs documented in runbook
- [ ] Monitoring alerts configured

---

## Next Steps

1. **Schedule BIR Deadline Checks**: Create n8n scheduled workflow to check BIR calendar daily
2. **ETL Silver Layer**: Add n8n workflow to transform Bronze → Silver with data quality checks
3. **Dashboard Integration**: Connect Supabase to Apache Superset for real-time analytics
4. **Mobile Alerts**: Add SMS notifications for critical BIR deadlines via Twilio node

---

## Support

**Documentation**: `/Users/tbwa/odoo-ce/workflows/`
**n8n Instance**: https://ipa.insightpulseai.com
**Contact**: Jake Tolentino (TBWA Finance SSC / InsightPulse AI)
