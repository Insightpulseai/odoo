# Odoo 19 Go-Live Checklist — Accounting + Inventory + Ops

> **Self-hosted CE 19.0** · Container: `odoo-core` · DB: `odoo`
> Domain: `erp.insightpulseai.com` · Nginx: `ipai-nginx`
> No outbound SMTP (DO blocks 25/465/587) — email via `ipai_zoho_mail_api`
>
> **Machine-verifiable manifest**: `ssot/go_live/odoo19_checklist.manifest.yaml`
> Schema: `ssot.go_live.manifest.v1` · Version: `1.1`
> `required_items` array pins 6 critical controls that must pass before go-live.

Last updated: 2026-02-27

---

## Quick Reference — Container Commands

```bash
# Shell into Odoo
docker exec -it odoo-core bash

# Odoo CLI
docker exec -it odoo-core /bin/bash -c \
  "python3 /opt/odoo/odoo-bin --config /etc/odoo/odoo.conf <args>"

# PostgreSQL
docker exec -it odoo-postgres psql -U odoo -d odoo

# Health check
curl -s https://erp.insightpulseai.com/web/health | python3 -m json.tool
scripts/healthcheck_odoo.sh  # full smoke test

# Module install/update
docker exec odoo-core python3 /opt/odoo/odoo-bin \
  --config /etc/odoo/odoo.conf \
  -d odoo --update ipai_zoho_mail_api --stop-after-init
```

---

## A) Pre-Cutover Controls

> Complete ALL items before any accounting data entry. Non-negotiable gate.

- [ ] **Freeze window declared** — announce cutover date/time to all users; lock legacy system
- [ ] **Chart of Accounts (CoA) finalized** — no pending account additions or renames
- [ ] **Currencies configured** — base currency set (`PHP`); foreign currencies + exchange rates imported
- [ ] **Fiscal year / tax periods open** — confirm opening fiscal period is unlocked for journal posting
- [ ] **Bank journals created** — one journal per bank account; account numbers + currencies correct
- [ ] **Email transport verified** — `ipai_zoho_mail_api` config parameters set (see §G2); test send passes
- [ ] **Backup baseline captured** — DB + filestore snapshot before any data entry:
  ```bash
  # DB dump
  docker exec odoo-postgres pg_dump -U odoo -Fc odoo > \
    backups/odoo_pre_golive_$(date +%Y%m%d_%H%M).dump
  # Filestore
  tar -czf backups/filestore_pre_golive_$(date +%Y%m%d_%H%M).tar.gz \
    /var/lib/docker/volumes/odoo_filestore/
  ```

---

## B) Opening Entries — Accounts Receivable (AR)

### B1) AR Clearing Account Setup

```sql
-- Confirm account exists: type=asset_current, reconcile=true
SELECT code, name, account_type, reconcile
FROM account_account
WHERE code LIKE '%AR%' OR name ILIKE '%receivable%clearing%';
```

- [ ] Account `1300` (or similar) exists with `account_type = asset_current`
- [ ] `reconcile = true` (Allow Reconciliation checked)
- [ ] Account NOT the same as the normal AR trade account

### B2) Open Invoices + Credit Notes Import

- [ ] Export open AR aging from legacy system as of cutover date
- [ ] Import via `account.move` CSV or Odoo data import wizard:
  - Move type: `out_invoice` (invoices), `out_refund` (credit notes)
  - Journal: dedicated `AR Opening` journal (type=General)
  - Counterpart: AR Clearing account (B1)
- [ ] Verify total imported AR = legacy AR aging total
  ```sql
  SELECT SUM(amount_residual)
  FROM account_move
  WHERE move_type = 'out_invoice'
    AND state = 'posted'
    AND payment_state != 'paid';
  ```

### B3) Open Customer Payments + Reconciliation

- [ ] Import unreconciled payments against AR Clearing account
- [ ] Reconcile each payment against the corresponding open invoice
- [ ] Verify AR Clearing balance approaches zero:
  ```sql
  SELECT SUM(balance)
  FROM account_move_line
  WHERE account_id = (SELECT id FROM account_account WHERE code = '1300')
    AND parent_state = 'posted';
  -- Expected: 0.00 (or within rounding tolerance)
  ```

### B4) AR Validation Gate ✅

- [ ] AR aging in Odoo matches signed-off legacy aging (diff < rounding threshold)
- [ ] AR Clearing account balance = 0.00

---

## C) Opening Entries — Accounts Payable (AP)

### C1) AP Clearing Account Setup

```sql
SELECT code, name, account_type, reconcile
FROM account_account
WHERE code LIKE '%AP%' OR name ILIKE '%payable%clearing%';
```

- [ ] Account `2100` (or similar) exists with `account_type = liability_current`
- [ ] `reconcile = true`
- [ ] Account NOT the same as normal AP trade account

### C2) Open Bills + Refunds Import

- [ ] Export open AP aging from legacy as of cutover date
- [ ] Import via `account.move`:
  - Move type: `in_invoice` (bills), `in_refund` (vendor refunds)
  - Journal: `AP Opening` journal (type=General)
  - Counterpart: AP Clearing account (C1)
- [ ] Verify total imported AP = legacy AP aging total:
  ```sql
  SELECT SUM(amount_residual)
  FROM account_move
  WHERE move_type = 'in_invoice'
    AND state = 'posted'
    AND payment_state != 'paid';
  ```

### C3) Open Vendor Payments + Reconciliation

- [ ] Import unreconciled payments against AP Clearing account
- [ ] Reconcile each payment against the corresponding open bill
- [ ] Verify AP Clearing balance = 0.00:
  ```sql
  SELECT SUM(balance)
  FROM account_move_line
  WHERE account_id = (SELECT id FROM account_account WHERE code = '2100')
    AND parent_state = 'posted';
  ```

### C4) AP Validation Gate ✅

- [ ] AP aging in Odoo matches signed-off legacy aging
- [ ] AP Clearing account balance = 0.00

---

## D) Inventory Opening

> Choose D1 (automated valuation) or D2 (manual/average cost). Not both.

### D1) Automated Valuation (Stock Accounting Active)

- [ ] **Product categories** configured:
  - Costing Method: `Average Cost (AVCO)` or `FIFO` (match legacy)
  - Inventory Valuation: `Automated`
  - Stock Input/Output/Valuation accounts set
- [ ] **Inventory Clearing account** created:
  - Type: `asset_current`, `reconcile = false`
  - Used as counterpart for opening stock journal entry
- [ ] **On-hand quantities import** via `stock.quant` wizard or CSV:
  - Product, location (`WH/Stock`), quantity, unit cost
- [ ] **Opening value journal entry** posted:
  - Dr Inventory Valuation account (sum of all qty × cost)
  - Cr Inventory Clearing account (same amount)
- [ ] **Opening value validation**:
  ```sql
  -- Odoo computed stock value
  SELECT SUM(quantity * cost) AS total_value
  FROM stock_quant
  WHERE location_id IN (
    SELECT id FROM stock_location WHERE usage = 'internal'
  );
  -- Compare to signed-off inventory value from legacy
  ```
- [ ] Inventory Clearing account balance = legacy-agreed value (offset by §E)

### D2) Manual Valuation

- [ ] Import quantities only (no accounting postings)
- [ ] No Inventory Clearing account needed
- [ ] Verify quantities match legacy count sheets:
  ```sql
  SELECT pt.name, sq.quantity, sq.location_id
  FROM stock_quant sq
  JOIN product_product pp ON sq.product_id = pp.id
  JOIN product_template pt ON pp.product_tmpl_id = pt.id
  ORDER BY pt.name;
  ```

---

## E) Trial Balance Import

> Import the signed-off legacy trial balance to establish opening balances
> for all accounts not covered by AR/AP/Inventory entries above.

### E1) Bank Journals — Approach Decision

Choose one approach per bank account:

| Approach | When to use | Notes |
|----------|-------------|-------|
| **A — With payments** | Outstanding cheques / uncleared items exist | Import individual transactions; reconcile against statement |
| **B — Net balance only** | Balance is clean / no uncleared items | Single journal entry: Dr/Cr bank account = TB balance |

- [ ] Decision recorded for each bank journal: Approach A or B

### E2) Trial Balance Posting Steps

For accounts with cleared TB balances (excluding AR, AP, Inventory handled above):

1. **Remap** AR/AP/Inventory lines in the import to their respective Clearing accounts
   (the real AR/AP/Inventory accounts are already populated via §B/C/D)
2. **Post** opening journal entries:
   - Journal: `Opening Balance Journal` (type=General, `default_move_type=general`)
   - Date: last day of prior fiscal year (or first day of new FY, per accountant preference)
3. **Retained earnings / Opening Equity** entry:
   - Net difference posts to `Retained Earnings (Opening)` account
   - This is the balancing entry; the TB import should net to zero

```sql
-- Verify total debits = total credits in opening journal
SELECT SUM(debit) AS total_dr, SUM(credit) AS total_cr,
       SUM(debit) - SUM(credit) AS imbalance
FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
WHERE am.ref LIKE '%Opening%'
  AND am.state = 'posted';
-- Expected: imbalance = 0
```

### E3) Clearing Accounts → Zero Validation

- [ ] AR Clearing = 0.00 (after B3 reconciliation)
- [ ] AP Clearing = 0.00 (after C3 reconciliation)
- [ ] Inventory Clearing = 0.00 (after TB entry offsets D1 entry)
- [ ] Bank Opening entries reconciled against opening statements

---

## F) Post-Cutover Validation — Go/No-Go Gate

> All items must be ✅ before declaring go-live complete.

### F1) AR Validation

- [ ] AR Aging report in Odoo matches signed-off legacy aging (customer-level)
- [ ] Total open AR balance matches legacy (diff ≤ rounding tolerance)

### F2) AP Validation

- [ ] AP Aging report in Odoo matches signed-off legacy aging (vendor-level)
- [ ] Total open AP balance matches legacy

### F3) Balance Sheet

- [ ] Balance Sheet in Odoo matches signed-off trial balance:
  - Total Assets = Total Liabilities + Equity
  - Major account groups tie line-by-line to legacy TB
  - Cash/bank balances match bank statements

### F4) P&L Baseline

- [ ] P&L report for the opening period shows zero or only expected YTD activity
- [ ] No phantom revenue/expense from data entry errors

### F5) Stock Validation (if D1)

- [ ] Inventory on-hand (qty) matches signed-off count sheets
- [ ] Stock valuation (cost) matches agreed opening inventory value

---

## G) Operational Hardening — Self-Hosted Specifics

### G1) Module Health

```bash
# Check addons_path warnings
docker logs odoo-core 2>&1 | grep -i "warning\|error" | grep -i "addon" | tail -20

# Full repo health
scripts/repo_health.sh

# Odoo health endpoint
curl -sf https://erp.insightpulseai.com/web/health && echo "PASS" || echo "FAIL"
```

- [ ] Zero addon-path warnings in startup logs
- [ ] `scripts/repo_health.sh` exits 0
- [ ] `/web/health` returns `{"status": "pass"}` with HTTP 200
- [ ] All required `ipai_*` modules installed and active:
  ```sql
  SELECT name, state FROM ir_module_module
  WHERE name LIKE 'ipai_%'
  ORDER BY name;
  -- Expected: all 'installed'
  ```

### G2) Email — Zoho API Transport

> `ipai_zoho_mail_api` replaces SMTP (DO blocks outbound mail ports).
> Credentials stored as `ir.config_parameter`, never hardcoded.

- [ ] Config parameters set (via Odoo Settings → Technical → Parameters):
  - `zoho_mail_api.client_id` — from Supabase Vault `zoho_client_id`
  - `zoho_mail_api.client_secret` — from Supabase Vault `zoho_client_secret`
  - `zoho_mail_api.refresh_token` — from Supabase Vault `zoho_refresh_token`
  - `zoho_mail_api.from_address` — e.g. `noreply@insightpulseai.com`
- [ ] Outgoing mail server: type=`zoho_api`, confirmed active (no SMTP server needed)
- [ ] Test send from Odoo:
  ```python
  # In Odoo shell (docker exec -it odoo-core python3 /opt/odoo/odoo-bin shell -d odoo)
  env['mail.mail'].create({
      'subject': 'Odoo Go-Live Test',
      'email_to': 'devops@insightpulseai.com',
      'body_html': '<p>Go-live email test from Odoo CE 19.0</p>',
  }).send()
  ```
- [ ] Test password-reset email sends successfully (Odoo built-in template):
  `Settings → Users → [user] → Send Password Reset Email`

### G3) Backups

- [ ] **DB backup job scheduled** — cron or CI workflow:
  ```bash
  # Example: daily dump to /backups/
  0 2 * * * docker exec odoo-postgres pg_dump -U odoo -Fc odoo > \
    /backups/odoo_$(date +\%Y\%m\%d).dump
  ```
- [ ] **Restore test performed** — restore to separate DB and verify:
  ```bash
  docker exec odoo-postgres createdb -U odoo odoo_restore_test
  docker exec -i odoo-postgres pg_restore -U odoo -d odoo_restore_test < backup.dump
  # Spot-check record counts
  docker exec odoo-postgres psql -U odoo -d odoo_restore_test \
    -c "SELECT COUNT(*) FROM res_partner;"
  ```
- [ ] Restore test evidence saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/restore_test.log`
- [ ] **Filestore backup** scheduled (volume mount `/var/lib/odoo`)

### G4) Security

- [ ] **Company scope enforcement** — `ipai_company_scope_omc` active:
  OMC-domain users are automatically restricted to TBWA company only
  ```sql
  SELECT name, state FROM ir_module_module
  WHERE name = 'ipai_company_scope_omc';
  -- Expected: installed
  ```
- [ ] **Admin account review**:
  - Default `admin` user password rotated (store in OS keychain, not in repo)
  - Admin email set to `devops@insightpulseai.com`
  - `list_db = False` in `odoo.conf` (prevents DB listing via web)
- [ ] **Auth subdomain resolves**: `https://auth.insightpulseai.com/.well-known/openid-configuration`
  returns valid OIDC discovery JSON (DNS PR #401 merged)
- [ ] **2FA enabled** for all admin-level users
- [ ] **No debug mode** in production URL: `/web?debug=` must not expose developer options

---

## H) Evidence Capture Convention

All go-live evidence bundles to:
```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/
```

### Required Artifacts

| File | Contents | How to generate |
|------|----------|-----------------|
| `balance_sheet_opening.csv` | Odoo Balance Sheet export at cutover date | Accounting → Reports → Balance Sheet → Export CSV |
| `ar_aging_opening.csv` | AR Aging report at cutover date | Accounting → Reports → Aged Receivable → Export |
| `ap_aging_opening.csv` | AP Aging report at cutover date | Accounting → Reports → Aged Payable → Export |
| `stock_valuation_opening.csv` | Inventory valuation report | Inventory → Reports → Valuation → Export |
| `go_live_health_check.log` | Full health check output | `scripts/healthcheck_odoo.sh > .../go_live_health_check.log 2>&1` |
| `trial_balance_comparison.csv` | Side-by-side: legacy TB vs Odoo TB | Manual comparison spreadsheet |
| `restore_test.log` | DB restore smoke test output | See §G3 |
| `email_test.log` | Zoho API test send result | Capture from Odoo mail logs |

### Capture Script

```bash
STAMP=$(date +%Y%m%d-%H%M+0800)
EVIDENCE=web/docs/evidence/${STAMP}/go-live/logs
mkdir -p "$EVIDENCE"

# Health check
scripts/healthcheck_odoo.sh 2>&1 | tee "${EVIDENCE}/go_live_health_check.log"

# Module states
docker exec odoo-postgres psql -U odoo -d odoo \
  -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;" \
  > "${EVIDENCE}/ipai_module_states.log"

# Stock valuation
docker exec odoo-postgres psql -U odoo -d odoo \
  -c "SELECT pt.name, sq.quantity, sq.cost FROM stock_quant sq JOIN product_product pp ON sq.product_id=pp.id JOIN product_template pt ON pp.product_tmpl_id=pt.id ORDER BY pt.name;" \
  > "${EVIDENCE}/stock_valuation_opening.csv"

echo "Evidence captured to: ${EVIDENCE}/"
echo "STATUS=PARTIAL — export Balance Sheet, AR/AP aging, TB comparison manually from Odoo UI"
```

---

## Go/No-Go Decision Matrix

| Gate | Owner | Pass Criteria | Status |
|------|-------|---------------|--------|
| AR balance matches legacy | Finance | Diff ≤ 1 PHP | ☐ |
| AP balance matches legacy | Finance | Diff ≤ 1 PHP | ☐ |
| Balance Sheet ties to TB | Finance | All major lines match | ☐ |
| Stock value matches | Ops | Diff ≤ agreed threshold | ☐ |
| Health check passes | DevOps | Exit 0, `/web/health` 200 | ☐ |
| Email sends successfully | DevOps | Test email delivered | ☐ |
| Backup + restore verified | DevOps | Restore count matches | ☐ |
| Security review complete | DevOps | No open admin risks | ☐ |

**All gates ✅ → STATUS=COMPLETE → Live**
**Any gate ❌ → STATUS=BLOCKED → Do not go live**

---

## Related Files

| File | Purpose |
|------|---------|
| `docs/runbooks/SECRETS_SSOT.md` | Vault secrets management (Zoho creds, etc.) |
| `ssot/secrets/registry.yaml` | Secret identifier registry |
| `addons/ipai/ipai_zoho_mail_api/` | Zoho API transport module |
| `addons/ipai/ipai_company_scope_omc/` | OMC user company restriction |
| `scripts/healthcheck_odoo.sh` | Full Odoo health check script |
| `deploy/odoo-prod.compose.yml` | Production container definitions |
| `config/odoo/odoo.conf` | Odoo runtime configuration |
