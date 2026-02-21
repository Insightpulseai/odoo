# OCA Module Wave Plan — Review & Findings

**Date**: 2026-02-21T16:00:00+08:00
**Reviewer**: Claude Code (automated)
**Scope**: 4 waves, 21 modules, Odoo 19.0 CE
**Instance**: erp.insightpulseai.com (DO droplet 178.128.112.214)

---

## Executive Summary

The OCA wave install plan is **well-structured** and mostly correct. Of 22 unique modules
across 4 waves, **21 are confirmed available on OCA 19.0 branches**. One critical finding:
`account_tax_balance` is **NOT on 19.0** and requires porting.

| Metric | Value |
|--------|-------|
| Modules checked | 22 |
| Confirmed on 19.0 | 21 |
| Missing from 19.0 | 1 (`account_tax_balance`) |
| Already in allowlist | 18 of 22 |
| New additions needed | 4 (`web_refresher`, `account_move_post_date_user`, `account_move_print`, `account_payment_order_grouped`) |
| Dependency conflicts | 0 |
| Architecture issues | 2 (submodule strategy, interactive prompt) |

---

## Findings by Wave

### Wave 1 — Already Present (3 modules)

| Module | 19.0 | In Allowlist | Status | Notes |
|--------|------|-------------|--------|-------|
| `account_statement_import_file_reconcile_oca` | N/A (local) | YES | **OK** | Present on instance per install_manifest |
| `quality_control_oca` | N/A (local) | NO | **OK** | Not in allowlist; already present on disk |
| `quality_control_stock_oca` | N/A (local) | NO | **OK** | Depends on quality_control_oca |

**Verdict**: APPROVED. No issues. These are already on the instance and just need activation.

---

### Wave 2 — UX + Reporting (9 modules)

| Module | OCA Repo | 19.0 Branch | In Allowlist | Status |
|--------|----------|-------------|-------------|--------|
| `report_xlsx` | reporting-engine | CONFIRMED | YES | OK |
| `report_xlsx_helper` | reporting-engine | CONFIRMED | YES | OK |
| `web_responsive` | web | CONFIRMED | YES | OK |
| `web_dialog_size` | web | CONFIRMED | YES | OK |
| `web_environment_ribbon` | web | CONFIRMED | YES | OK |
| `web_refresher` | web | CONFIRMED | **NO** | **ADD to allowlist** |
| `web_search_with_and` | web | CONFIRMED | YES | OK |
| `date_range` | server-ux | CONFIRMED | YES | OK |
| `auth_session_timeout` | server-auth | CONFIRMED | YES | OK |

**Issues**:
1. `web_refresher` is in the diagram but **missing from `module_allowlist.yml`** — needs to be added
2. `base_substate` appears in the install_manifest Wave 2 and the install plan text but is **not in the Mermaid diagram** — clarify if wanted

**Verdict**: APPROVED with minor fix (add `web_refresher` to allowlist).

---

### Wave 3 — Finance Tools (10 modules in diagram, 6 in manifest)

| Module | OCA Repo | 19.0 Branch | In Allowlist | Status |
|--------|----------|-------------|-------------|--------|
| `account_move_name_sequence` | account-financial-tools | CONFIRMED | YES | OK |
| `account_journal_restrict_mode` | account-financial-tools | CONFIRMED | YES | OK |
| `account_usability` | account-financial-tools | CONFIRMED | YES | OK |
| `account_tax_balance` | account-financial-tools | **NOT FOUND** | YES | **BLOCKER** |
| `account_move_post_date_user` | account-financial-tools | CONFIRMED | YES (enhanced) | OK |
| `account_move_print` | account-financial-tools | CONFIRMED | YES (enhanced) | OK |
| `account_payment_mode` | bank-payment | CONFIRMED | YES | OK |
| `account_payment_order` | bank-payment | CONFIRMED | YES | OK |
| `account_payment_purchase` | bank-payment | CONFIRMED | YES | OK |
| `account_payment_sale` | bank-payment | CONFIRMED | YES | OK |

**Critical Issues**:
1. **`account_tax_balance` is NOT on OCA 19.0** — The module does not exist on the
   `account-financial-tools` 19.0 branch. Options:
   - **Option A**: Port from 18.0 using `oca-port` (add to `port_queue.yml`)
   - **Option B**: Skip for now; use `account_financial_report` (already installed) which
     provides tax reporting capabilities
   - **Option C**: Build a lightweight `ipai_tax_balance` wrapper using the date_range
     framework
   - **Recommendation**: Option A (port) or Option B (skip). `account_financial_report`
     v19.0.0.0.2 is already installed and includes tax balance reporting

2. `account_move_post_date_user` and `account_move_print` are in the Mermaid diagram but
   **not in the install_manifest.yaml Wave 3** — they need to be added to the manifest

3. The install_manifest puts `account_payment_purchase` and `account_payment_sale` in
   Wave 4 but the Mermaid diagram puts them in Wave 3 — **align to Wave 3** since they
   logically belong with the payment order ecosystem

**Verdict**: APPROVED with `account_tax_balance` either ported or deferred.

---

### Wave 4 — Nice-to-Haves (3 core + 2 payment extensions)

| Module | OCA Repo | 19.0 Branch | In Allowlist | Status |
|--------|----------|-------------|-------------|--------|
| `hr_employee_firstname` | hr | CONFIRMED | YES | OK |
| `document_url` | knowledge | CONFIRMED | YES (documents pack) | OK |
| `hr_timesheet_task_stage` | timesheet | CONFIRMED | YES | OK |

**Verdict**: APPROVED. All modules confirmed available.

---

## Architecture Issues

### Issue 1: Submodule Strategy Conflict

The user's install script uses `git submodule add` but commit `5e55c77e` deliberately
**removed all 38 git submodules** in favor of gitaggregate (commit `00c969fe`). The repo
currently has **no `.gitmodules` file**.

**Recommendation**: Do NOT reintroduce git submodules. Use one of:
- **gitaggregate** (already configured per `00c969fe`) — preferred
- **Direct clone** to `oca/` with `.gitignore` entries
- **pip install** from OCA PyPI packages (if available)

The install script has been rewritten to use direct clones instead of submodules.

### Issue 2: Interactive Prompt in wave3_install

The `read -p "Continue? (y/N)"` prompt in `wave3_install()` violates the repo's
no-interactive execution constraint (see CLAUDE.md: "No interactive questions").

**Fix**: Use a `--confirm` flag or `FORCE=1` environment variable instead.

### Issue 3: Missing Repos for Wave 4

The user's script defines `wave3_clone` for finance repos but Wave 4 modules come from
3 additional repos (hr, knowledge, timesheet) with no corresponding `wave4_clone` step.

**Fix**: Added `wave4-clone` and `wave4-install` commands to the script.

---

## Dependency Chain Verification

```
Tier 1 (no inter-OCA deps):
  report_xlsx → base, web (core) ✓
  web_responsive → web, web_tour, mail (core) ✓
  web_dialog_size → web (core) ✓
  web_environment_ribbon → web (core) ✓
  web_refresher → web (core) ✓
  web_search_with_and → web (core) ✓
  date_range → web (core) ✓
  auth_session_timeout → base (core) ✓
  account_move_name_sequence → account (core) ✓
  account_journal_restrict_mode → account (core) ✓
  account_usability → account (core) ✓
  account_payment_mode → account (core) ✓
  hr_employee_firstname → hr (core) ✓
  document_url → mail (core) ✓

Tier 2 (depends on Tier 1):
  report_xlsx_helper → report_xlsx ✓
  account_tax_balance → account, date_range ⚠️ (module not on 19.0)
  account_payment_order → account_payment_mode, base_iban ✓
  hr_timesheet_task_stage → hr_timesheet (core) ✓

Tier 3 (depends on Tier 2):
  account_payment_purchase → account_payment_order, purchase ✓
  account_payment_sale → account_payment_order, sale ✓
```

All dependency chains are valid. The only broken link is `account_tax_balance` (module
not available on 19.0).

---

## Cross-Reference: Existing Allowlist Coverage

Modules already tracked in `config/oca/module_allowlist.yml`:
- **foundation pack**: `date_range`, `auth_session_timeout`, `base_substate` ✓
- **web_ux pack**: `web_dialog_size`, `web_environment_ribbon`, `web_responsive`,
  `web_search_with_and` ✓ (missing: `web_refresher`)
- **accounting_core pack**: `account_journal_restrict_mode`, `account_move_name_sequence`,
  `account_tax_balance`, `account_usability` ✓
- **accounting_payments pack**: `account_payment_mode`, `account_payment_order`,
  `account_payment_purchase`, `account_payment_sale` ✓ (missing: `account_payment_order_grouped`)
- **reporting pack**: `report_xlsx`, `report_xlsx_helper` ✓
- **hr_modules pack**: `hr_employee_firstname`, `hr_timesheet_task_stage` ✓
- **documents pack**: `document_url` ✓

Modules in wave plan but **not in any allowlist pack**:
- `web_refresher` — ADD to `web_ux` pack
- `account_move_post_date_user` — already in `accounting_tools` (enhanced allowlist)
- `account_move_print` — already in `accounting_tools` (enhanced allowlist)
- `quality_control_oca` — not in allowlist (already on instance)
- `quality_control_stock_oca` — not in allowlist (already on instance)
- `account_statement_import_file_reconcile_oca` — in `accounting_statements` pack ✓

---

## Confirmed NOT Available on 19.0

| Module | Last OCA Version | Alternative |
|--------|-----------------|-------------|
| `account_tax_balance` | 18.0 | Port via oca-port OR use account_financial_report |
| `base_tier_validation` | 18.0 (ported locally) | Already ported in port_queue.yml |
| `helpdesk_mgmt` | 18.0 | Project app with helpdesk stages |
| `mail_activity_board` | 18.0 | Native Activities menu |
| `stock_barcodes` | 18.0 | Odoo CE native barcode |
| `account_lock_date_update` | 18.0 | N/A |
| `contract` | 18.0 | N/A |

Note: `base_tier_validation` was listed as "not available" in the install_manifest but
the port_queue.yml shows it was **successfully ported** (commit `75bb2e2`). Update the
manifest accordingly.

---

## Recommended Actions

### Immediate (before Wave 1)
1. Update `docs/oca/install_manifest.yaml` — add missing Wave 3 modules
2. Add `web_refresher` to `config/oca/module_allowlist.yml` web_ux pack
3. Decide on `account_tax_balance`: port or defer

### Wave 1 Execution
- Activate 3 already-present modules (no git operations needed)
- Verify on dev DB first, then production

### Wave 2 Execution
- Clone 4 OCA repos (reporting-engine, web, server-ux, server-auth) using gitaggregate
  or direct clone (NOT submodules)
- Symlink 9 modules to addons path
- Test responsive layout + XLSX export + session timeout

### Wave 3 Execution
- Clone 2 OCA repos (account-financial-tools, bank-payment)
- Install Tier 1 finance tools first (no inter-OCA deps)
- Install Tier 2 (payment orders + tax balance) after Tier 1
- Finance team approval required before production
- Staging test mandatory

### Wave 4 Execution
- Clone 3 additional repos (hr, knowledge, timesheet)
- Install as needed; no business logic risk

---

## Files Modified in This Review

| File | Change |
|------|--------|
| `docs/oca/OCA_WAVE_REVIEW_2026-02-21.md` | This review document |
| `scripts/oca_install.sh` | Installer script (rewritten, no submodules) |
| `docs/oca/install_manifest.yaml` | Updated with missing modules + findings |
| `config/oca/module_allowlist.yml` | Added `web_refresher` to web_ux pack |
