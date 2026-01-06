# Odoo 18 CE + OCA + IPAI Go-Live Checklist (InsightPulseAI)

This checklist is for: Dockerized Odoo 18 CE on DO droplet + nginx reverse proxy + OCA modules + IPAI custom suite
and optional AI (OpenAI/Gemini) + OCR/Digitalization service.

---

## 0) Platform / Infra Health (must be ✅ before functional testing)

- [ ] Domain + TLS ok: https://erp.insightpulseai.net loads without mixed-content errors
- [ ] Odoo container healthy:
  - [ ] `docker ps` shows `odoo-erp-prod` running
  - [ ] `docker logs -n 200 odoo-erp-prod` shows no repeating tracebacks
- [ ] Outbound HTTPS from container works (for AI/OCR):
  - [ ] `curl -sS https://api.openai.com` (or gemini endpoint) returns a response (no DNS/egress block)
- [ ] Workers restart policy set; no crash loop
- [ ] Filestore volume mounted & writable

---

## 1) Critical Odoo 18 Compatibility Gate (prevents UI hard-stops)

### 1.1 Fix act_window view_mode breaking change (tree → list)

Odoo 18 renamed `tree` to `list` in view_mode. Legacy actions will fail with:
> "View types not defined tree found in act_window action ..."

- [ ] Run ORM fixer (module hook or script) to replace any `tree` in:
  - `ir.actions.act_window.view_mode`
  - action view definitions that still reference tree

**Fix options:**

```bash
# Option A: Upgrade the compat module (runs post-migrate automatically)
docker exec -it odoo-erp-prod bash -lc 'odoo -d odoo -u ipai_v18_compat --stop-after-init'
docker restart odoo-erp-prod

# Option B: Run standalone script
docker exec -it odoo-erp-prod bash -lc '
  export ODOO_DB=odoo
  export ODOO_CONF=/etc/odoo/odoo.conf
  python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py
'
docker restart odoo-erp-prod
```

### 1.2 Fix broken kanban views missing `t-name="card"`

Odoo 18 requires kanban views to have a `t-name="card"` template. Missing it triggers:
> "Missing 'card' template."

- [ ] Detect kanban views missing card template
- [ ] Either patch them (if you own the view) or deactivate them (safer)

**To auto-deactivate broken kanbans:**

```bash
# Set system parameter to enable deactivation
docker exec -it odoo-erp-prod bash -lc '
  odoo shell -d odoo <<PY
p = env["ir.config_parameter"].sudo()
p.set_param("ipai_v18_compat.deactivate_broken_kanban", "1")
print("set ipai_v18_compat.deactivate_broken_kanban=1")
env.cr.commit()
PY
'

# Then run the compat module upgrade
docker exec -it odoo-erp-prod bash -lc 'odoo -d odoo -u ipai_v18_compat --stop-after-init'
docker restart odoo-erp-prod
```

### 1.3 Verification

- [ ] No more client errors like:
  - "View types not defined tree found in act_window action …"
  - "Missing 'card' template."

```bash
# Check logs for remaining issues
docker logs -n 200 odoo-erp-prod | egrep -i "Missing .card.|View types not defined|Traceback" || echo "✓ No view errors found"
```

---

## 2) Email / Invites / Reset Password (Outbound-only baseline)

- [ ] Outgoing SMTP configured (Mailgun 2525 / TLS STARTTLS)
- [ ] Odoo test connection successful
- [ ] From filtering set (e.g. *@insightpulseai.net)
- [ ] Send test:
  - [ ] Invite user email arrives
  - [ ] Password reset email arrives
- [ ] No mail queue stuck: Settings → Technical → Emails

**Verification:**

```bash
# Check for email errors
docker logs -n 200 odoo-erp-prod | egrep -i "smtp|mail|email" | tail -20
```

---

## 3) AI Provider Configuration (Ask AI feature)

### 3.1 Provider Setup

- [ ] Settings → AI Provider Configuration
  - [ ] "Use your own ChatGPT account" enabled + key saved
  - [ ] "Use your own Google Gemini account" enabled + key saved
  - [ ] Model endpoint configured (if using DigitalOcean GenAI)

### 3.2 Verification

- [ ] Ask AI channel responds (Discuss → Ask AI)
- [ ] No provider errors in logs:

```bash
docker logs -n 200 odoo-erp-prod | egrep -i "ai|openai|gemini|http|traceback" | tail -20
```

### 3.3 DigitalOcean Model Endpoints (if applicable)

If using DO GenAI instead of direct OpenAI/Gemini:

- [ ] System Parameter `ipai.ai_endpoint_url` set to DO endpoint
- [ ] System Parameter `ipai.ai_api_key` set to DO API key
- [ ] Test completion works through DO proxy

---

## 4) Expenses + Document Digitalization (OCR) readiness

### 4.1 Core expenses flow

- [ ] Products exist for expense categories (Meals/Transpo/Misc/etc)
- [ ] Employee Expense Journal configured
- [ ] Payment modes correct ("Employee (to reimburse)" vs "Company")
- [ ] End-to-end:
  - [ ] Create expenses → Create report → Submit → Approve → Post journal entry

### 4.2 Incoming email expenses (optional)

- [ ] Alias configured (expense@insightpulseai.net)
- [ ] Email gateway routes to Odoo (inbound) OR disabled if out-of-scope

### 4.3 OCR / Receipt ingestion

Pick ONE:

**Option A: Use ipai_expense_ocr module (recommended)**

- [ ] Module `ipai_expense_ocr` installed
- [ ] Settings → Expenses → OCR Configuration:
  - [ ] OCR Backend selected (OpenAI Vision / Gemini Vision / Custom)
  - [ ] API keys configured
- [ ] Test: Upload receipt → "Extract from Receipt" button → fields populated

**Option B: Custom OCR microservice**

- [ ] Define endpoint + auth in System Parameters:
  - `ipai.ocr_endpoint_url`
  - `ipai.ocr_api_key`
- [ ] Upload receipt → OCR job → extracted fields mapped to expense

### 4.4 Evidence

- [ ] Upload receipt produces structured fields (date, merchant, amount)
- [ ] At least one receipt processed successfully

---

## 5) Accounting Go-Live (adapted from community checklist)

### A) Opening entries (accrual basis)

**Open invoices/bills:**

- [ ] Create AR Clearing (reconcilable current asset)
- [ ] Create AP Clearing (reconcilable current liability)
- [ ] Validate totals vs open AR/AP balances
- [ ] Import open invoices/credit notes
- [ ] Import open bills/refunds
- [ ] Reconcile clearing accounts to zero where expected

### B) Inventory (only if holding stock)

**Automated valuation:**

- [ ] Product categories configured (costing + valuation)
- [ ] Inventory clearing account configured
- [ ] Import on-hand quantities & validate stock valuation vs initial balance

**Manual valuation:**

- [ ] Ensure no stock valuation is expected on balance sheet

### C) Trial balance import

- [ ] Choose bank method:
  - [ ] Outstanding receipt/payment accounts (if using payment entries)
  - [ ] Bank clearing (if not)
- [ ] Modify trial balance to account for AR/AP/inventory clearing approach
- [ ] Post TB journal entry
- [ ] Validate clearing accounts (AR/AP/Inventory) are consistent

---

## 6) SCSS/CSS Asset Compilation (prevents "Style compilation failed")

- [ ] No "Style compilation failed" banner in UI
- [ ] CSS loads properly (check DevTools Network tab for 200 status)

**If asset compilation fails:**

```bash
# Diagnose
./scripts/odoo/diagnose_scss_error.sh odoo-erp-prod odoo

# Purge and rebuild
./scripts/odoo/purge_assets.sh odoo-erp-prod odoo
```

---

## 7) Final Smoke Tests (non-negotiable)

### 7.1 UI Health

- [ ] No blocking JS client errors in normal navigation
- [ ] Settings pages open without Owl "Oops" modal
- [ ] All menu items accessible without view errors

### 7.2 Core Functions

- [ ] Create a user → invitation email arrives
- [ ] Ask AI answers "Say OK" (Discuss → Ask AI)
- [ ] Create & submit an expense report
- [ ] Accounting reports load without access errors

### 7.3 Infrastructure

- [ ] Backups/snapshot taken
- [ ] Health check endpoint responds: `curl -I https://erp.insightpulseai.net/web/health`

---

## 8) Post-Go-Live Monitoring

### Daily checks (first week)

```bash
# Check for errors
docker logs --since 24h odoo-erp-prod | egrep -i "error|traceback|exception" | wc -l

# Check container health
docker ps | grep odoo

# Check disk space
df -h /var/lib/docker
```

### Weekly checks

- [ ] Review System Parameters for any unauthorized changes
- [ ] Check mail queue for stuck emails
- [ ] Verify backup jobs completed successfully
- [ ] Review user activity logs for anomalies

---

## Quick Reference: Fix Commands

| Issue | Command |
|-------|---------|
| tree→list fix | `docker exec -it odoo-erp-prod bash -lc 'odoo -d odoo -u ipai_v18_compat --stop-after-init'` |
| Asset purge | `./scripts/odoo/purge_assets.sh odoo-erp-prod odoo` |
| View errors | `docker logs -n 200 odoo-erp-prod \| egrep -i "view\|tree\|kanban"` |
| AI errors | `docker logs -n 200 odoo-erp-prod \| egrep -i "ai\|openai\|gemini"` |
| SMTP errors | `docker logs -n 200 odoo-erp-prod \| egrep -i "smtp\|mail"` |

---

## Related Documentation

- [CE + OCA Project Stack Mapping](./CE_OCA_PROJECT_STACK.md)
- [Enterprise to CE/OCA Mapping](./ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md)
- [OCA Apps Parity](./odoo-apps-parity.md)

---

*Last updated: 2026-01-06*
*Stack: Odoo 18 CE + OCA + IPAI custom modules*
