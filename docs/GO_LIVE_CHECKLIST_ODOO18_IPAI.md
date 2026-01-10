# Odoo 18 CE + OCA + IPAI Go-Live Checklist (InsightPulseAI)

**Version**: 2.0
**Stack**: Dockerized Odoo 18 CE on DO droplet + nginx reverse proxy + OCA modules + IPAI custom suite
**Optional**: AI (OpenAI/Gemini) + OCR/Digitalization service
**Last Updated**: January 2026

---

## 0) Platform / Infra Health (must be green before functional testing)

### 0.1 Domain + TLS

- [ ] Domain + TLS ok: https://erp.insightpulseai.net loads without mixed-content errors
- [ ] Certificate valid and not expiring within 30 days
- [ ] HSTS headers configured

### 0.2 Container Health

- [ ] Odoo container healthy:
  - [ ] `docker ps` shows `odoo-erp-prod` running
  - [ ] `docker logs -n 200 odoo-erp-prod` shows no repeating tracebacks
- [ ] Workers restart policy set; no crash loop
- [ ] Filestore volume mounted & writable

### 0.3 Outbound Connectivity (for AI/OCR)

- [ ] Outbound HTTPS from container works:
  - [ ] `curl -sS https://api.openai.com` returns a response (no DNS/egress block)
  - [ ] `curl -sS https://generativelanguage.googleapis.com` returns a response

### 0.4 Database Health

- [ ] PostgreSQL 15 running and healthy
- [ ] Database backup schedule active
- [ ] Connection pooling configured

---

## 1) Critical Odoo 18 Compatibility Gate (prevents UI hard-stops)

> **CRITICAL**: Odoo 18 renamed `tree` view mode to `list`. Kanban views now require `t-name="card"` template. These breaking changes will crash the UI if not fixed.

### 1.1 Fix act_window view_mode breaking change (tree -> list)

- [ ] Install `ipai_v18_compat` module:
  ```bash
  docker exec -it odoo-erp-prod odoo -d odoo -u ipai_v18_compat --stop-after-init
  docker restart odoo-erp-prod
  ```
- [ ] OR run standalone fix script:
  ```bash
  docker exec -it odoo-erp-prod python /mnt/extra-addons/ipai/scripts/fix_odoo18_views.py
  ```
- [ ] Verify no `tree` view_mode remains:
  ```bash
  docker exec -it odoo-erp-prod odoo shell -d odoo -c /etc/odoo/odoo.conf << 'EOF'
  actions = env['ir.actions.act_window'].sudo().search([('view_mode', 'ilike', 'tree')])
  print(f"Actions with tree view_mode: {len(actions)}")
  for a in actions[:10]:
      print(f"  - {a.id}: {a.name} ({a.view_mode})")
  EOF
  ```

### 1.2 Fix broken kanban views missing `t-name="card"`

- [ ] Detect kanban views missing card template (script will log these)
- [ ] Option A: Patch the views in source modules
- [ ] Option B: Enable auto-deactivation via system parameter:
  ```bash
  docker exec -it odoo-erp-prod odoo shell -d odoo -c /etc/odoo/odoo.conf << 'EOF'
  env["ir.config_parameter"].sudo().set_param("ipai_v18_compat.deactivate_broken_kanban", "1")
  print("Set ipai_v18_compat.deactivate_broken_kanban=1")
  EOF
  ```

### 1.3 Verification (Evidence)

- [ ] No client errors in browser console:
  - [ ] No "View types not defined tree found in act_window action ..."
  - [ ] No "Missing 'card' template."
- [ ] Verify logs are clean:
  ```bash
  docker logs -n 200 odoo-erp-prod | grep -iE "Missing .card.|View types not defined|Traceback" || echo "Clean!"
  ```

### 1.4 XML View Tag Migration (`<tree>` → `<list>`)

Odoo 17+ renamed the `<tree>` XML tag to `<list>`. While Odoo 18 supports both for backward compatibility, Odoo 19 may break.

| Version | `<tree>` | `<list>` |
|---------|----------|----------|
| Odoo 16 | ✅ | ❌ |
| Odoo 17 | ⚠️ deprecated | ✅ |
| Odoo 18 | ⚠️ warnings | ✅ |
| Odoo 19 | ❌ may break | ✅ |

- [ ] Audit custom modules for deprecated `<tree>` tags:

```bash
# Run audit script
./scripts/ci/audit_tree_tags.sh addons/ipai

# Quick fix (review changes before committing)
sed -i 's/<tree /<list /g; s/<\/tree>/<\/list>/g' <file>
```

- [ ] Update `view_mode="tree,form"` to `view_mode="list,form"` in action definitions
- [ ] No deprecation warnings in logs for view tags

---

## 2) Email / Invites / Reset Password (Outbound-only baseline)

### 2.1 Outgoing SMTP Configuration

- [ ] Outgoing SMTP configured (Mailgun 2525 / TLS STARTTLS)
- [ ] Odoo test connection successful
- [ ] From filtering set (e.g. *@insightpulseai.net)

### 2.2 Email Delivery Tests

- [ ] Send test:
  - [ ] Invite user email arrives
  - [ ] Password reset email arrives
- [ ] No mail queue stuck: Settings -> Technical -> Emails
- [ ] Check mail.mail model for failed records:
  ```bash
  docker exec -it odoo-erp-prod odoo shell -d odoo << 'EOF'
  failed = env['mail.mail'].sudo().search([('state', '=', 'exception')])
  print(f"Failed emails: {len(failed)}")
  EOF
  ```

---

## 3) AI Provider Configuration (Ask AI feature)

### 3.1 Provider Setup

- [ ] Settings -> AI Provider Configuration
  - [ ] "Use your own ChatGPT account" enabled + key saved
  - [ ] "Use your own Google Gemini account" enabled + key saved

### 3.2 Functional Tests

- [ ] Ask AI channel responds (Discuss -> Ask AI)
- [ ] Test simple prompt: "Say OK" returns response

### 3.3 Verification

- [ ] No provider errors in logs:
  ```bash
  docker logs -n 200 odoo-erp-prod | grep -iE "ai|openai|gemini|http.*error|traceback" || echo "Clean!"
  ```
- [ ] API key not exposed in logs or UI

---

## 4) Expenses + Document Digitalization (OCR) Readiness

### 4.1 Core Expenses Flow

- [ ] Products exist for expense categories:
  - [ ] Meals
  - [ ] Transportation
  - [ ] Accommodation
  - [ ] Miscellaneous
- [ ] Employee Expense Journal configured
- [ ] Payment modes correct:
  - [ ] "Employee (to reimburse)"
  - [ ] "Company"

### 4.2 End-to-End Expense Test

- [ ] Create expense
- [ ] Create expense report
- [ ] Submit for approval
- [ ] Approve expense report
- [ ] Post journal entry
- [ ] Verify GL entries created

### 4.3 Incoming Email Expenses (optional)

- [ ] Alias configured (expense@insightpulseai.net)
- [ ] Email gateway routes to Odoo (inbound)
- [ ] OR mark as "disabled/out-of-scope"

### 4.4 OCR / Receipt Ingestion

Pick ONE approach:

**Option A: Odoo Built-in OCR (if available)**
- [ ] OCR provider configured in Settings
- [ ] IAP account linked (if applicable)

**Option B: Custom OCR Microservice (recommended for CE)**
- [ ] Define endpoint in System Parameters: `ipai.ocr.endpoint`
- [ ] Define auth token in System Parameters: `ipai.ocr.api_key`
- [ ] ipai_ocr_expense module installed

### 4.5 OCR Verification

- [ ] Upload receipt produces structured fields:
  - [ ] Date extracted
  - [ ] Merchant extracted
  - [ ] Amount extracted
- [ ] At least one receipt processed successfully end-to-end

---

## 5) Accounting Go-Live (Opening Balances)

> Adapted from Odoo community best practices for accrual-basis accounting

### 5.A Opening Entries (Open Invoices/Bills)

#### Create Clearing Accounts
- [ ] Create AR Clearing account (reconcilable current asset)
- [ ] Create AP Clearing account (reconcilable current liability)
- [ ] Validate totals vs open AR/AP balances from prior system

#### Import Open Documents
- [ ] Import open invoices
- [ ] Import open credit notes
- [ ] Import open vendor bills
- [ ] Import open vendor refunds/credit memos

#### Reconciliation
- [ ] Reconcile AR Clearing to zero (or expected balance)
- [ ] Reconcile AP Clearing to zero (or expected balance)

### 5.B Inventory (only if holding stock)

#### Automated Valuation
- [ ] Product categories configured:
  - [ ] Costing method set (FIFO/Average/Standard)
  - [ ] Valuation method set (Automated)
- [ ] Inventory clearing account configured
- [ ] Import on-hand quantities
- [ ] Validate stock valuation vs initial balance

#### Manual Valuation
- [ ] Ensure no stock valuation expected on balance sheet
- [ ] Mark as "not applicable" if no inventory

### 5.C Trial Balance Import

#### Bank Account Method Selection
- [ ] Choose outstanding receipt/payment accounts (if using payment entries)
- [ ] OR use bank clearing account (if not using payment entries)

#### Trial Balance Entry
- [ ] Modify TB to account for AR/AP/Inventory clearing approach
- [ ] Post Trial Balance journal entry as opening entry
- [ ] Set journal entry date to cutover date

#### Validation
- [ ] AR Clearing account balance = 0 (or expected)
- [ ] AP Clearing account balance = 0 (or expected)
- [ ] Inventory Clearing account balance = 0 (or expected)
- [ ] Balance sheet balances

---

## 6) Final Smoke Tests (non-negotiable)

### 6.1 UI/UX Validation

- [ ] No blocking JS client errors in normal navigation
- [ ] Settings pages open without Owl "Oops" modal
- [ ] All installed app menus accessible

### 6.2 Core Workflows

- [ ] Create a user -> invitation email works
- [ ] Ask AI answers "Say OK" (if AI enabled)
- [ ] Create & submit an expense report
- [ ] Accounting reports load without access errors
- [ ] PDF reports generate correctly

### 6.3 Module Compatibility

- [ ] All IPAI modules installed without error
- [ ] All OCA dependencies resolved
- [ ] Module upgrade completes successfully:
  ```bash
  docker exec -it odoo-erp-prod odoo -d odoo -u all --stop-after-init
  ```

### 6.4 Backup Verification

- [ ] Backup snapshot taken
- [ ] Backup restoration tested on separate instance
- [ ] Filestore included in backup

---

## 7) Post-Fix Verification Commands

Run these after any fixes:

```bash
# Check for tree view_mode remnants
docker exec -it odoo-erp-prod odoo shell -d odoo << 'EOF'
tree_actions = env['ir.actions.act_window'].sudo().search([('view_mode', 'ilike', 'tree')])
print(f"Actions with 'tree': {len(tree_actions)}")
EOF

# Check for broken kanban views
docker exec -it odoo-erp-prod odoo shell -d odoo << 'EOF'
kanban_views = env['ir.ui.view'].sudo().search([('type', '=', 'kanban'), ('active', '=', True)])
broken = [v for v in kanban_views if 't-name="card"' not in (v.arch_db or '') and "t-name='card'" not in (v.arch_db or '')]
print(f"Broken kanban views: {len(broken)}")
for v in broken[:10]:
    print(f"  - {v.id}: {v.name} ({v.model})")
EOF

# Check for client errors in logs
docker logs -n 500 odoo-erp-prod 2>&1 | grep -iE "traceback|error|exception|missing" | head -20

# General health check
docker exec -it odoo-erp-prod odoo shell -d odoo << 'EOF'
print("=== Module Status ===")
for mod in env['ir.module.module'].sudo().search([('name', 'like', 'ipai_%')]):
    print(f"  {mod.name}: {mod.state}")
print("\n=== Database Info ===")
cr = env.cr
cr.execute("SELECT version();")
print(f"  PostgreSQL: {cr.fetchone()[0]}")
EOF
```

---

## 8) Sign-Off

### Technical Sign-Off

- [ ] All Section 0-1 checks passed (Platform + V18 Compat)
- [ ] All Section 2-4 checks passed (Email + AI + Expenses)
- [ ] Section 5 Accounting opening complete
- [ ] Section 6 smoke tests all green

**Signed By**: _________________________ (DevOps Lead)
**Date/Time**: _________________________

### Business Sign-Off

- [ ] Core business processes verified
- [ ] User acceptance testing complete
- [ ] Training delivered
- [ ] Go-live approved

**Signed By**: _________________________ (Business Owner)
**Date/Time**: _________________________

---

## Quick Reference: ipai_v18_compat Module

### Installation

```bash
# Standard installation (migration runs automatically)
docker exec -it odoo-erp-prod odoo -d odoo -i ipai_v18_compat --stop-after-init
docker restart odoo-erp-prod
```

### Upgrade (re-run migration)

```bash
docker exec -it odoo-erp-prod odoo -d odoo -u ipai_v18_compat --stop-after-init
docker restart odoo-erp-prod
```

### Enable Auto-Deactivation of Broken Kanban

```bash
docker exec -it odoo-erp-prod odoo shell -d odoo << 'EOF'
env["ir.config_parameter"].sudo().set_param("ipai_v18_compat.deactivate_broken_kanban", "1")
env.cr.commit()
print("Enabled auto-deactivation")
EOF
```

---

## Appendix A: Common Odoo 18 Breaking Changes

| Change | Impact | Fix |
|--------|--------|-----|
| `tree` -> `list` in view_mode | UI crashes with "View types not defined tree" | Run ipai_v18_compat migration |
| Kanban requires `t-name="card"` | UI crashes with "Missing 'card' template" | Patch views or deactivate |
| `arch` -> `arch_db` in views | Code accessing `arch` may fail | Update to use `arch_db` |
| `search_count` signature change | Existing code may break | Check domain parameter |

---

## Appendix B: Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project conventions and commands
- [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) - Original comprehensive checklist
- [ODOO_18_EE_TO_CE_OCA_PARITY.md](ODOO_18_EE_TO_CE_OCA_PARITY.md) - Enterprise to CE mapping
- [TESTING_ODOO_18.md](TESTING_ODOO_18.md) - Testing guide

---

*This checklist extends the original GO_LIVE_CHECKLIST.md with Odoo 18-specific compatibility fixes and AI/OCR readiness sections.*
