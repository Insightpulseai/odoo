# Spec 003: AI Enrichment Agent - Deployment Guide

**Goal**: Automatically enrich Odoo contacts with AI-generated industry tags and summaries

---

## Architecture Overview

```
Odoo Contact Created
   ↓ (Automated Action)
n8n Webhook Listener
   ↓
GPT-4o Mini (AI Analyst)
   ↓
Search/Create Industry Tag
   ↓
Update Contact (Tag + Summary)
   ↓
Mattermost Notification (optional)
```

---

## Prerequisites

### 1. OpenAI API Key

**Get API Key**:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-...`)

**Add to n8n**:
1. Open n8n → Settings → Credentials
2. Click "Create New Credential"
3. Select "OpenAI API"
4. **Name**: `OpenAI GPT-4o Mini`
5. **API Key**: Paste your key
6. Save

**Cost Estimate**:
- GPT-4o Mini: ~$0.00015 per contact
- 1,000 contacts/month = $0.15
- Extremely affordable for CRM enrichment

### 2. n8n Odoo Credential (Already Created)

Should already exist from previous webhooks:
- **Name**: `Odoo Production (erp.insightpulseai.com)`
- **URL**: `https://erp.insightpulseai.com`
- **Database**: `production`

---

## Deployment Steps

### Step 1: Import Workflow to n8n

```bash
# Upload workflow to n8n server (if remote)
scp workflows/n8n_enrichment_agent.json root@<n8n-server>:/tmp/

# Or import via n8n UI:
# 1. Open n8n (https://ipa.insightpulseai.com)
# 2. Click "Add Workflow" → "Import from File"
# 3. Select n8n_enrichment_agent.json
# 4. Update credentials:
#    - AI Analyst node → Select OpenAI credential
#    - Search Tag, Create Tag, Update Contact → Select Odoo credential
# 5. Click "Save"
# 6. Toggle "Active" switch
```

### Step 2: Configure Odoo Automated Action

**Via Odoo UI**:

1. Open Odoo: `https://erp.insightpulseai.com/web`
2. Enable Developer Mode (Settings → Activate Developer Mode)
3. Navigate to: **Settings → Technical → Automation → Automated Actions**
4. Click **Create**
5. Configure:

```
Name: Trigger AI Enrichment
Model: Contact (res.partner)
Trigger: On Creation
Apply On: (leave empty to apply to all new contacts)
Action To Do: Execute Python Code
```

6. In the **Python Code** tab, paste:

```python
# SHADOW ENTERPRISE: AI ENRICHMENT PROTOCOL
import requests

webhook_url = "https://ipa.insightpulseai.com/webhook/enrich-contact"

payload = {
    "id": record.id,
    "name": record.name,
    "email": record.email or "",
    "website": record.website or ""
}

try:
    requests.post(webhook_url, json=payload, timeout=1)
except requests.exceptions.Timeout:
    pass  # Expected for async processing
except Exception as e:
    env['ir.logging'].sudo().create({
        'name': 'AI Enrichment Error',
        'type': 'server',
        'level': 'warning',
        'message': str(e),
        'path': 'res.partner',
        'func': 'create',
        'line': '0'
    })
```

7. Click **Save**

**Via Docker/CLI** (Alternative):

```bash
# Create automated action via Odoo shell
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])

with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})

    # Check if action already exists
    existing = env['ir.actions.server'].search([('name', '=', 'Trigger AI Enrichment')], limit=1)

    if not existing:
        # Create automated action
        action = env['ir.actions.server'].create({
            'name': 'Trigger AI Enrichment',
            'model_id': env.ref('base.model_res_partner').id,
            'state': 'code',
            'code': '''import requests
webhook_url = \"https://ipa.insightpulseai.com/webhook/enrich-contact\"
payload = {\"id\": record.id, \"name\": record.name, \"email\": record.email or \"\", \"website\": record.website or \"\"}
try:
    requests.post(webhook_url, json=payload, timeout=1)
except:
    pass'''
        })

        # Create trigger rule
        env['base.automation'].create({
            'name': 'AI Enrichment Trigger',
            'model_id': env.ref('base.model_res_partner').id,
            'trigger': 'on_create',
            'action_server_id': action.id,
            'active': True
        })

        cr.commit()
        print('✅ Automated action created')
    else:
        print('ℹ️ Automated action already exists')
\""
```

---

## Testing

### Test 1: Create Contact Manually

1. Open Odoo → Contacts → Create
2. Fill in:
   - **Name**: Test Company
   - **Email**: hello@microsoft.com
   - **Website**: https://www.microsoft.com
3. Click **Save**
4. Wait 5 seconds
5. Check **Internal Notes** → Should show AI summary
6. Check **Tags** → Should show "Technology" tag

### Test 2: Test via n8n Directly

```bash
curl -X POST https://ipa.insightpulseai.com/webhook/enrich-contact \
  -H "Content-Type: application/json" \
  -d '{
    "id": 999,
    "name": "Test Logistics Co",
    "email": "info@dhl.com",
    "website": "https://www.dhl.com"
  }'
```

**Expected n8n Execution**:
1. AI Analyst identifies industry: "Logistics"
2. Search Tag finds/creates "Logistics" tag
3. Update Contact adds tag and summary

### Test 3: Verify in Odoo

```bash
# Check if contact was enriched
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])

with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    contact = env['res.partner'].browse(999)
    print(f'Name: {contact.name}')
    print(f'Tags: {[tag.name for tag in contact.category_id]}')
    print(f'Summary: {contact.comment}')
\""
```

---

## Industry Tag Examples

AI will automatically create these tags based on email domains:

- **Technology**: microsoft.com, google.com, apple.com
- **Finance**: jpmorgan.com, hsbc.com, citibank.com
- **Healthcare**: mayoclinic.org, kp.org, uhc.com
- **Retail**: walmart.com, target.com, amazon.com
- **Agency**: ogilvy.com, wpp.com, publicis.com
- **Logistics**: dhl.com, fedex.com, ups.com
- **Education**: harvard.edu, mit.edu, stanford.edu
- **Telecommunications**: verizon.com, att.com, tmobile.com

---

## Monitoring

### Check n8n Execution History

1. Open n8n workflow
2. Click **Executions** tab
3. View execution logs with:
   - Input payload (contact data)
   - AI response (industry + summary)
   - Odoo update status

### Check Odoo Logs

```bash
# View AI enrichment logs
ssh root@159.223.75.148 "docker logs odoo-ce 2>&1 | grep -i 'AI Enrichment' | tail -20"

# Check for errors
ssh root@159.223.75.148 "docker exec odoo-ce python3 -c \"
import odoo
odoo.tools.config['db_name'] = 'production'
odoo.service.server.preload_registries(['production'])

with odoo.registry('production').cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    logs = env['ir.logging'].search([('name', 'ilike', 'AI Enrichment')], limit=10, order='create_date desc')
    for log in logs:
        print(f'{log.create_date} | {log.level} | {log.message}')
\""
```

---

## Advanced Enhancements

### 1. Add Mattermost Notification

After "Update Contact" node in n8n, add:

```json
{
  "name": "Notify Mattermost",
  "type": "n8n-nodes-base.mattermost",
  "parameters": {
    "channel": "#crm-updates",
    "text": "🤖 AI enriched contact: {{ $node['Webhook Listener'].json.body.name }} → {{ JSON.parse($node['AI Analyst'].json.content).industry }}"
  }
}
```

### 2. Add Confidence Threshold

Modify AI Analyst prompt:

```
Analyze the email domain '{{ $json.body.email }}' or website '{{ $json.body.website }}'.

1. Identify the Industry with confidence (0-100%)
2. Only return if confidence >= 70%

Return JSON:
{
  "industry": "Technology",
  "confidence": 95,
  "summary": "A multinational technology company."
}
```

Add IF node after AI Analyst:
```
Condition: {{ JSON.parse($json.content).confidence >= 70 }}
```

### 3. Enrich Existing Contacts (Batch)

Create scheduled n8n workflow:

1. **Schedule Trigger**: Daily at 2 AM
2. **Get Contacts**: Search Odoo for contacts without tags
3. **Loop**: Process 50 contacts per day
4. **Enrich**: Same AI enrichment flow

---

## Troubleshooting

**Issue**: AI returns invalid JSON
**Fix**: Add error handling in n8n with Function node:
```javascript
try {
  const parsed = JSON.parse($json.content);
  return { json: parsed };
} catch (e) {
  return { json: { industry: "Unknown", summary: "Could not determine industry" } };
}
```

**Issue**: Odoo webhook times out
**Fix**: Already handled with 1s timeout and exception catching

**Issue**: Too many API calls
**Fix**: Add filter in Odoo automation:
```python
# Only enrich if email domain is not @gmail.com, @yahoo.com, etc.
if record.email and not any(domain in record.email for domain in ['gmail.com', 'yahoo.com', 'hotmail.com']):
    # ... send to webhook
```

---

## Cost Analysis

**OpenAI GPT-4o Mini Pricing**:
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens
- Average prompt: ~100 tokens
- Average response: ~50 tokens
- **Cost per contact**: ~$0.00015 (less than 1/100th of a cent)

**Monthly Cost Examples**:
- 100 contacts/month: $0.015
- 1,000 contacts/month: $0.15
- 10,000 contacts/month: $1.50

**ROI**: Even at 10,000 contacts/month, the $1.50 AI cost is negligible compared to manual tagging labor (estimated 5-10 hours @ $50/hr = $250-500 saved).

---

## Success Criteria

- [x] Spec 003 documented
- [ ] n8n workflow imported and activated
- [ ] OpenAI credential configured
- [ ] Odoo automated action created
- [ ] Test contact enriched successfully
- [ ] AI tags created automatically
- [ ] Summaries appear in Internal Notes

---

## Next Steps

1. **Deploy to production** (follow steps above)
2. **Monitor first 100 enrichments** for accuracy
3. **Add vendor/customer classification** (separate AI prompt)
4. **Integrate with email marketing** (auto-segment by industry)
5. **Create industry-specific workflows** (e.g., Finance → Send pricing for accounting services)

---

**Documentation**: `/Users/tbwa/odoo-ce/specs/003-ai-enrichment/`
**Workflow File**: `/Users/tbwa/odoo-ce/workflows/n8n_enrichment_agent.json`
**Contact**: Jake Tolentino (TBWA Finance SSC / InsightPulse AI)
