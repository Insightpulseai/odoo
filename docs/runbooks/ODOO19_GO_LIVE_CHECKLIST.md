# Odoo 19 Go-Live Checklist — Accounting + Inventory + Ops

> **Stack**: Odoo CE 19.0 · Self-hosted on DigitalOcean (178.128.112.214)
> **Container**: `odoo-core` · **DB**: `odoo` · **Nginx**: `ipai-nginx`
> **Domain**: `erp.insightpulseai.com` (Cloudflare proxied)
> **Email**: Zoho Mail API (`ipai_zoho_mail_api`) — no SMTP (DO blocks 25/465/587)
> **Scope enforcement**: `ipai_company_scope_omc` active (OMC users → TBWA company only)

---

## Quick reference — container commands

```bash
SSH_HOST=root@178.128.112.214

# Odoo shell (for data checks)
ssh $SSH_HOST "docker exec -it odoo-core /opt/odoo/odoo-bin shell -d odoo"

# Odoo logs
ssh $SSH_HOST "docker logs odoo-core --tail 50 -f"

# Health check
ssh $SSH_HOST "curl -s -o /dev/null -w '%{http_code}' http://localhost:8069/web/health"

# Repo health (run locally after SSH)
./scripts/healthcheck_odoo.sh
./scripts/repo_health.sh
```

---

## A) Pre-cutover controls

- [ ] **Freeze window defined** — no new invoices/bills/stock moves during cutover
- [ ] **Chart of Accounts** finalized — all accounts, taxes, journals, fiscal positions ready
- [ ] **Currencies** configured — FX rates set, especially for open items in foreign currency
- [ ] **Bank journals** configured:
  - [ ] Outstanding Receipts account assigned (if using "with payments after go-live" path)
  - [ ] Outstanding Payments account assigned
- [ ] **Email delivery** verified:
  - `ipai_zoho_mail_api` configured via `ir.config_parameter` (not hardcoded)
  - Zoho OAuth tokens stored in keychain/Vault (see `ssot/secrets/registry.yaml`)
  - Test outbound send passes: Settings → Technical → Email → Outgoing Mail Servers → Test
- [ ] **Company + user scope** verified:
  - `ipai.company.tbwa_company_id` config param set
  - OMC test user (`*@omc.com`) resolves to TBWA company only
- [ ] **DNS** resolves: `erp.insightpulseai.com` → `178.128.112.214` (verify PR #401 merged)

---

## B) Opening entries — Accounts Receivable (AR)

**Goal:** Open invoices, credit notes, and allocated payments net to zero on the AR Clearing
account. AR control account in the trial balance reconciles cleanly.

### Setup

- [ ] Create **AR Clearing (ARC)** account
  - Type: Current Assets
  - `Reconciliation: true` (allow reconciliation)
  - Code convention: e.g., `1100-CLR` or per your CoA

### Import open AR items

- [ ] **Multi-currency prep**: Set FX rates for all currencies in open items *before* import
- [ ] Import **open customer invoices** (status = posted, not paid)
- [ ] Import **open customer credit notes** (status = posted, not fully applied)
- [ ] Import/create **open customer payments** (unreconciled against invoices)

### Reconcile

- [ ] Reconcile open payments against open invoices in Odoo
- [ ] ARC balance after reconciliation = **0** (or exactly the agreed unreconciled balance)
- [ ] **Partner ledger (AR aging)** matches legacy system totals
  - Accounting → Reporting → Partner Ledger → filter type=Customer

---

## C) Opening entries — Accounts Payable (AP)

**Goal:** Open bills, refunds, and allocated payments net to zero on AP Clearing.

### Setup

- [ ] Create **AP Clearing (APC)** account
  - Type: Current Liabilities
  - `Reconciliation: true`

### Import open AP items

- [ ] **Multi-currency prep**: FX rates set before import
- [ ] Import **open vendor bills** (status = posted, not paid)
- [ ] Import **open vendor refunds/credit notes**
- [ ] Import/create **open vendor payments** (unreconciled)

### Reconcile

- [ ] Reconcile open payments against open bills
- [ ] APC balance after reconciliation = **0**
- [ ] **AP aging** matches legacy totals
  - Accounting → Reporting → Partner Ledger → filter type=Vendor

---

## D) Inventory opening

Choose **one** valuation path. Mixed is not recommended.

### D1) Automated valuation (Stock Accounting)

Use when product costs must drive accounting postings automatically.

- [ ] Accounting settings: confirm automated inventory valuation is active
- [ ] **Product categories** set per costing method:
  - [ ] Costing method: Standard / FIFO / Average Cost (AVCO) — per product type
  - [ ] Valuation: Automated
  - [ ] Stock Input / Output / Valuation accounts assigned
- [ ] **Products** imported/verified with:
  - [ ] Category assigned (correct costing method)
  - [ ] Type = Storable (not consumable, not service)
  - [ ] UoM set
  - [ ] Cost set (required for Standard and AVCO)
  - [ ] Lot/serial number tracking configured if needed
- [ ] Create **Inventory Clearing** account
  - Type: Current Assets
  - `Reconciliation: true`
- [ ] Configure virtual adjustment location:
  - Inventory → Configuration → Locations → `Virtual/Inventory adjustments`
  - Set valuation account to **Inventory Clearing**
- [ ] **Import on-hand quantities**
  - Inventory → Operations → Physical Inventory → import (product, location, qty, lot/SN)
  - Validate the physical inventory adjustment
- [ ] Verify opening stock value:
  - `Σ(standard_cost × opening_qty)` = agreed opening inventory balance
  - Inventory Clearing entry matches this value
- [ ] Post TB journal entry to offset Inventory Clearing (see Section E)

### D2) Manual valuation

Use when stock quantities are tracked but accounting valuation stays in the GL only.

- [ ] Products: type = Storable, costs set for reporting reference
- [ ] Import on-hand quantities (product, location, qty)
- [ ] Confirm: no automated stock valuation postings appear in the GL
- [ ] Opening inventory value handled purely via trial balance journal entry (Section E)

---

## E) Trial balance import

### E1) Bank journals — approach decision

Choose one before posting the TB entry:

**Option A — With payment entries after go-live (recommended)**

Configure bank journals with:
- Outstanding Receipts account (Current Assets, Allow reconciliation)
- Outstanding Payments account (Current Assets, Allow reconciliation)

Open outstanding items will be cleared when you reconcile bank statements post-go-live.

**Option B — Bank clearing account (simpler cutover)**

Temporarily map bank account balance to a Bank Clearing account until
real statement reconciliation begins. Useful when historical statement data
is not available for import.

### E2) TB posting steps

1. Export the legacy trial balance to CSV
2. Re-map control accounts:
   - AR control → **AR Clearing** (net of open items handled in Section B)
   - AP control → **AP Clearing** (net of open items handled in Section C)
   - Inventory control → **Inventory Clearing** (only if automated valuation path)
   - Bank accounts → per Option A or B decision above
3. Post TB journal entry:
   - Accounting → Accounting → Journal Entries → New
   - Journal: General / Miscellaneous
   - Date: cutover date (opening period)
   - Lines: one line per re-mapped TB row

### E3) Clearing account validation

- [ ] **AR Clearing = 0** after reconciling open invoices and payments
- [ ] **AP Clearing = 0** after reconciling open bills and payments
- [ ] **Inventory Clearing = 0** (automated valuation only — offset by TB entry)
- [ ] Bank balances tie to agreed opening statement balances

---

## F) Post-cutover validation — go/no-go gate

All items must pass before go-live is declared complete.

- [ ] **Aged Receivables** matches legacy system (Accounting → Reporting → Aged Receivable)
- [ ] **Aged Payables** matches legacy system (Accounting → Reporting → Aged Payable)
- [ ] **Balance Sheet** ties to the signed-off opening trial balance
  - Accounting → Reporting → Balance Sheet → set date to cutover date
- [ ] **P&L** baseline is structurally sound (no unexpected historic postings)
- [ ] **Stock on hand** (quantity + valuation) matches agreed opening
  - Inventory → Reporting → Inventory Valuation
- [ ] Bank journals operational:
  - Register a test payment → reconcile against a test bank statement line → confirm
- [ ] Tax reports/tax grids look sane (no phantom values from import)

---

## G) Operational hardening (self-hosted specifics)

### G1) Module and system health

```bash
# Run from local workstation (requires SSH access)
./scripts/repo_health.sh
./scripts/healthcheck_odoo.sh

# Verify /web/health endpoint
curl -s https://erp.insightpulseai.com/web/health | python3 -m json.tool
# Expected: {"status": "pass"} or {"result": "pass"}

# Confirm no addons_path warnings
ssh root@178.128.112.214 "docker logs odoo-core 2>&1 | grep -i 'addons.*warning\|not found.*addon' | tail -20"
# Expected: zero lines (or only pre-approved exceptions with tracked issues)
```

- [ ] `scripts/repo_health.sh` exits 0
- [ ] `/web/health` returns pass
- [ ] No unresolved `addons_path` warnings in Odoo logs

### G2) Email delivery (Zoho API transport)

The `ipai_zoho_mail_api` module routes outbound mail via Zoho REST API (port 443).
No SMTP config needed; DigitalOcean blocks SMTP ports.

- [ ] Zoho API credentials configured in `ir.config_parameter`:
  - `ipai.zoho.client_id`, `ipai.zoho.client_secret`, `ipai.zoho.refresh_token`, `ipai.zoho.account_id`
  - Values must come from keychain/Vault — never hardcoded
- [ ] Test user invitation email sends successfully:
  - Settings → Users → Invite User → verify delivery to a test address
  - This exercises the `auth_signup.set_password_email` template through the Zoho bridge
- [ ] Test transactional email (e.g., invoice by email) delivers

### G3) Backups

- [ ] Database backup scheduled (cron or managed backup):
  ```bash
  # Manual backup verification
  ssh root@178.128.112.214 "docker exec odoo-db pg_dump -U odoo odoo | gzip > /backups/odoo_$(date +%Y%m%d).sql.gz"
  ```
- [ ] Restore test: confirm backup can be restored to a test instance
- [ ] Filestore backup captured:
  ```bash
  ssh root@178.128.112.214 "tar czf /backups/filestore_$(date +%Y%m%d).tar.gz /var/lib/odoo/.local/share/Odoo/filestore/odoo"
  ```
- [ ] Backup evidence captured to: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/backup_verify.log`

### G4) Security

- [ ] **OMC company scope** active and correct:
  - `ipai_company_scope_omc` module installed
  - Config param `ipai.company.tbwa_company_id` set to correct company ID
  - Test: login as an `@omc.com` user → confirm only TBWA company is visible
- [ ] **Admin accounts** reviewed:
  - Default `admin` account password changed or disabled
  - 2FA policy documented (enforced at Cloudflare/IdP level if not in Odoo CE)
- [ ] **Auth subdomain** resolves (required for SSO/OIDC flows):
  - `dig +short auth.insightpulseai.com` → `178.128.112.214`
  - PR #401 must be merged and Cloudflare record applied

---

## H) Evidence capture convention

Capture artifacts to the canonical evidence path before declaring go-live complete.

```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/
```

**Required artifacts:**

| Artifact | How to capture |
|----------|---------------|
| `balance_sheet_opening.csv` | Odoo → Balance Sheet → export CSV at cutover date |
| `ar_aging_opening.csv` | Odoo → Aged Receivable → export CSV |
| `ap_aging_opening.csv` | Odoo → Aged Payable → export CSV |
| `stock_valuation_opening.csv` | Odoo → Inventory Valuation → export CSV |
| `go_live_health_check.log` | `./scripts/healthcheck_odoo.sh 2>&1 \| tee <path>/go_live_health_check.log` |
| `email_test.log` | Capture send test output |
| `backup_verify.log` | Capture backup + restore test output |

**Gitignore note:** Evidence log paths are unblocked by `.gitignore` negation rules:
```
!web/docs/evidence/20*/**/logs/
!web/docs/evidence/20*/**/logs/*.log
```
See MEMORY.md § Gitignore Trap if evidence logs won't stage.

---

## Related runbooks and scripts

| Resource | Path |
|----------|------|
| Deployment go-live (infra) | `docs/runbooks/deployment/DEPLOYMENT_RUNBOOK.md` |
| Mail smoke test | `docs/runbooks/RB_ODOO_MAIL_SMOKE.md` |
| Secrets SSOT | `docs/runbooks/SECRETS_SSOT.md` |
| Health check script | `scripts/healthcheck_odoo.sh` |
| Repo health check | `scripts/repo_health.sh` |
| Go-live orchestrator | `scripts/go_live.sh` |
| Release checklist generator | `scripts/new_go_live_checklist.sh` |
| DNS verification | `scripts/verify-dns-baseline.sh` |
