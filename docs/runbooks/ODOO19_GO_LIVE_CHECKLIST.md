# Odoo 19 Go-Live Checklist

> **Version:** 1.0.0 | **Date:** 2026-03-19 | **Owner:** Jake Tolentino
> **SSOT:** `ssot/delivery/go_live_plan.yaml`
> **Status:** DRAFT -- sections updated with 2026-03-18/19 session evidence

---

## 1. Pre-Flight Checks (Identity, MFA, Secrets)

- [ ] **CP-1** Both native Entra admins (`admin@`, `emergency-admin@`) have MFA enrolled
- [ ] Security Defaults enabled in Entra ID (or equivalent Conditional Access policy)
- [ ] Emergency break-glass account tested (sign-in + MFA verification)
- [ ] All Azure Key Vault secrets present and resolvable at runtime:
  - [x] `zoho-smtp-user` / `zoho-smtp-password` (mail)
  - [x] `foundry-endpoint` / `foundry-api-key` (AI -- vaulted 2026-03-18)
  - [x] `search-endpoint` / `search-api-key` (AI Search -- vaulted 2026-03-18)
  - [x] `pg-admin-password` (database -- vaulted 2026-03-18)
  - [x] `ado-pat` (Azure DevOps -- vaulted 2026-03-18)
- [ ] No plaintext secrets in committed config files (verified via `gitleaks`)
- [ ] Service principal / managed identity bindings verified for ACA -> KV access

---

## 2. Infrastructure Readiness (ACA, PG, Front Door, Key Vault, Azure Files)

- [x] Azure Container Apps environment (`cae-ipai-dev`) is provisioned and healthy
- [x] PostgreSQL Flexible Server (`ipai-odoo-dev-pg`) is accessible from ACA
- [ ] **CP-3** Azure Front Door (`ipai-fd-dev`) deployed with WAF managed rules active
- [ ] **CP-3** All canonical hostnames route through AFD (`erp.`, `n8n.`, `auth.`, etc.)
- [x] Azure Key Vault (`kv-ipai-dev`) is accessible from ACA via managed identity
- [x] KV-backed secrets wired to all 3 ACA apps (web, worker, cron) -- DONE 2026-03-18
- [ ] **CP-2** Azure Files share mounted to ACA for Odoo filestore persistence
- [ ] **CP-2** Filestore survives container restart (persistence test passed)
- [x] Container Registry (`cripaidev` or `ipaiodoodevacr`) contains current image
- [ ] Resource locks on production-critical resources (PG, KV, storage)

---

## 3. Database Readiness

- [x] Production database (`odoo`) exists on `ipai-odoo-dev-pg`
- [ ] All pending migrations applied (`odoo-bin -u all --stop-after-init`)
- [ ] Database backup verified (point-in-time restore or manual backup)
- [ ] Backup restore tested on a disposable database
- [ ] **CP-6** `dbfilter` configured and hostname-to-database routing validated
- [ ] `list_db = False` in production config (prevents database enumeration)
- [ ] `admin_passwd` set and not the default (or disabled)
- [x] Database connection string uses KV-backed secret (not hardcoded)

---

## 4. Runtime Readiness (Web, Worker, Cron)

- [x] `ipai-odoo-dev-web` container healthy (HTTP 200 on `/web/login`)
- [x] `ipai-odoo-dev-worker` container running (background jobs processing)
- [x] `ipai-odoo-dev-cron` container running (scheduled actions executing)
- [x] Asset bundling working (CSS/JS served correctly) -- FIXED 2026-03-18
- [x] Stale DB secret resolved (prod login functional) -- FIXED 2026-03-18
- [ ] `proxy_mode = True` set (required behind Azure Front Door)
- [ ] **CP-4** Cron jobs execute without error (analytic_account_id drift fixed)
- [ ] **CP-4** Cron execution log captured as evidence
- [ ] Longpolling / websocket configured for worker container
- [ ] `--max-cron-threads` set appropriately per container role

---

## 5. Module Readiness

### IPAI Custom Modules

- [x] `ipai_odoo_copilot` module built (20 files, OWL systray) -- 2026-03-18
- [x] `ipai_finance_ppm` demo data seeded (95 tasks, 4-phase close) -- 2026-03-18
- [ ] All critical-path `ipai_*` modules install cleanly on production DB
- [ ] Module dependency graph validated (no missing deps)
- [ ] No Enterprise module dependencies in any installed module

### OCA Modules

- [ ] OCA modules hydrated via gitaggregate (`addons/oca/`)
- [ ] 56-module baseline installable (should-do, not blocking go-live)
- [ ] No version conflicts between IPAI and OCA modules

---

## A) Opening Entries — Accounts Receivable (AR)

> Adapted from Odoo 18 SF-Experts go-live checklist (accrual basis).
> All journal entries execute via CLI against `pg-ipai-odoo` (Azure PG Flexible Server).

- [ ] Create account: **AR Clearing** (ARC), type: Current Assets, allow reconciliation
- [ ] Create account: **AP Clearing** (APC), type: Current Liabilities, allow reconciliation
- [ ] Verify open invoice + credit note sums match open AR balance (client accountant sign-off)
- [ ] Check multi-currency open invoices — update exchange rates before import
- [ ] Import open invoices and credit notes
- [ ] Adjust open customer payments to AR credit on initial balance (per line item, partner set)
- [ ] Verify AR Clearing balance = 0 after reconciliation

---

## B) Opening Entries — Accounts Payable (AP)

- [ ] Verify open bill + refund sums match open AP balance (client accountant sign-off)
- [ ] Check multi-currency open bills — update exchange rates before import
- [ ] Import open bills and refunds
- [ ] Adjust open vendor payments to AP debit on initial balance (per line item, partner set)
- [ ] Verify AP Clearing balance = 0 after reconciliation

---

## C) Inventory Opening

> Choose automated or manual valuation per product category.

### Automated Valuation

- [ ] Accounting settings: enable Automatic Accounting
- [ ] Product categories configured with costing method and valuation
- [ ] Products imported with correct category, cost, type=Goods, track=Quantity
- [ ] Create **Inventory Clearing** account (type: Current Asset, allow reconciliation)
- [ ] Set Inventory Clearing on virtual inventory adjustment location
- [ ] Collect inventory import file (product, location, quantity, lot/SN optional)
- [ ] Verify: sum(cost * qty) = initial balance inventory value
- [ ] Physical inventory imported and validated via Inventory app
- [ ] Change normal loss account on virtual adjustment location post-import

### Manual Valuation

- [ ] Products set up with cost
- [ ] Inventory file collected and imported
- [ ] Verify: sum(cost * qty) = initial balance inventory value
- [ ] Confirm: Balance Sheet shows no stock valuation line (manual mode)

---

## D) Trial Balance Import

### Payment Journal Configuration

> Choose A (payment entries needed) or B (no payment entries after go-live).

**Option A — Bank journal with payment entry:**

- [ ] Create **Outstanding Receipt** and **Outstanding Payment** accounts (Current Asset, allow reconciliation)
- [ ] Add Outstanding Receipt/Payment to bank journal incoming/outgoing sections
- [ ] Map bank account to Outstanding Receipt account

**Option B — Bank journal without payment entry:**

- [ ] Create **Bank Clearing** account (Current Asset, allow reconciliation)
- [ ] Map bank account to Bank Clearing account

### Trial Balance Steps (both options)

- [ ] Prepare client original trial balance (Excel)
- [ ] Modify TB AR account → AR Clearing (exclude open customer payments)
- [ ] Modify TB AP account → AP Clearing (exclude open vendor payments)
- [ ] Modify TB Inventory account → Inventory Clearing (if automated valuation)
- [ ] Import journal entry for trial balance and post
- [ ] Verify: General Ledger → AR Clearing = 0
- [ ] Verify: General Ledger → AP Clearing = 0
- [ ] Verify: General Ledger → Inventory Clearing = 0
- [ ] **Balance Sheet ties to signed-off Trial Balance**

---

## E) Payment Provider Configuration (Azure + PH Market)

> Module: `ipai_payment_paymongo` (v18.0.1.0.0)
> Secrets: Azure Key Vault (`kv-ipai-dev`)

- [ ] PayMongo API keys vaulted in `kv-ipai-dev` (`paymongo-secret-key`, `paymongo-public-key`)
- [ ] Payment provider activated in Odoo (Accounting → Configuration → Payment Providers)
- [ ] Supported methods enabled: Credit/Debit, GCash, Maya, GrabPay, BPI/UnionBank
- [ ] Webhook endpoint registered with PayMongo (`https://erp.insightpulseai.com/payment/paymongo/webhook`)
- [ ] Test transaction completed in sandbox mode
- [ ] Production mode activated after sandbox verification

### Bank Account Configuration

- [ ] Company bank accounts created in Odoo (matching BIR-registered accounts)
- [ ] Bank journals created per account with correct outstanding receipt/payment accounts
- [ ] Bank statement import method configured (manual CSV or OCA bank-statement-import)
- [ ] Reconciliation model configured for common payment patterns

---

## 6. Integration Readiness

- [x] **Foundry endpoint** tested (gpt-4.1 live, ~3s latency) -- 2026-03-18
- [x] **AI Search** provisioned and seeded (331 docs indexed) -- 2026-03-18
- [x] **ATC crosswalk** draft complete (17 BIR-standard mappings) -- 2026-03-18
- [x] Agent-platform v0.1 runtime operational (22/22 tests passing) -- 2026-03-18
- [x] Copilot Skills framework operational (4 skills, 16 tests) -- 2026-03-18
- [ ] Supabase Edge Functions reachable from n8n (if applicable)
- [ ] n8n workflows deployed and activated (task bus, notifications)
- [ ] Slack webhooks configured for alerting

---

## 7. Security Readiness

- [ ] `proxy_mode = True` in Odoo config (required for correct IP forwarding behind AFD)
- [ ] `list_db = False` (prevents unauthenticated database enumeration)
- [ ] `admin_passwd` is set to a strong value via KV (not default `admin`)
- [ ] `dbfilter` configured to restrict database access per hostname
- [x] All secrets in Azure Key Vault (no plaintext in config files) -- DONE 2026-03-18
- [ ] HTTPS enforced on all public endpoints (AFD terminates TLS)
- [ ] WAF managed rules active on Azure Front Door
- [ ] Session cookie `secure` and `httponly` flags verified
- [ ] CORS headers configured appropriately for API endpoints
- [ ] No debug mode enabled in production (`--dev` flags removed)

---

## 8. Smoke Test Execution

> **CP-7**: All smoke tests must pass before go/no-go decision.
> Script: `scripts/odoo/smoke_test.sh` (TGT-005)

- [ ] **Login**: Admin user can log in via `erp.insightpulseai.com`
- [ ] **Sales Order**: Create SO, confirm, create invoice -- no errors
- [ ] **Invoice**: Invoice validates and posts correctly
- [ ] **Project**: Create project, add tasks, transition task states
- [ ] **Finance PPM**: Dashboard renders with seeded data (95 tasks visible)
- [ ] **Copilot**: OWL systray widget loads, Foundry endpoint responds
- [ ] **Cron**: Scheduled actions run without error in cron container logs
- [ ] **Email**: Test outbound email sends via Zoho SMTP (ir.mail_server)

---

## 9. Go/No-Go Decision

### Decision Criteria

| Category | Status | Gate |
|----------|--------|------|
| Identity (CP-1) | BLOCKED | MUST PASS |
| Storage (CP-2) | PARTIAL | MUST PASS |
| Edge/WAF (CP-3) | BLOCKED | MUST PASS |
| Cron fix (CP-4) | PARTIAL | MUST PASS |
| Pipeline (CP-5) | BLOCKED | MUST PASS |
| Tenancy (CP-6) | NOT STARTED | MUST PASS |
| Smoke test (CP-7) | NOT STARTED | MUST PASS |
| Evidence pack (CP-8) | NOT STARTED | MUST PASS |

### Evidence Pack (CP-8)

- [ ] All CP-1 through CP-7 evidence artifacts committed to `docs/delivery/evidence/poc-pack/`
- [ ] Architecture diagram reflects deployed state
- [ ] Runtime screenshots captured (login, dashboard, ACA overview)
- [ ] Azure resource inventory snapshot captured
- [ ] Demo narrative written (one-page)
- [ ] Demo script executable by one operator
- [ ] Readiness summary is reproducible (not self-reported)

### Decision

- [ ] **GO**: All MUST PASS gates are green, evidence pack is complete
- [ ] **NO-GO**: Document specific failures and remediation plan with dates

---

## Session Evidence (2026-03-18/19)

Items completed during the Phase 0-to-1 acceleration session:

| Item | Status | Evidence |
|------|--------|----------|
| Prod login (asset bundling + stale DB secret) | FIXED | Login page renders, CSS/JS serving |
| KV-backed secrets on all 3 ACA apps | DONE | All KV refs wired to web/worker/cron |
| Foundry gpt-4.1 integration | TESTED | ~3s latency, endpoint responds |
| AI Search provisioned | DONE | `srch-ipai-dev`, 331 docs indexed |
| ATC crosswalk draft | COMPLETE | 17 BIR-standard mappings |
| ipai_odoo_copilot module | BUILT | 20 files, OWL systray widget |
| ipai_finance_ppm demo data | SEEDED | 95 tasks, 4-phase close |
| Agent-platform v0.1 runtime | OPERATIONAL | 22/22 tests passing |
| Copilot Skills framework | OPERATIONAL | 4 skills, 16 tests passing |
| Azure DevOps pipelines | CREATED | ci-cd.yml in ADO project |
| All keys vaulted | DONE | foundry, search, pg-admin, ADO PAT |

---

*Last updated: 2026-03-19*
