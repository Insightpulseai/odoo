# OCA Must-Have Decision Matrix

**Version:** 1.0.0
**Date:** 2026-02-15
**Total Modules:** 69 candidates → 67 post-filter (2 exclusions)
**Policy:** Explicit CE19 overlap detection

---

## Summary

| Category | Candidates | Included | Excluded |
|----------|------------|----------|----------|
| Base | 28 | 26 | 2 |
| Accounting | 18 | 18 | 0 |
| Sales | 11 | 11 | 0 |
| Purchases | 12 | 12 | 0 |
| **Total** | **69** | **67** | **2** |

---

## Decision Legend

- **INCLUDE**: No CE19 overlap detected, approved for installation
- **EXCLUDE**: Absorbed into Odoo CE17+ core, causes conflicts
- **REVIEW_REQUIRED**: Partial overlap or unclear status (none in v1.0)

---

## Base Category (28 modules → 26 included)

| Module | Decision | Rationale | Evidence |
|--------|----------|-----------|----------|
| base_technical_features | INCLUDE | No CE overlap, essential technical features | OCA/server-tools |
| base_search_fuzzy | INCLUDE | No CE overlap, fuzzy search enhancement | OCA/server-tools |
| base_exception | INCLUDE | No CE overlap, exception handling framework | OCA/server-tools |
| base_tier_validation | INCLUDE | No CE overlap, approval workflows | OCA/server-tools |
| base_user_role | INCLUDE | No CE overlap, role-based access control | OCA/server-tools |
| base_jsonify | INCLUDE | No CE overlap, JSON serialization | OCA/server-tools |
| base_sparse_field | INCLUDE | No CE overlap, sparse field support | OCA/server-tools |
| base_suspend_security | INCLUDE | No CE overlap, security context management | OCA/server-tools |
| base_custom_info | INCLUDE | No CE overlap, custom field management | OCA/server-tools |
| base_menu_visibility_restriction | INCLUDE | No CE overlap, menu access control | OCA/server-tools |
| base_technical_user | INCLUDE | No CE overlap, technical user mode | OCA/server-tools |
| base_fontawesome | INCLUDE | No CE overlap, FontAwesome icon support | OCA/server-tools |
| base_import_async | INCLUDE | No CE overlap, async import operations | OCA/server-tools |
| queue_job | INCLUDE | No CE overlap, job queue system | OCA/queue |
| web_widget_x2many_2d_matrix | INCLUDE | No CE overlap, 2D matrix widget | OCA/web |
| **web_advanced_search** | **EXCLUDE** | **Absorbed into CE17+ core search** | **[odoo/odoo CE17 release notes]** |
| **mail_activity_plan** | **EXCLUDE** | **Absorbed into CE17+ core activity planning** | **[odoo/odoo CE17 release notes]** |
| web_refresher | INCLUDE | No CE overlap, auto-refresh functionality | OCA/web |
| web_domain_field | INCLUDE | No CE overlap, domain field widget | OCA/web |
| web_pwa_oca | INCLUDE | No CE overlap, progressive web app support | OCA/web |
| web_notify | INCLUDE | No CE overlap, notification system | OCA/web |
| web_m2x_options | INCLUDE | No CE overlap, many2one/many2many options | OCA/web |
| web_responsive | INCLUDE | No CE overlap, responsive web design | OCA/web |
| web_timeline | INCLUDE | No CE overlap, timeline view widget | OCA/web |
| web_widget_digitized_signature | INCLUDE | No CE overlap, signature widget | OCA/web |
| web_dialog_size | INCLUDE | No CE overlap, dialog size control | OCA/web |
| web_search_with_and | INCLUDE | No CE overlap, AND search operator | OCA/web |
| web_ir_actions_act_multi | INCLUDE | No CE overlap, multi-action support | OCA/web |

---

## Accounting Category (18 modules → 18 included)

| Module | Decision | Rationale | Evidence |
|--------|----------|-----------|----------|
| account_fiscal_year | INCLUDE | No CE overlap, fiscal year management | OCA/account-financial-tools |
| account_move_line_purchase_info | INCLUDE | No CE overlap, purchase info in move lines | OCA/account-financial-tools |
| account_move_line_sale_info | INCLUDE | No CE overlap, sale info in move lines | OCA/account-financial-tools |
| account_invoice_refund_link | INCLUDE | No CE overlap, invoice-refund linking | OCA/account-financial-tools |
| account_usability | INCLUDE | No CE overlap, accounting UX improvements | OCA/account-financial-tools |
| account_payment_partner | INCLUDE | No CE overlap, partner payment management | OCA/account-financial-tools |
| account_tag_menu | INCLUDE | No CE overlap, account tag menu | OCA/account-financial-tools |
| account_type_menu | INCLUDE | No CE overlap, account type menu | OCA/account-financial-tools |
| account_move_tier_validation | INCLUDE | No CE overlap, move approval workflows | OCA/account-financial-tools |
| account_statement_import | INCLUDE | No CE overlap, bank statement import | OCA/account-financial-tools |
| account_lock_to_date | INCLUDE | No CE overlap, accounting lock date | OCA/account-financial-tools |
| account_invoice_constraint_chronology | INCLUDE | No CE overlap, invoice chronology validation | OCA/account-financial-tools |
| account_cost_center | INCLUDE | No CE overlap, cost center accounting | OCA/account-analytic |
| account_journal_lock_date | INCLUDE | No CE overlap, journal lock date | OCA/account-financial-tools |
| account_reconcile_oca | INCLUDE | No CE overlap, reconciliation tools | OCA/account-reconcile |
| account_invoice_view_payment | INCLUDE | No CE overlap, invoice payment view | OCA/account-financial-tools |
| account_chart_update | INCLUDE | No CE overlap, chart of accounts update | OCA/account-financial-tools |
| account_financial_report | INCLUDE | No CE overlap, financial reporting | OCA/account-financial-reporting |

---

## Sales Category (11 modules → 11 included)

| Module | Decision | Rationale | Evidence |
|--------|----------|-----------|----------|
| sale_automatic_workflow | INCLUDE | No CE overlap, automated sales workflows | OCA/sale-workflow |
| sale_exception | INCLUDE | No CE overlap, sales exception handling | OCA/sale-workflow |
| sale_tier_validation | INCLUDE | No CE overlap, sales approval workflows | OCA/sale-workflow |
| sale_order_type | INCLUDE | No CE overlap, sales order types | OCA/sale-workflow |
| sale_order_invoicing_grouping_criteria | INCLUDE | No CE overlap, invoice grouping | OCA/sale-workflow |
| sale_order_line_date | INCLUDE | No CE overlap, line-level dates | OCA/sale-workflow |
| sale_delivery_state | INCLUDE | No CE overlap, delivery state tracking | OCA/sale-workflow |
| sale_stock_mto_as_mts_orderpoint | INCLUDE | No CE overlap, MTO/MTS conversion | OCA/sale-workflow |
| sale_order_priority | INCLUDE | No CE overlap, order priority management | OCA/sale-workflow |
| sale_force_invoiced | INCLUDE | No CE overlap, force invoice state | OCA/sale-workflow |
| sale_validity | INCLUDE | No CE overlap, quotation validity dates | OCA/sale-workflow |

---

## Purchases Category (12 modules → 12 included)

| Module | Decision | Rationale | Evidence |
|--------|----------|-----------|----------|
| purchase_exception | INCLUDE | No CE overlap, purchase exception handling | OCA/purchase-workflow |
| purchase_tier_validation | INCLUDE | No CE overlap, purchase approval workflows | OCA/purchase-workflow |
| purchase_order_type | INCLUDE | No CE overlap, purchase order types | OCA/purchase-workflow |
| purchase_order_line_price_history | INCLUDE | No CE overlap, price history tracking | OCA/purchase-workflow |
| purchase_order_secondary_unit | INCLUDE | No CE overlap, secondary UoM support | OCA/purchase-workflow |
| purchase_last_price_info | INCLUDE | No CE overlap, last price information | OCA/purchase-workflow |
| purchase_work_acceptance | INCLUDE | No CE overlap, work acceptance workflows | OCA/purchase-workflow |
| purchase_landed_cost | INCLUDE | No CE overlap, landed cost calculation | OCA/purchase-workflow |
| purchase_discount | INCLUDE | No CE overlap, purchase discounts | OCA/purchase-workflow |
| purchase_order_analytic | INCLUDE | No CE overlap, analytic account integration | OCA/purchase-workflow |
| purchase_order_approved | INCLUDE | No CE overlap, approval state management | OCA/purchase-workflow |
| purchase_security | INCLUDE | No CE overlap, purchase security enhancements | OCA/purchase-workflow |

---

## Excluded Modules (Detailed)

### 1. web_advanced_search

**Category:** Base
**Decision:** EXCLUDE
**Rationale:** Absorbed into Odoo CE17+ core search functionality
**Evidence:** [odoo/odoo CE17 release notes - search improvements]
**Impact:** Dependency conflicts with core web module
**Replacement:** Use built-in Odoo CE19 advanced search features

**Technical Details:**
- CE17+ includes native advanced search with filter builder
- Installing OCA module causes web asset conflicts
- Core implementation supersedes OCA functionality

---

### 2. mail_activity_plan

**Category:** Base
**Decision:** EXCLUDE
**Rationale:** Absorbed into Odoo CE17+ core activity planning
**Evidence:** [odoo/odoo CE17 release notes - activity planning]
**Impact:** Duplicates core mail/activity functionality
**Replacement:** Use built-in Odoo CE19 activity plan templates

**Technical Details:**
- CE17+ includes activity plan templates and automation
- Installing OCA module creates duplicate models
- Core implementation provides superior integration

---

## Validation

**Generated:** 2026-02-15
**Tool:** Manual compilation from spec bundle
**Verification:** All 69 modules documented

```bash
# Verify row count (69 modules + headers)
grep -c "^|" decision_matrix.md
# Expected: 70+ (accounting for section headers)

# Verify exclusions
grep -c "| EXCLUDE |" decision_matrix.md
# Expected: 2

# Verify inclusions
grep -c "| INCLUDE |" decision_matrix.md
# Expected: 67
```

---

## References

- **Constitution:** [spec/oca-musthave-no-ce19-overlap/constitution.md](../../../spec/oca-musthave-no-ce19-overlap/constitution.md)
- **PRD:** [spec/oca-musthave-no-ce19-overlap/prd.md](../../../spec/oca-musthave-no-ce19-overlap/prd.md)
- **Filter Script:** [scripts/oca_musthave/check_overlap.py](../../../scripts/oca_musthave/check_overlap.py)
- **OCA Workflow:** [docs/ai/OCA_WORKFLOW.md](../../ai/OCA_WORKFLOW.md)

---

**Last Updated:** 2026-02-15
**Next Review:** Quarterly (or when CE20 release approaches)
