# Knowledge Base Review Queue

> Track review status of generated seed files before promoting to canonical/SSOT.

## Review Levels

| Level | Meaning |
|-------|---------|
| **unreviewed** | Generated, not yet validated |
| **spot-checked** | Key claims verified, minor corrections applied |
| **validated** | Full review, factual accuracy confirmed |
| **promoted** | Moved to or referenced from `ssot/` as canonical |

## Queue

| File | Owner | Status | Review Depth | Promote to SSOT? | Notes |
|------|-------|--------|-------------|-------------------|-------|
| `capability-map/capability-taxonomy.yaml` | — | spot-checked | codebase | candidate | 2 errors fixed (fixed_assets, helpdesk marked Enterprise-only). All Odoo model refs verified. OCA module names confirmed on disk. MRP/analytic plans confirmed CE. |
| `benchmark/sap-to-odoo-matrix.yaml` | — | spot-checked | codebase | candidate | 2 errors fixed (fixed_assets CE claim, helpdesk CE claim). OCA modules verified: mis_builder, bi_sql_editor, purchase_request, purchase_blanket_order, queue_job, connector, auth_oidc, account_payment_order, base_tier_validation all on disk. Spreadsheet confirmed CE. |
| `benchmark/gap-analysis.md` | — | spot-checked | derivative | no (derivative) | Fixed assets correctly classified as O (OCA). No helpdesk claim. Consistent with corrected matrix. |
| `ontology/entities.yaml` | — | spot-checked | codebase | candidate | 23/23 Odoo models verified against vendor/odoo/ source. OCA addons confirmed: base_user_role (server-backend), auth_oidc (server-auth), base_tier_validation (server-ux), all partner/purchase/sale/project/hr modules. |
| `ontology/glossary.yaml` | — | unreviewed | — | candidate | Verify SAP term accuracy and Odoo implementation mappings |
| `ontology/relationships.yaml` | — | unreviewed | — | candidate | Cross-check process-to-model mappings against actual install |
| `evaluation/scenarios.yaml` | — | validated | codebase | candidate | 13/13 claims verified against source. move_type values confirmed (account_move.py:160-177). ir.rule OR/AND logic confirmed (ir_rule.py:94,168). analytic plans confirmed CE. Studio confirmed EE-only. |
| `evaluation/scoring-rubric.md` | — | unreviewed | — | no (methodology) | Review thresholds for reasonableness |
| `evaluation/risks-blind-spots.md` | — | unreviewed | — | no (living doc) | Update as risks materialize or are mitigated |
| `learning/phases.yaml` | — | unreviewed | — | no (planning) | Validate exercise feasibility |
| `learning/execution-plan-30-60-90.md` | — | unreviewed | — | no (planning) | Adjust timeline based on actual progress |
| `skill-packs/enterprise-finance/SKILL.md` | — | unreviewed | — | no (reference) | Verify OCA module names exist at 18.0 |
| `skill-packs/procure-to-pay/SKILL.md` | — | unreviewed | — | no (reference) | Verify 3-way match OCA claims |
| `skill-packs/order-to-cash/SKILL.md` | — | unreviewed | — | no (reference) | Verify process steps match CE behavior |
| `skill-packs/record-to-report/SKILL.md` | — | spot-checked | codebase | no (reference) | Fixed account.asset CE claim → corrected to OCA-only |
| `skill-packs/inventory-warehouse/SKILL.md` | — | unreviewed | — | no (reference) | Verify MRP claims in CE |
| `skill-packs/management-accounting/SKILL.md` | — | unreviewed | — | no (reference) | Verify analytic plan features in CE 18 |
| `skill-packs/project-portfolio/SKILL.md` | — | unreviewed | — | no (reference) | Verify timesheet billing model |
| `skill-packs/tax-compliance-ph/SKILL.md` | — | spot-checked | codebase + rates file | no (reference) | Corrected: removed 15% EWT (max 10%), fixed ATC codes (W157/W158 not WI010/WC010), qualified FWT rates (max 20% in rates file), marked 3 OCA modules as not-on-disk, marked 3 ipai modules as planned, added `ipai_bir_tax_compliance` as available, BIR 2307 clarified as core `l10n_ph` |
| `skill-packs/reporting-bi/SKILL.md` | — | unreviewed | — | no (reference) | Verify MIS Builder and bi_sql_editor capabilities |
| `skill-packs/identity-rbac-sod/SKILL.md` | — | unreviewed | — | no (reference) | Verify SoD implementation claims |
| `skill-packs/copilot-agent-erp/SKILL.md` | — | unreviewed | — | no (reference) | Verify MCP tool patterns are current |
| `patterns/architecture/enterprise-erp-patterns.md` | — | unreviewed | — | no (reference) | Validate code examples compile |
| `patterns/anti-patterns/enterprise-anti-patterns.md` | — | unreviewed | — | no (reference) | Review for completeness |
| `patterns/integration/integration-patterns.md` | — | unreviewed | — | no (reference) | Verify Azure service names and auth patterns |
| `process-maps/order-to-cash.md` | — | unreviewed | — | no (reference) | Walk through on odoo_dev |
| `process-maps/procure-to-pay.md` | — | unreviewed | — | no (reference) | Walk through on odoo_dev |
| `process-maps/record-to-report.md` | — | unreviewed | — | no (reference) | Walk through on odoo_dev |
| `domain-primers/*.md` | — | unreviewed | — | no (reference) | Light review sufficient |
| `checklists/*.md` | — | unreviewed | — | no (reference) | Test against actual module creation |
| `decision-records/ADR-001-*.md` | — | unreviewed | — | no (ADR) | Verify rationale still holds |

## Review Priority

1. `capability-taxonomy.yaml` — foundational; everything else references it
2. `sap-to-odoo-matrix.yaml` — highest risk of hallucinated SAP mappings
3. `ontology/entities.yaml` — agents will reason from this; errors cascade
4. `evaluation/scenarios.yaml` — used for capability assessment; must be accurate
5. `skill-packs/tax-compliance-ph/SKILL.md` — legal/regulatory; errors are costly
