# IPAI OCA Must-Have Meta

Meta-module for one-command installation of all OCA Must-Have modules (no CE19 overlap).

## Purpose

Install the minimal viable OCA layer for Odoo 19 CE, explicitly excluding modules absorbed into core.

This meta-module provides a curated, conflict-free set of 67 OCA modules that enhance Odoo 19 CE without duplicating core functionality.

## Installation

```bash
# One-command installation (all 67 modules)
odoo-bin -d your_database -i ipai_oca_musthave_meta

# Update existing installation
odoo-bin -d your_database -u ipai_oca_musthave_meta
```

## Excluded Modules (CE19 Overlap)

The following modules are **explicitly excluded** because they're absorbed into Odoo CE17+ core:

- `web_advanced_search` - Absorbed into CE17+ core search functionality
- `mail_activity_plan` - Absorbed into CE17+ core activity planning

**Impact:** Installing these modules would cause dependency conflicts with Odoo 19 CE core.

**Replacement:** Use built-in Odoo CE19 features instead.

## Module Count

| Metric | Count |
|--------|-------|
| **Total Candidates** | 69 modules |
| **Excluded** | 2 modules (CE19 overlap) |
| **Installed** | 67 modules |

## Categories

| Category | Modules | Description |
|----------|---------|-------------|
| **Base** | 26 | Server tools, web widgets, queue management |
| **Accounting** | 18 | Financial tools, reporting, reconciliation |
| **Sales** | 11 | Sales workflows, order management |
| **Purchases** | 12 | Procurement workflows, vendor management |

### Base Category (26 modules)

**Server Tools (13):**
- base_technical_features, base_search_fuzzy, base_exception
- base_tier_validation, base_user_role, base_jsonify
- base_sparse_field, base_suspend_security, base_custom_info
- base_menu_visibility_restriction, base_technical_user
- base_fontawesome, base_import_async

**Queue (1):**
- queue_job

**Web Widgets & Tools (12):**
- web_widget_x2many_2d_matrix, web_refresher, web_domain_field
- web_pwa_oca, web_notify, web_m2x_options, web_responsive
- web_timeline, web_widget_digitized_signature, web_dialog_size
- web_search_with_and, web_ir_actions_act_multi

### Accounting Category (18 modules)

- account_fiscal_year, account_move_line_purchase_info
- account_move_line_sale_info, account_invoice_refund_link
- account_usability, account_payment_partner, account_tag_menu
- account_type_menu, account_move_tier_validation
- account_statement_import, account_lock_to_date
- account_invoice_constraint_chronology, account_cost_center
- account_journal_lock_date, account_reconcile_oca
- account_invoice_view_payment, account_chart_update
- account_financial_report

### Sales Category (11 modules)

- sale_automatic_workflow, sale_exception, sale_tier_validation
- sale_order_type, sale_order_invoicing_grouping_criteria
- sale_order_line_date, sale_delivery_state
- sale_stock_mto_as_mts_orderpoint, sale_order_priority
- sale_force_invoiced, sale_validity

### Purchases Category (12 modules)

- purchase_exception, purchase_tier_validation, purchase_order_type
- purchase_order_line_price_history, purchase_order_secondary_unit
- purchase_last_price_info, purchase_work_acceptance
- purchase_landed_cost, purchase_discount, purchase_order_analytic
- purchase_order_approved, purchase_security

## Governance & Documentation

### Specification Bundle

**Location:** `spec/oca-musthave-no-ce19-overlap/`

**Files:**
- `constitution.md` - Governance principles and hard constraints
- `prd.md` - Product requirements and acceptance criteria
- `plan.md` - 4-phase implementation pipeline
- `tasks.md` - Task breakdown with verification

### Decision Documentation

**Decision Matrix:** `docs/oca/musthave/decision_matrix.md`
- All 69 candidate modules documented
- INCLUDE/EXCLUDE decisions with rationale
- Evidence references for exclusions

**Install Sets:** `docs/oca/musthave/install_sets.yml`
- 5 install sets (base, accounting, sales, purchases, all)
- YAML manifests for selective installation
- Usage examples and validation commands

### Filter Algorithm

**Script:** `scripts/oca_musthave/check_overlap.py`
- Deterministic CE19 overlap detection
- Exit codes for CI integration
- JSON output for automation

## Usage Examples

### Full Installation (All 67 modules)

```bash
odoo-bin -d production -i ipai_oca_musthave_meta
```

### Selective Installation by Category

```bash
# Base modules only (26 modules)
odoo-bin -d production -i $(yq '.sets.musthave_base.modules | join(",")' \
  docs/oca/musthave/install_sets.yml)

# Accounting modules only (18 modules)
odoo-bin -d production -i $(yq '.sets.musthave_accounting.modules | join(",")' \
  docs/oca/musthave/install_sets.yml)
```

### Verification

```bash
# Verify no CE19 overlaps
python scripts/oca_musthave/check_overlap.py --test-exclusions

# Validate install sets structure
python -c "
import yaml
with open('docs/oca/musthave/install_sets.yml') as f:
    data = yaml.safe_load(f)
    assert len(data['sets']['musthave_all']['modules']) == 67
    print('✅ Install sets validated')
"

# Verify meta-module dependencies
python -c "
import ast
with open('addons/ipai/ipai_oca_musthave_meta/__manifest__.py') as f:
    manifest = ast.literal_eval(f.read())
    assert len(manifest['depends']) == 67
    print('✅ Meta-module validated')
"
```

## Version Policy

**Odoo Version:** 19.0
**OCA Branches:** 19.0
**Review Frequency:** Quarterly (or when CE20 release approaches)

### Maintenance

- Monitor OCA repository changes for new modules
- Review Odoo CE release notes for new absorptions
- Update exclusion list when CE incorporates OCA functionality
- Quarterly audit of decision matrix against CE changelog

## CI/CD Integration

**Workflow:** `.github/workflows/oca-must-have-gate.yml`

**Validation Jobs:**
- CE19 overlap detection (strict mode)
- Install sets structure validation
- Meta-module dependency sync verification
- Drift detection for manifest changes

## References

- **Spec Bundle:** `/spec/oca-musthave-no-ce19-overlap/`
- **Decision Matrix:** `/docs/oca/musthave/decision_matrix.md`
- **Install Sets:** `/docs/oca/musthave/install_sets.yml`
- **Filter Script:** `/scripts/oca_musthave/check_overlap.py`
- **OCA Workflow:** `/docs/ai/OCA_WORKFLOW.md`
- **Git-Aggregator Config:** `/config/oca-repos.yaml`

## License

LGPL-3

## Author

InsightPulse AI - https://insightpulseai.com

---

**Last Updated:** 2026-02-15
**Module Version:** 19.0.1.0.0
