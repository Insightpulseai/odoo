# TBWA/OMC PH Go-Live Guide (Odoo 18 CE + IPAI)

> **Scope**: Accounting + Month-End Close + BIR Tax via Project Command Center
> **Onboarding**: Invitation-only email (Gmail OAuth or Zoho SMTP)
> **Copilot**: Ask AI (ChatGPT or Gemini) in Settings > Integrations
> **Finance Supervisor**: Beng Manalo (beng.manalo@omc.com)

---

## Quick Links

| Resource | Location |
|----------|----------|
| **Checklist CSV** | `docs/golive/TBWA_OMC_PH_GOLIVE_CHECKLIST.csv` |
| **Prod Server** | `159.223.75.148` |
| **Prod URL** | `https://erp.insightpulseai.com` |
| **Database** | `odoo` |

---

## Section 0: Prerequisites (Day -7 to -1)

### System Checks

| Check | Command/Action |
|-------|----------------|
| Prod URL OK | `curl -I https://erp.insightpulseai.com` returns 200 |
| Workers running | `docker ps \| grep odoo-erp-prod` shows healthy |
| Mail queue cron | See automated check below |

### Email (Invite-Only Onboarding)

- [ ] Outgoing email server configured (Gmail OAuth OR Zoho SMTP)
- [ ] Test invite + password reset works end-to-end
- [ ] Domain allowlist: `omc.com,tbwa-smp.com`

### Ask AI

- [ ] Provider selected: `openai` or `gemini`
- [ ] API key saved in Settings > Integrations
- [ ] Smoke test returns valid response

### Automated Prerequisites Check

```bash
ssh root@159.223.75.148 <<'EOF'
set -euo pipefail
docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
print("=== PREREQUISITES CHECK ===")

# 1) Company + basic config
companies = env['res.company'].search([])
print("Companies:", [(c.id, c.name, c.currency_id.name) for c in companies])

# 2) Active users (no demo)
users = env['res.users'].sudo().search([('active','=',True)])
print("Active users:", len(users))
demo = env['res.users'].sudo().search([('login','ilike','demo')])
print("Demo users (should be 0):", len(demo))

# 3) Email server
servers = env['ir.mail_server'].sudo().search([])
print("Outgoing servers:", [(s.name, s.smtp_host, s.active) for s in servers])

# 4) Email queue cron
cron = env['ir.cron'].sudo().search([('name','ilike','Email Queue')])
print("Email queue crons:", [(c.name, c.active) for c in cron])

# 5) Ask AI config
ICP = env['ir.config_parameter'].sudo()
print("Ask AI enabled:", ICP.get_param('ipai.ask_ai.enabled'))
print("Ask AI provider:", ICP.get_param('ipai.ask_ai.provider'))
print("Domain allowlist:", ICP.get_param('ipai.ask_ai.domain_allowlist'))
PY
EOF
```

---

## Section A: Opening Entries Import

### A1) AR/AP Clearing Accounts

| Account | Type | Reconcilable |
|---------|------|--------------|
| AR Clearing | Current Assets | ✓ |
| AP Clearing | Current Liabilities | ✓ |

### A2) Validation Before Import

- [ ] Open invoices + credits + payments reconcile vs AR aging
- [ ] Open bills + refunds + payments reconcile vs AP aging
- [ ] Multi-currency rates updated (if applicable)

### A3) Import Sequence

1. Partners (Customers + Vendors)
2. Open invoices / credit notes
3. Open bills / refunds
4. Payment initial balances (mapped to clearing)

### A4) Gate Check

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
Acc = env['account.account'].sudo()
ML = env['account.move.line'].sudo()

def check_clearing(name):
    acc = Acc.search([('name','ilike',name)], limit=1)
    if not acc:
        print(f"{name}: NOT FOUND")
        return
    balance = sum(ML.search([('account_id','=',acc.id)]).mapped('balance'))
    status = "PASS" if abs(balance) < 0.01 else "FAIL"
    print(f"{name} ({acc.code}): balance = {balance:.2f} [{status}]")

check_clearing("AR Clearing")
check_clearing("AP Clearing")
PY
EOF
```

---

## Section B: Inventory (Optional for Agency)

> **TBWA Note**: Most agencies don't hold significant stock. Skip this section if you have no inventory to track.

### Decision Point

- [ ] **No stock**: Skip to Section C
- [ ] **Hold stock**: Choose Automated or Manual valuation

### Automated Valuation Setup

1. Enable automatic stock accounting
2. Configure product categories (costing + valuation)
3. Create Inventory Clearing (Current Asset, reconcilable)
4. Import products + initial quantities
5. Gate: inventory value = opening balance

---

## Section C: Trial Balance Import

### C0) Bank Method Decision

| Option | Use Case |
|--------|----------|
| **C-A: Outstanding Accounts** | Need payment entries post go-live (recommended) |
| **C-B: Bank Clearing** | Simpler ops, no payment reconciliation |

### C1) Account Setup (if C-A)

- [ ] Outstanding Receipts (Current Asset, reconcilable)
- [ ] Outstanding Payments (Current Asset, reconcilable)
- [ ] Bank journal configured with outstanding accounts

### C2) TB Mapping Rules

| Original Account | Map To | Notes |
|-----------------|--------|-------|
| AR | AR Clearing | Exclude open customer payments |
| AP | AP Clearing | Exclude open vendor payments |
| Inventory | Inventory Clearing | Only if automated valuation |

### C3) Import + Post

- [ ] Import TB journal entry
- [ ] Post journal entry
- [ ] Run gate checks

### Gate Check

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
Acc = env['account.account'].sudo()
ML = env['account.move.line'].sudo()

clearings = ["AR Clearing", "AP Clearing", "Inventory Clearing"]
for name in clearings:
    acc = Acc.search([('name','ilike',name)], limit=1)
    if not acc:
        print(f"{name}: NOT CONFIGURED (OK if not used)")
        continue
    balance = sum(ML.search([('account_id','=',acc.id)]).mapped('balance'))
    status = "PASS" if abs(balance) < 0.01 else "FAIL"
    print(f"{name} ({acc.code}): {balance:.2f} [{status}]")
PY
EOF
```

---

## Section D: Project Command Center (Month-End Close + BIR Tax)

### D1) Required Modules

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo -d odoo \
  -u ipai_month_end_closing,ipai_bir_tax_compliance,ipai_close_orchestration \
  --stop-after-init --log-level=info
EOF
```

### D2) Ownership Rules

| Role | Assigned To |
|------|-------------|
| Finance Supervisor | Beng Manalo (beng.manalo@omc.com) |
| All task assignees | Must be Internal Users (not just contacts) |

**Critical**: No placeholder users allowed (e.g., `<<MAP:Role>>`)

### D3) Import Sequence

1. Projects (Month-end close, Tax filing)
2. Stages (mapped to stage gates)
3. Tasks (parents first, then children)
4. Dependencies (if enabled)
5. Calendar events (holidays, deadlines)

### D4) Stage Gates

| From Stage | To Stage | Requirement |
|------------|----------|-------------|
| Preparation | Review | Required tasks complete |
| Review | Approval | Beng approval |
| Approval | Done | Posting/locks complete |

### D5) Executive Dashboard

The home screen should show:
- Month-end close progress (status, blockers)
- Tax filing deadlines (owner, due date)
- "Ask AI" panel link
- Quick actions (create invite, open close run)

### Gate Check

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
print("=== PROJECT COMMAND CENTER CHECK ===")

Proj = env['project.project'].sudo()
Task = env['project.task'].sudo()
Users = env['res.users'].sudo()

# 1) Key projects exist
close_proj = Proj.search([('name','ilike','close')])
tax_proj = Proj.search([('name','ilike','tax')])
print("Close projects:", [(p.id, p.name) for p in close_proj])
print("Tax projects:", [(p.id, p.name) for p in tax_proj])

# 2) Beng exists and is assigned
beng = Users.search([('login','=','beng.manalo@omc.com')], limit=1)
if beng:
    print(f"Beng user: ID={beng.id}, login={beng.login} [PASS]")
    beng_tasks = Task.search_count([('user_ids','in',[beng.id])])
    print(f"Tasks assigned to Beng: {beng_tasks}")
else:
    print("Beng user: NOT FOUND [FAIL]")

# 3) No placeholders
placeholders = Task.search_count([('name','ilike','<<MAP:')])
status = "PASS" if placeholders == 0 else "FAIL"
print(f"Placeholder tasks: {placeholders} [{status}]")

# 4) Task counts
total_tasks = Task.search_count([])
print(f"Total tasks: {total_tasks}")
PY
EOF
```

---

## Section E: Invitation-Only Onboarding

### E1) Email Flow

1. Admin creates user (via UI or `admin.invite_user` tool)
2. System sends password reset email
3. User clicks link, sets password
4. User logs in

### E2) Security Settings

- [ ] Public signup disabled
- [ ] Domain allowlist enforced (`omc.com,tbwa-smp.com`)
- [ ] All invitees get correct groups (Internal User, not Portal)

### Test Flow

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
# Test invite (dry run - don't actually send)
email = "test.user@omc.com"
ICP = env['ir.config_parameter'].sudo()
allowlist = ICP.get_param('ipai.ask_ai.domain_allowlist', '')
domains = [d.strip().lower() for d in allowlist.split(',') if d.strip()]
domain = email.split('@')[-1].lower()

if domain in domains:
    print(f"Email {email}: domain {domain} ALLOWED")
else:
    print(f"Email {email}: domain {domain} NOT IN ALLOWLIST {domains}")
PY
EOF
```

---

## Section F: Final Go/No-Go Gates

### Automated Final Check

```bash
ssh root@159.223.75.148 <<'EOF'
set -euo pipefail
echo "=== TBWA/OMC PH GO-LIVE FINAL GATES ==="

docker exec -t odoo-erp-prod odoo shell -d odoo <<'PY'
results = []

# 1) Email server
servers = env['ir.mail_server'].sudo().search([('active','=',True)])
results.append(("Outgoing email server", "PASS" if servers else "FAIL"))

# 2) Required users
must_have = ["beng.manalo@omc.com"]
for login in must_have:
    u = env['res.users'].sudo().search([('login','=',login)], limit=1)
    results.append((f"User: {login}", "PASS" if u else "FAIL"))

# 3) Projects exist
Proj = env['project.project'].sudo()
close = Proj.search([('name','ilike','close')])
tax = Proj.search([('name','ilike','tax')])
results.append(("Close project exists", "PASS" if close else "FAIL"))
results.append(("Tax project exists", "PASS" if tax else "FAIL"))

# 4) No placeholders
Task = env['project.task'].sudo()
bad = Task.search_count([('name','ilike','<<MAP:')])
results.append(("No placeholder tasks", "PASS" if bad == 0 else f"FAIL ({bad} found)"))

# 5) AR/AP clearing balanced
Acc = env['account.account'].sudo()
ML = env['account.move.line'].sudo()
for name in ["AR Clearing", "AP Clearing"]:
    acc = Acc.search([('name','ilike',name)], limit=1)
    if acc:
        bal = sum(ML.search([('account_id','=',acc.id)]).mapped('balance'))
        results.append((f"{name} = 0", "PASS" if abs(bal) < 0.01 else f"FAIL ({bal:.2f})"))

# Print results
print("\n" + "="*50)
print("GO-LIVE GATE RESULTS")
print("="*50)
all_pass = True
for item, status in results:
    print(f"  {item}: {status}")
    if "FAIL" in status:
        all_pass = False

print("="*50)
print("OVERALL:", "GO" if all_pass else "NO-GO")
print("="*50)
PY
EOF
```

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Finance Supervisor | Beng Manalo | | |
| IT Admin | | | |
| Project Lead | | | |

**Go-Live Date**: ________________

---

## Appendix: Module Upgrade Command

```bash
ssh root@159.223.75.148 <<'EOF'
docker exec -t odoo-erp-prod odoo -d odoo \
  -u ipai_ask_ai,ipai_month_end_closing,ipai_bir_tax_compliance,ipai_close_orchestration,ipai_theme_tbwa_backend \
  --stop-after-init --log-level=info
EOF
```

---

*Last updated: 2026-01-05*
