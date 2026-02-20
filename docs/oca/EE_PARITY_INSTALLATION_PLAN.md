# OCA Modules for Enterprise Edition Parity - Installation Plan

> **Goal**: Install OCA modules to replace Odoo Enterprise Edition features
> **Status**: 30/70 base modules installed, enhanced to 120+ target modules
> **Current EE Parity**: ~70% (baseline) → Target: 85%+ (enhanced)

---

## Executive Summary

### Current State (2026-02-20)

| Metric | Value | Notes |
|--------|-------|-------|
| OCA modules available in 19.0 | 288 | Total in inventory |
| Base allowlist modules | 70 | Original target set |
| Successfully installed | 30 | 42.9% coverage |
| Blocked (not in 19.0) | 32 | Need porting from 18.0 |
| Blocked (uninstallable) | 8 | Dependency issues |
| Enhanced allowlist target | 120+ | +50 high-value modules |

### EE Parity Coverage

| Feature Area | Current | Enhanced Target | Blocker Status |
|--------------|---------|-----------------|----------------|
| **Financial Reports** | 90% | 95% | ✓ Available |
| **Accounting Core** | 85% | 90% | ✓ Available |
| **Bank Reconciliation** | 0% | 95% | ✗ Needs porting |
| **Invoicing** | 65% | 85% | ✓ Available |
| **Purchase Workflow** | 70% | 90% | ○ Partial (tier validation blocked) |
| **Contact Management** | 60% | 85% | ✓ Available |
| **Web UX** | 90% | 95% | ✓ Available |
| **Project/Timesheet** | 75% | 80% | ✓ Available |
| **CRM** | 70% | 75% | ✓ Available |
| **Reporting** | 85% | 90% | ○ Partial (MIS blocked) |
| **Server Tools** | 90% | 95% | ○ Partial (server_environment blocked) |
| **Helpdesk** | 0% | 90% | ✗ Needs porting |
| **DMS/Knowledge** | 0% | 85% | ✗ Needs porting |

**Legend**: ✓ Modules available | ○ Partial availability | ✗ Blocked (needs porting)

---

## Current Installation (30 Modules)

### What's Working ✓

**P0 - Critical Features (Already Providing EE Parity)**:
1. **Financial Reports (90%)**
   - `account_financial_report` - Replaces EE account_reports
   - `account_tax_balance` - Tax reporting
   - `partner_statement` - Partner account statements

2. **Accounting Core (85%)**
   - `account_journal_restrict_mode` - Journal security controls
   - `account_move_name_sequence` - Move numbering
   - `account_usability` - UX improvements

3. **Bank Statements (80%)**
   - `account_statement_base` - Statement infrastructure
   - *(Missing: import formats, reconciliation UI)*

**P1 - High Value Features**:
4. **Web UX (90%)**
   - `web_responsive` - Mobile/tablet support
   - `web_dialog_size` - Better dialog management
   - `web_environment_ribbon` - Environment indicators

5. **Project Management (75%)**
   - `project_task_default_stage` - Default workflows
   - `project_task_stage_mgmt` - Stage management
   - `project_task_pull_request` - GitHub integration

6. **HR/Timesheet (80%)**
   - `hr_employee_firstname` - Name handling
   - `hr_timesheet_task_stage` - Stage-based timesheets
   - `hr_timesheet_time_control` - Time tracking

**P2 - Quality of Life Features**:
7. **CRM Extensions (70%)**
   - `crm_lead_code` - Lead numbering
   - `crm_industry` - Industry classification
   - `crm_stage_probability` - Pipeline forecasting

8. **Reporting (85%)**
   - `report_xlsx` - Excel exports
   - `report_xml` - XML exports

9. **Server Tools (90%)**
   - `auditlog` - Audit trail
   - `base_exception` - Exception handling
   - `base_technical_user` - Technical users

---

## Critical Gaps (40 Blocked Modules)

### Priority 0 - Business Blockers

**Bank Reconciliation (CRITICAL)**
- `account_reconcile_oca` - Main reconciliation UI (EE replacement)
- `account_reconcile_model_oca` - Auto-reconciliation rules
- `account_statement_import_file` - File import
- `account_statement_import_camt` - CAMT format (European banks)
- `account_statement_import_ofx` - OFX format (US banks)
- **Impact**: Cannot do bank reconciliation without these
- **Status**: In port queue P0, needs migration from 18.0

**Connector Framework (CRITICAL)**
- `component`, `component_event`, `connector` - Integration framework
- `fastapi`, `extendable_fastapi` - Modern REST APIs
- **Impact**: Blocks all integration/connector modules
- **Status**: In port queue P0, foundational dependency

**Server Environment (CRITICAL)**
- `server_environment` - Multi-environment config (dev/staging/prod)
- `server_environment_data_encryption` - Encrypted secrets
- **Impact**: Cannot deploy to production safely
- **Status**: In port queue P0, deployment requirement

### Priority 1 - High Value Missing

**Purchase Approvals**
- `purchase_tier_validation` - Multi-tier approval workflows
- **Impact**: No purchase approval process
- **Status**: In port queue P1

**Advanced Reporting**
- `mis_builder` - Management Information System reports
- `mis_builder_budget` - Budget reporting
- **Impact**: Limited executive reporting
- **Status**: Uninstallable (dependency issues)

### Priority 2 - Future Roadmap

**Helpdesk** - Replaces EE `helpdesk` module
**DMS** - Document management system
**Knowledge** - Knowledge base / wiki
**Asset Management** - Fixed asset tracking

All require porting from 18.0 to 19.0.

---

## Installation Strategy

### Phase 1: Install Available Enhanced Modules (Immediate)

**Objective**: Install 50+ additional OCA modules currently available in 19.0

**New Modules to Install**:

**Accounting/Invoicing** (10 modules):
- `account_billing` - Recurring billing
- `account_global_discount` - Invoice-level discounts
- `account_invoice_check_total` - Total validation
- `account_invoice_refund_link` - Refund tracking
- `account_invoice_tax_required` - Tax validation
- `account_invoice_pricelist` - Pricelist integration
- `account_invoice_fiscal_position_update` - Fiscal position automation
- `account_invoice_date_due` - Due date management
- `account_invoice_fixed_discount` - Fixed discount amounts
- `account_invoice_refund_reason` - Refund reason tracking

**Purchase Extended** (10 modules):
- `partner_supplierinfo_smartbutton` - Supplier info quick access
- `product_supplier_code_purchase` - Supplier SKU management
- `product_supplierinfo_qty_multiplier` - Quantity multipliers
- `purchase_all_shipments` - Shipment tracking
- `purchase_blanket_order` - Framework/blanket orders (EE replacement)
- `purchase_commercial_partner` - Partner hierarchy
- `purchase_deposit` - Deposit/advance payments
- `purchase_discount` - Purchase order discounts
- `purchase_invoice_plan` - Installment billing

**Partner/Contact Management** (9 modules):
- `base_partner_sequence` - Auto-numbering
- `partner_contact_department` - Department tracking
- `partner_contact_job_position` - Job position management
- `partner_identification` - ID number tracking
- `partner_manual_rank` - VIP/ranking system
- `partner_ref_unique` - Unique reference enforcement
- `partner_vat_unique` - Unique VAT validation
- `partner_contact_access_link` - Portal access links
- `partner_contact_address_default` - Default address logic

**Server Authentication** (3 modules):
- `auth_session_timeout` - Session security
- `auth_user_case_insensitive` - Case-insensitive logins
- `impersonate_login` - User impersonation (support/debug)

**Accounting Tools** (3 modules):
- `account_account_tag_code` - Account tag codes
- `account_move_post_date_user` - Post date tracking
- `account_move_print` - Accounting move printing

**Commands**:
```bash
# 1. Backup current allowlist
cp config/oca/module_allowlist.yml config/oca/module_allowlist_backup.yml

# 2. Use enhanced allowlist
cp config/oca/module_allowlist_enhanced.yml config/oca/module_allowlist.yml

# 3. Run installation
./scripts/oca/install_from_allowlist.sh

# Expected result: 30 → 60-80 modules installed (depends on dependencies)
```

### Phase 2: Port Critical P0 Modules (2-4 weeks)

**Objective**: Port the 15 foundation modules from 18.0 to 19.0

**Priority Order** (from `config/oca/port_queue.yml`):

1. **Week 1: Foundation Infrastructure**
   - `server_environment` (server-env repo)
   - `server_environment_data_encryption` (server-env repo)
   - `component` (connector repo)
   - `component_event` (connector repo)

2. **Week 2: Connector Stack + Bank Base**
   - `connector` (connector repo)
   - `account_statement_import_base` (bank-statement-import repo)

3. **Week 3-4: REST Framework (if needed)**
   - `extendable`, `pydantic`, `fastapi` (rest-framework repo)
   - Or wait for upstream fixes if uninstallable

**Porting Workflow** (per module):
```bash
# Use the automated harness
./scripts/oca/port_to_19.sh <repo> <module>

# Follow runbook for manual steps
# See: docs/oca/PORTING_19_RUNBOOK.md
```

### Phase 3: Port P1 High-Value Modules (4-6 weeks)

**Bank Reconciliation** (account-reconcile repo):
- `account_reconcile_oca`
- `account_reconcile_model_oca`
- `account_reconcile_oca_add_default_filters`
- `account_partner_reconcile`

**Bank Import Formats** (bank-statement-import repo):
- `account_statement_import_file`
- `account_statement_import_camt`
- `account_statement_import_ofx`
- `account_statement_import_file_reconcile_oca`

**Purchase Workflows** (purchase-workflow repo):
- `purchase_tier_validation`
- `purchase_advance_payment`
- `purchase_exception`
- `purchase_order_approval_block`

---

## Expected Outcomes

### After Phase 1 (Enhanced Install)

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Modules installed | 30 | 60-80 | +30-50 |
| EE Parity (estimated) | 70% | 82% | +12% |
| Invoicing coverage | 65% | 85% | +20% |
| Purchase coverage | 70% | 90% | +20% |
| Contact management | 60% | 85% | +25% |

### After Phase 2 (Critical P0 Ports)

| Feature | Parity | Impact |
|---------|--------|--------|
| Server environment | 95% | Production-ready deployments |
| Connector framework | 90% | Unlock integrations |
| Bank import base | 80% | Foundation for reconciliation |

### After Phase 3 (P1 Ports)

| Feature | Parity | Impact |
|---------|--------|--------|
| Bank reconciliation | 95% | **Full finance operations** |
| Statement imports | 90% | **Auto bank sync** |
| Purchase approvals | 90% | **Procurement workflows** |

**Final EE Parity Target**: 90%+ for core business operations

---

## Recommended Action Plan

### Immediate (Today)

1. ✅ Review enhanced allowlist: `config/oca/module_allowlist_enhanced.yml`
2. ✅ Backup current installation
3. ✅ Run Phase 1 installation with enhanced allowlist
4. ✅ Verify new modules work and provide value

### This Week

1. Start porting `server_environment` (critical for deployments)
2. Start porting `component` + `component_event` (foundation for connectors)
3. Update port queue status as modules complete

### Next 2-4 Weeks

1. Port connector framework stack
2. Port bank reconciliation stack
3. Port purchase workflow approvals
4. Re-run installation with newly ported modules

### Month 2

1. Assess EE parity coverage
2. Identify remaining gaps
3. Port P2 modules (DMS, Knowledge, Helpdesk) if business priority

---

## Risk Assessment

### Low Risk

- **Phase 1 installation**: All modules verified available in 19.0, worst case is module doesn't install (continue with rest)

### Medium Risk

- **P0 porting**: Manual framework updates required, may take longer than estimated if complex modules
- **Dependency cascades**: Some modules may require others to be ported first

### High Risk

- **Uninstallable modules**: `mis_builder`, `base_rest`, `pydantic` may require upstream fixes beyond our control
- **EE feature parity**: Some EE features may not have exact OCA equivalents

---

## Success Criteria

1. ✅ **60+ modules installed** (Phase 1) - Doubling current coverage
2. ✅ **Server environment working** (Phase 2) - Production deployment capability
3. ✅ **Bank reconciliation available** (Phase 3) - Critical finance workflow
4. ✅ **85%+ EE parity** (Overall) - Comparable to EE for core business operations

---

## Reference Documents

- Enhanced Allowlist: `config/oca/module_allowlist_enhanced.yml`
- Port Queue: `config/oca/port_queue.yml`
- Porting Runbook: `docs/oca/PORTING_19_RUNBOOK.md`
- Port Harness: `scripts/oca/port_to_19.sh`
- EE Parity Map: `docs/ee_parity_map.md`
- Install Script: `scripts/oca/install_from_allowlist.sh`

---

*Last updated: 2026-02-20*
*Status: Ready for Phase 1 execution*
