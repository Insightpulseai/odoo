# Shadow Enterprise Webhook & AI Stack

**Complete n8n + Odoo CE Integration replacing Odoo Enterprise features**

---

## Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHADOW ENTERPRISE STACK                      │
│                    (Odoo CE 18 + n8n + AI)                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   External   │ ────→   │     n8n      │ ────→   │  Odoo CE 18  │
│   Systems    │ Webhook │  Interceptor │  Action │    (ERP)     │
└──────────────┘         └──────────────┘         └──────────────┘
                               │
                               ↓
                         ┌──────────────┐
                         │   AI Layer   │
                         │  GPT-4o Mini │
                         └──────────────┘
                               │
                               ↓
                         ┌──────────────┐
                         │   Supabase   │
                         │  (Analytics) │
                         └──────────────┘
                               │
                               ↓
                         ┌──────────────┐
                         │  Mattermost  │
                         │ (Alerts)     │
                         └──────────────┘
```

---

## Components

### 1. Inbound Webhooks (External → Odoo)

**Purpose**: Receive data from external systems and automate Odoo operations

| Workflow | Trigger | Action | Cost |
|----------|---------|--------|------|
| **OCR Expense** | OCR service completes | Auto-create expense in Odoo | Free |
| **BIR Deadline** | Calendar reminder | Create task + alert team | Free |
| **Scout Sync** | Transaction data updated | ETL to Supabase Bronze | Free |
| **AI Enrichment** | New contact created | Classify industry + tag | $0.00015/contact |

**Files**:
- `workflows/n8n_ocr_expense_webhook.json`
- `workflows/n8n_bir_deadline_webhook.json`
- `workflows/n8n_scout_sync_webhook.json`
- `workflows/n8n_enrichment_agent.json`

### 2. Outbound Automations (Odoo → External)

**Purpose**: Send data FROM Odoo when records change

**Configured in Odoo**: Settings → Technical → Automation → Automated Actions

**Example Triggers**:
- Expense approved → Notify Mattermost
- Invoice created → Sync to Supabase
- Task completed → Update project tracker
- Contact created → AI enrichment (via n8n)

**Code Pattern**:
```python
import requests
webhook_url = "https://ipa.insightpulseai.com/webhook/<endpoint>"
payload = {"id": record.id, "data": record.field}
try:
    requests.post(webhook_url, json=payload, timeout=1)
except:
    pass  # Don't crash Odoo if webhook fails
```

### 3. AI Intelligence Layer

**Purpose**: Add GPT-4o Mini intelligence to CRM and business processes

**Current Implementation**: Spec 003 - AI CRM Enrichment
- Auto-classify contacts by industry
- Generate company summaries
- Create/assign tags automatically
- Cost: ~$0.00015 per contact

**Future Capabilities**:
- Expense categorization (OCR confidence boost)
- Email sentiment analysis
- Invoice fraud detection
- Predictive cash flow modeling

---

## Feature Comparison: Shadow Enterprise vs Odoo Enterprise

| Feature | Odoo Enterprise | Shadow Enterprise (CE + n8n) | Savings |
|---------|----------------|------------------------------|---------|
| **Webhooks** | Built-in UI | n8n visual workflows | $0 |
| **AI Studio** | $600/mo | GPT-4o Mini ($1.50/10k contacts) | ~$598/mo |
| **Advanced Analytics** | $300/mo | Supabase + Superset | $300/mo |
| **Automation** | Limited | Unlimited via n8n | $0 |
| **Total Monthly** | ~$900/mo | ~$10/mo | **$890/mo saved** |
| **Annual Savings** | - | - | **$10,680/year** |

---

## Deployment Locations

### n8n Instance
- **URL**: https://ipa.insightpulseai.com
- **Workflows**: 4 active
- **Credentials**: Odoo, Supabase, Mattermost, OpenAI

### Odoo CE 18
- **URL**: https://erp.insightpulseai.com
- **Database**: production
- **Automated Actions**: 1 (AI Enrichment trigger)

### Supabase
- **URL**: https://xkxyvboeubffxxbebsll.supabase.co
- **Tables**: scout_transactions_bronze, scout_etl_sync_log
- **Functions**: Bronze → Silver data quality pipeline

### Mattermost
- **URL**: https://ipa.insightpulseai.com
- **Channels**: #finance-alerts, #finance-tasks, #finance-data, #crm-updates

---

## Webhook URLs

### Production Endpoints

```bash
# Inbound Webhooks (External → n8n → Odoo)
OCR_EXPENSE_URL="https://ipa.insightpulseai.com/webhook/ocr-expense"
BIR_DEADLINE_URL="https://ipa.insightpulseai.com/webhook/bir-deadline"
SCOUT_SYNC_URL="https://ipa.insightpulseai.com/webhook/scout-sync"
AI_ENRICHMENT_URL="https://ipa.insightpulseai.com/webhook/enrich-contact"

# Outbound Webhooks (Odoo → n8n → External)
EXPENSE_APPROVED_URL="https://ipa.insightpulseai.com/webhook/expense-approved"
INVOICE_CREATED_URL="https://ipa.insightpulseai.com/webhook/invoice-created"
```

### Test Commands

```bash
# Test OCR Expense (High Confidence)
curl -X POST $OCR_EXPENSE_URL \
  -H "Content-Type: application/json" \
  -d '{"vendor_name":"SM","amount":1250.50,"confidence":0.87,"receipt_id":"REC-001","employee_id":4}'

# Test BIR Deadline (Urgent)
curl -X POST $BIR_DEADLINE_URL \
  -H "Content-Type: application/json" \
  -d '{"bir_form":"1601-C","deadline":"2025-12-10","period":"November 2025"}'

# Test Scout Sync (Multi-Transaction)
curl -X POST $SCOUT_SYNC_URL \
  -H "Content-Type: application/json" \
  -d '{"employee_code":"RIM","transactions":[{"id":"TXN-001","date":"2025-11-20","vendor":"Office Depot","amount":2500.00}]}'

# Test AI Enrichment
curl -X POST $AI_ENRICHMENT_URL \
  -H "Content-Type: application/json" \
  -d '{"id":999,"name":"Test Company","email":"info@microsoft.com","website":"https://www.microsoft.com"}'
```

---

## Architecture Benefits

### 1. Security
- **n8n as Firewall**: External systems never touch Odoo directly
- **Authentication**: Basic auth, API keys, header validation
- **IP Whitelisting**: n8n can restrict webhook sources

### 2. Resilience
- **Async Processing**: Odoo doesn't wait for external responses
- **Error Isolation**: Webhook failures don't crash Odoo
- **Retry Logic**: n8n handles retries automatically
- **Logging**: Full execution history in n8n UI

### 3. Flexibility
- **Visual Workflows**: No coding required for changes
- **Multi-System**: Connect ANY external system
- **Transformation**: Clean dirty data before Odoo ingestion
- **Orchestration**: Chain multiple operations

### 4. Cost Efficiency
- **Open Source**: Odoo CE + n8n = $0 base cost
- **Pay-per-Use AI**: GPT-4o Mini = $0.00015/contact
- **No Vendor Lock-In**: Full control over infrastructure
- **Scalable**: Handles 10k+ operations/month easily

---

## Monitoring Dashboard (Recommended)

**Create in n8n**:

### Webhook Health Check (Scheduled)

```json
{
  "name": "Daily Webhook Health Check",
  "trigger": "Schedule (Daily 8 AM)",
  "nodes": [
    "Test OCR Endpoint",
    "Test BIR Endpoint",
    "Test Scout Endpoint",
    "Test AI Endpoint",
    "Aggregate Results",
    "Send Report to Mattermost"
  ]
}
```

### Execution Metrics

**Track in Supabase**:
```sql
CREATE TABLE webhook_metrics (
  date DATE,
  endpoint VARCHAR(50),
  total_calls INT,
  successful INT,
  failed INT,
  avg_response_time_ms INT
);
```

**Daily Report** (n8n → Mattermost):
```
📊 Webhook Health Report (2025-11-26)

✅ OCR Expense: 45 calls, 100% success, 1.2s avg
✅ BIR Deadline: 3 calls, 100% success, 0.8s avg
✅ Scout Sync: 12 calls, 100% success, 2.5s avg
🤖 AI Enrichment: 28 calls, 96% success, 3.1s avg

⚠️ 1 AI enrichment failed (invalid email domain)
```

---

## Maintenance Tasks

### Weekly
- [ ] Review n8n execution logs for errors
- [ ] Check Mattermost notifications for anomalies
- [ ] Verify Supabase Bronze layer data quality

### Monthly
- [ ] Analyze webhook usage patterns
- [ ] Review OpenAI API costs (should be <$2/mo)
- [ ] Update n8n workflows if needed
- [ ] Backup n8n workflow JSON files

### Quarterly
- [ ] Full system health check
- [ ] Review automation rules in Odoo
- [ ] Optimize slow-running workflows
- [ ] Update deployment documentation

---

## Troubleshooting Guide

### Issue: Webhook Returns 404

**Symptoms**: External system gets 404 Not Found

**Diagnosis**:
```bash
# Check if workflow is activated in n8n
curl -I https://ipa.insightpulseai.com/webhook/ocr-expense
```

**Fix**:
1. Open n8n workflow
2. Ensure "Active" toggle is ON
3. Re-save workflow to regenerate URL

### Issue: Odoo Automation Not Triggering

**Symptoms**: New contacts created but no AI enrichment

**Diagnosis**:
```bash
# Check automated action exists
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])
with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    actions = env['base.automation'].search([('name', 'ilike', 'AI Enrichment')])
    for action in actions:
        print(f'{action.name} | Active: {action.active} | Trigger: {action.trigger}')
\""
```

**Fix**:
1. Check automation is Active
2. Verify trigger is "on_create"
3. Check Python code has no syntax errors

### Issue: GPT-4o Mini Returns Errors

**Symptoms**: AI Analyst node fails in n8n

**Diagnosis**: Check n8n execution logs for OpenAI error

**Common Fixes**:
- **401 Unauthorized**: Invalid API key → Re-enter in n8n credentials
- **429 Rate Limit**: Too many requests → Add delay node
- **Invalid JSON**: Prompt needs refinement → Update prompt template

### Issue: Supabase Insert Fails

**Symptoms**: Scout sync fails at Bronze layer insert

**Diagnosis**:
```bash
# Check table exists
psql "$SUPABASE_URL" -c "SELECT * FROM scout_transactions_bronze LIMIT 1;"
```

**Fix**:
1. Verify table schema matches payload fields
2. Check Service Role Key has INSERT permissions
3. Review RLS policies (may block inserts)

---

## Security Best Practices

### 1. Webhook Authentication

**Add to n8n Webhook Nodes**:
```json
{
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-API-Key",
    "value": "{{ $env.WEBHOOK_SECRET }}"
  }
}
```

**External System**:
```bash
curl -X POST $WEBHOOK_URL \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 2. Rate Limiting

**Add to n8n** (Throttle node):
```json
{
  "name": "Rate Limiter",
  "type": "n8n-nodes-base.throttle",
  "parameters": {
    "rate": 100,
    "interval": "minute"
  }
}
```

### 3. Input Validation

**Add after Webhook Listener**:
```javascript
// Function node: Validate Input
const payload = $json.body;

// Required fields check
const required = ['id', 'email', 'name'];
for (const field of required) {
  if (!payload[field]) {
    throw new Error(`Missing required field: ${field}`);
  }
}

// Email format validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(payload.email)) {
  throw new Error('Invalid email format');
}

return { json: payload };
```

---

## Future Enhancements

### Phase 2: Advanced AI Features
- [ ] Expense fraud detection (anomaly detection)
- [ ] Email sentiment analysis (customer support)
- [ ] Invoice duplicate detection
- [ ] Predictive analytics for cash flow

### Phase 3: Multi-Modal AI
- [ ] Receipt image analysis (GPT-4 Vision)
- [ ] Document classification
- [ ] Signature verification
- [ ] Handwriting OCR

### Phase 4: Advanced ETL
- [ ] Silver layer data quality rules
- [ ] Gold layer analytics marts
- [ ] Platinum layer ML features
- [ ] Real-time dashboards (Superset)

---

## Documentation Index

```
odoo-ce/
├── workflows/
│   ├── n8n_ocr_expense_webhook.json
│   ├── n8n_bir_deadline_webhook.json
│   ├── n8n_scout_sync_webhook.json
│   ├── n8n_enrichment_agent.json
│   ├── WEBHOOK_DEPLOYMENT_GUIDE.md
│   └── SHADOW_ENTERPRISE_STACK.md (this file)
├── specs/
│   └── 003-ai-enrichment/
│       ├── spec.md
│       ├── DEPLOYMENT.md
│       └── odoo_automation_action.py
└── addons/
    └── ipai_portal_fix/  (bonus: portal KeyError fix)
```

---

## Support & Contact

**Stack Owner**: Jake Tolentino (TBWA Finance SSC / InsightPulse AI)
**Email**: jake.tolentino@insightpulseai.com
**Repository**: `/Users/tbwa/odoo-ce/`
**n8n Instance**: https://ipa.insightpulseai.com
**Odoo Instance**: https://erp.insightpulseai.com

---

## Quick Start Commands

```bash
# Upload all workflows to n8n server
scp workflows/n8n_*.json root@<n8n-server>:/tmp/

# Test all webhooks
bash workflows/test_all_webhooks.sh

# Check Odoo automation status
ssh root@159.223.75.148 "docker exec odoo-ce python3 /tmp/check_automations.py"

# View execution logs
ssh root@159.223.75.148 "docker logs odoo-ce --tail 50 | grep -i webhook"
```

---

**Last Updated**: 2025-11-26
**Version**: 1.0.0
**Status**: Production Ready ✅
