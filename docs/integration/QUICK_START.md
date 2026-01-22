# IPAI Integration Bus - Quick Start (5 Minutes)

**Goal**: Get expense → Mattermost notification working end-to-end

---

## Prerequisites

- Supabase CLI installed: `brew install supabase/tap/supabase`
- n8n running: https://n8n.insightpulseai.net
- Mattermost webhook URL configured
- Odoo CE 18.0 running (local or production)

---

## Step 1: Deploy Supabase (2 minutes)

```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce

# Link project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Deploy everything (migrations + Edge Function + secrets)
./scripts/integration/deploy-supabase.sh
```

**Copy the generated `ODOO_WEBHOOK_SECRET` from output!**

---

## Step 2: Configure Odoo (1 minute)

**Via UI** (Settings → Technical → System Parameters → Create):

| Key | Value |
|-----|-------|
| `ipai.webhook.url` | `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook` |
| `ipai.webhook.secret` | `<PASTE SECRET FROM STEP 1>` |

**Via CLI** (faster):
```bash
docker compose exec odoo-core odoo shell -d odoo_core << 'EOF'
env['ir.config_parameter'].sudo().set_param('ipai.webhook.url', 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook')
env['ir.config_parameter'].sudo().set_param('ipai.webhook.secret', 'PASTE_SECRET_HERE')
env.cr.commit()
EOF
```

---

## Step 3: Test Webhook (30 seconds)

```bash
export SUPABASE_FUNCTION_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook"
export ODOO_WEBHOOK_SECRET="<PASTE SECRET>"

# Send test expense event
./scripts/integration/test-webhook.py expense.submitted
```

**Expected**: `✅ expense.submitted`

**Verify in Supabase**:
```bash
supabase db query "SELECT event_type, status FROM integration.outbox ORDER BY created_at DESC LIMIT 1;"
```

---

## Step 4: Import n8n Event Router (1 minute)

1. Open n8n: https://n8n.insightpulseai.net
2. Workflows → Import from File
3. Select: `n8n/workflows/integration/event-router.json`
4. Configure Supabase credential:
   - URL: `https://spdtwktxdalcfigzeqrz.supabase.co`
   - Service Role Key: (from Supabase dashboard → Settings → API)
5. Save → Activate

---

## Step 5: Verify End-to-End (30 seconds)

**Test via Python** (simulates Odoo):
```bash
./scripts/integration/test-webhook.py expense.submitted
```

**Check Supabase Outbox**:
```bash
supabase db query "SELECT event_type, status FROM integration.outbox ORDER BY created_at DESC LIMIT 5;"
```

**Expected**:
```
event_type          | status
--------------------+--------
expense.submitted   | done
```

If `status = 'pending'`, wait 30 seconds for n8n to claim it.
If `status = 'processing'` for >5 minutes, check n8n logs.

---

## Next Steps (Optional)

### Add Real Odoo Emission

Edit `addons/hr_expense/models/hr_expense.py`:

```python
# Add at top
from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event
import logging
_logger = logging.getLogger(__name__)

# In HrExpense class
def action_submit_expenses(self):
    res = super().action_submit_expenses()

    # Get webhook config
    webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
    webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

    if not webhook_url or not webhook_secret:
        return res

    # Emit event
    for expense in self:
        event = {
            "event_type": "expense.submitted",
            "aggregate_type": "expense",
            "aggregate_id": str(expense.id),
            "payload": {
                "expense_id": expense.id,
                "employee_name": expense.employee_id.name,
                "amount": float(expense.total_amount),
                "currency": expense.currency_id.name,
                "description": expense.name,
            }
        }
        try:
            send_ipai_event(webhook_url, webhook_secret, event)
            _logger.info(f"Emitted expense.submitted event for expense #{expense.id}")
        except Exception as e:
            _logger.error(f"Failed to emit event: {e}")

    return res
```

Restart Odoo:
```bash
docker compose restart odoo-core
```

### Import Expense Handler Workflow

1. Create `n8n/workflows/integration/expense-handler.json` (see EVENT_TAXONOMY.md for spec)
2. Import in n8n
3. Configure Mattermost webhook
4. Activate workflow

---

## Troubleshooting

**Event stuck in `pending`**:
- Check n8n event router is active
- Verify Supabase credentials in n8n
- Check n8n execution logs for errors

**Event stuck in `processing`**:
- Wait 10 minutes (auto-unlock)
- Manual reset: `UPDATE integration.outbox SET status='pending', locked_at=NULL WHERE id='...';`

**Event in `dead` state**:
- Check `last_error` field
- Fix root cause
- Reset: `UPDATE integration.outbox SET status='pending', attempts=0 WHERE id='...';`

**HMAC signature error**:
- Verify `ODOO_WEBHOOK_SECRET` matches in:
  - Supabase secrets: `supabase secrets list`
  - Odoo system parameter: `ipai.webhook.secret`
  - Test script: `$ODOO_WEBHOOK_SECRET`

---

**Total Time**: ~5 minutes
**Status**: Production Ready
**Support**: See docs/integration/README.md for complete guide
