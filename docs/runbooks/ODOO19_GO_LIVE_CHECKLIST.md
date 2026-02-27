# Odoo 19 Go-Live Checklist — Accounting + Inventory + Ops

> Self-hosted CE · `odoo-core` container · DB: `odoo` · Domain: `erp.insightpulseai.com`
>
> Run this checklist for each go-live event (initial cutover or major module activation).
> Evidence convention: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/`

---

## Quick Reference — Container Commands

```bash
# SSH to droplet
ssh root@178.128.112.214

# Odoo shell
docker exec -it odoo-core /odoo/odoo-bin shell -d odoo --no-http

# Odoo logs (live)
docker logs odoo-core --follow --tail 100

# Restart Odoo
docker restart odoo-core

# Database backup (before any cutover step)
docker exec odoo-postgres pg_dump -U odoo odoo | gzip > /backup/odoo-$(date +%Y%m%d-%H%M).sql.gz

# Verify backup
ls -lh /backup/odoo-$(date +%Y%m%d)*.sql.gz
```

---

## A) Pre-Cutover Controls

### A1 — Database backup
```bash
# On droplet
docker exec odoo-postgres pg_dump -U odoo odoo | gzip > /backup/odoo-pre-golive.sql.gz
ls -lh /backup/odoo-pre-golive.sql.gz
```
**Evidence**: Record backup file size and timestamp.
**Acceptance**: Backup file > 0 bytes.

### A2 — Module health check
```bash
docker exec odoo-core /odoo/odoo-bin --db_host localhost -d odoo \
  --test-enable --log-level=test --stop-after-init 2>&1 | tail -20
```
**Acceptance**: No `ERROR` in final 20 lines.

### A3 — Freeze new transactions
- Notify all users: "System entering maintenance mode at HH:MM"
- Disable self-service user login (optional: set maintenance mode in Odoo settings)
- Confirm no open transactions in progress

### A4 — Confirm chart of accounts
- Verify CoA matches target accounting standard (Philippines PFRS / IFRS)
- Check: `Settings → Accounting → Chart of Accounts → Filter: Unreconciled`

### A5 — Confirm fiscal year / period
```bash
# Odoo shell
from odoo.fields import Date
env['account.fiscal.year'].search([('state', '=', 'draft')])
```
**Acceptance**: Active fiscal year covers go-live date.

---

## B) Opening Entries — Accounts Receivable (AR)

### B1 — Set up AR control account
- Account: `120000` (or per CoA) — `Accounts Receivable Control (ARC)`
- Type: Receivable, Reconcile: True
- Verify: `Accounting → Configuration → Accounts → Type: Receivable`

### B2 — Import open invoices
```bash
# Via CSV import or manual entry
# Each open invoice: customer, amount, due date, invoice date
# Leave as "Posted" state — do not set to "Paid"
```
**Acceptance**: All open invoices visible in `Accounting → Customers → Invoices → Filter: Open`

### B3 — Import customer payments on account
```bash
# Payments already collected but not matched to invoices
# Entry: DR Cash/Bank, CR Customer account
```

### B4 — Reconcile AR
- Run: `Accounting → Accounting → Actions → Reconcile → AR`
- Match payments to invoices where applicable
**Acceptance**: Unreconciled items < 5% of AR balance (investigate remainder)

---

## C) Opening Entries — Accounts Payable (AP)

### C1 — Set up AP control account
- Account: `200000` (or per CoA) — `Accounts Payable Control (APC)`
- Type: Payable, Reconcile: True

### C2 — Import open vendor bills
- Each open bill: vendor, amount, due date, bill date
- State: Posted (not paid)
**Acceptance**: All open bills visible in `Accounting → Vendors → Bills → Filter: Open`

### C3 — Import vendor payments on account
- Payments made but not matched to bills
- Entry: DR Vendor account, CR Cash/Bank

### C4 — Reconcile AP
**Acceptance**: Unreconciled items < 5% of AP balance

---

## D) Inventory Opening

### D1 — Automated valuation (Average Cost / FIFO)
```bash
# Odoo shell — create inventory adjustment
env['stock.quant'].with_context(inventory_mode=True).create({
    'product_id': product.id,
    'location_id': location.id,
    'quantity': qty,
})
env['stock.inventory'].action_validate()
```

### D2 — Manual valuation
- `Inventory → Operations → Physical Inventory`
- Enter quantities for each product/location
- Validate → Creates journal entries automatically (if automated valuation enabled)

**Acceptance**: `Inventory → Reporting → Inventory Valuation` matches trial balance inventory account.

---

## E) Trial Balance Import

### E1 — Bank journal opening balances
```bash
# For each bank account: create an opening entry
# DR Bank, CR Opening Balance Equity (999000)
# Date: day before go-live date
```

### E2 — Trial balance posting
- Import TB from previous system (CSV)
- Each line: Account code, Debit, Credit
- Post as opening journal entry dated: day before go-live

### E3 — Zero validation
```bash
# Odoo shell — verify TB is zero-balanced
from odoo import fields
moves = env['account.move.line'].search([('move_id.date', '<=', fields.Date.today())])
total = sum(m.debit - m.credit for m in moves)
print(f"Net balance: {total}")  # Expected: 0.0
```
**Acceptance**: Net balance = 0.00 (within rounding tolerance ±0.01)

---

## F) Post-Cutover Go/No-Go Gate

Run all checks. ALL must pass before declaring go-live complete.

| Check | Command | Expected |
|-------|---------|---------|
| AR balance matches TB | `account.move.line` query | Matches opening TB |
| AP balance matches TB | `account.move.line` query | Matches opening TB |
| Inventory value matches TB | `stock.valuation.layer` | Matches opening TB |
| Bank balance matches statement | Manual check | Matches bank statement |
| No unposted opening entries | `account.move` filter Draft | 0 draft entries |
| Module health | `docker logs odoo-core \| grep ERROR` | 0 errors |
| Email test | Send test mail from Odoo | Received via Zoho Mail |

**Decision**:
- ALL pass → **GO** — announce go-live to stakeholders
- ANY fail → **NO-GO** — execute rollback (restore pre-golive backup)

---

## G) Operational Hardening

### G1 — Module health (post go-live)
```bash
# Check for import errors
docker exec odoo-core python3 -c "import odoo; print('OK')"
docker logs odoo-core --since 1h 2>&1 | grep -c ERROR
```
**Acceptance**: 0 ERROR lines in last 1 hour.

### G2 — Email verification
```bash
# Send test email from Odoo
# Settings → Technical → Email → Outgoing Mail Servers → Test Connection
# Then: Settings → Technical → Email → Send Test Email
```
**Acceptance**: Test email received at admin inbox.

### G3 — Automated backups
```bash
# Verify backup cron is active
docker exec odoo-postgres crontab -l | grep backup
```
**Acceptance**: Backup cron runs daily at minimum.

### G4 — Security review
- [ ] Default admin password changed from `admin`
- [ ] 2FA enabled for admin account
- [ ] `list_db` set to `False` in `odoo.conf`
- [ ] No debug mode enabled in production
- [ ] `erp.insightpulseai.com` returns valid SSL certificate

```bash
# Verify SSL
curl -sI https://erp.insightpulseai.com | grep -E "HTTP|Strict"
```

---

## H) Evidence Capture

All go-live evidence goes to:
```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/logs/
```

Required artifacts:
- `pre-golive-backup.log` — backup file path + size
- `module-health.log` — output of step A2
- `tb-zero-check.log` — output of step E3
- `post-golive-errors.log` — `docker logs odoo-core --since 1h 2>&1 | grep ERROR`
- `email-test.log` — confirmation email received
- `ssl-check.log` — output of curl command in G4

```bash
# Capture all evidence
STAMP=$(date +%Y%m%d-%H%M+0800)
EVIDENCE_DIR="web/docs/evidence/${STAMP}/go-live/logs"
mkdir -p "$EVIDENCE_DIR"

# Run checks and capture
docker logs odoo-core --since 1h 2>&1 | grep ERROR > "${EVIDENCE_DIR}/post-golive-errors.log"
curl -sI https://erp.insightpulseai.com > "${EVIDENCE_DIR}/ssl-check.log"
ls -lh /backup/odoo-pre-golive.sql.gz > "${EVIDENCE_DIR}/pre-golive-backup.log"

echo "Evidence captured at: ${EVIDENCE_DIR}"
```

**STATUS**: Report `STATUS=COMPLETE` only when all sections A-G have passed and evidence is captured.

---

*Owner: Platform Engineering*
*Template version: 1.0.0 (2026-02-27)*
*Evidence convention: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/go-live/`*
