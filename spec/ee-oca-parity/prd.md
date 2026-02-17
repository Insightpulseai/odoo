# EE-OCA Parity — Product Requirements

> **Version**: 1.0.0
> **Date**: 2026-02-17
> **Spec**: `spec/ee-oca-parity/`

---

## Problem Statement

Odoo Enterprise contains ~228 modules not available in Community Edition.
InsightPulseAI replaces these via OCA addons, external service bridges, and
thin connectors — but "a mapping exists" is not the same as "parity achieved".

The parity proof (`reports/ee_oca_parity_proof.json`) currently demonstrates
**Tier 1 (Mapped)** coverage: every EE module has an identified replacement.
This PRD defines what it takes to reach Tier 4 (Verified) and what CI must
enforce along the way.

---

## What "Parity" Means (and Doesn't)

### Parity IS

- Every EE-only **module** has an OCA addon that covers ≥80% of its feature surface
- Every EE-only **capability** has an integration bridge or external service
- Replacements install cleanly on our Odoo 19 CE baseline
- Replacements are tested against our actual workflows, not hypothetical ones
- Evidence is machine-readable, auditable, and versioned

### Parity IS NOT

- 1:1 UI clone of Enterprise (different UX is acceptable if functional)
- Feature-complete replacement of every EE edge case
- Permanent — OCA evolves, upstream evolves, mappings need refresh
- A reason to build custom modules (OCA first, always)

---

## Evidence Tier Requirements

### T1: Mapped (Current State)

**What we have**: 151 EE modules mapped to OCA/CE/external replacements.

**Evidence**: `reports/ee_oca_parity_proof.json` + `docs/evidence/*/parity/`

**Gaps at T1**: No installability proof, no functional testing.

### T2: Installable

**Requirement**: Each OCA module installs on our Odoo 19 CE instance.

**Evidence required per module**:
```json
{
  "module": "account_asset_management",
  "odoo_version": "19.0",
  "install_exit_code": 0,
  "install_log_hash": "sha256:...",
  "tested_date": "2026-MM-DD",
  "tested_by": "ci/manual"
}
```

**Automation**: `scripts/ci/test_oca_install.sh` runs `odoo-bin -i <module> --stop-after-init`
for each mapped OCA module and records results.

### T3: Functional

**Requirement**: Each replacement covers ≥80% of EE feature surface for IPAI workflows.

**Evidence required per domain**:
```markdown
# Functional Parity Checklist: <domain>
- [x] Core feature A works
- [x] Core feature B works
- [ ] Edge case C: not needed for IPAI workflows
- [x] Integration with related modules verified
```

**Stored in**: `docs/evidence/<date>/parity/<domain>_functional.md`

### T4: Verified

**Requirement**: 30-day soak in staging, production deploy with rollback plan.

**Evidence required**:
- Staging deploy log
- 30-day monitoring report (no regressions)
- Production deploy confirmation
- Rollback plan document

---

## Directory Boundary Rules

These are enforced by CI gate `scripts/ci/check_parity_boundaries.sh`:

| Rule ID | Rule | Enforcement |
|---------|------|-------------|
| PB-001 | Every `addons/oca/*` must have `__manifest__.py` | CI blocks PR |
| PB-002 | Every `addons/ipai/*` must have `__manifest__.py` | CI blocks PR |
| PB-003 | Every `addons/ipai/*` must match pattern `ipai_*` | CI blocks PR |
| PB-004 | No `bridges/*` may have `__manifest__.py` | CI blocks PR |
| PB-005 | No `addons/ipai/*` module may exceed 1000 LOC Python | CI warns |
| PB-006 | `addons/_deprecated/` contents are excluded from parity counts | CI skip |
| PB-007 | No `addons/` subdirectory may lack `__manifest__.py` (except `oca/`, `ipai/`, `_deprecated/`) | CI blocks PR |

---

## Parity Report Schema

The parity report (`reports/ee_oca_parity_proof.json`) must include per module:

```json
{
  "ee_module": "helpdesk",
  "domain": "helpdesk",
  "description": "Helpdesk / Ticketing System",
  "strategy": "oca",
  "tier": "T1",
  "oca_repos": [{"ref": "OCA/helpdesk", "exists": true, "url": "..."}],
  "oca_modules": ["helpdesk_mgmt", "helpdesk_mgmt_project"],
  "ipai_modules": [],
  "external_service": null,
  "notes": "...",
  "evidence": {
    "t1_mapped": true,
    "t2_installable": null,
    "t3_functional": null,
    "t4_verified": null
  }
}
```

---

## Non-Goals

- Replacing Odoo.sh hosting (that's `spec/odoo-sh-clone/`)
- Building EE-equivalent UI themes (functional parity, not visual parity)
- Supporting multiple Odoo versions (19.0 only)
- Replacing Odoo IAP services with self-hosted equivalents at T1 (external APIs are fine)

---

## Success Criteria

| Milestone | Criteria | Target |
|-----------|----------|--------|
| T1 Complete | 100% EE modules mapped with verified OCA repos | Done (2026-02-17) |
| T2 Batch 1 | Top 20 OCA modules install on our baseline | 2026-Q1 |
| T2 Complete | All mapped OCA modules install cleanly | 2026-Q2 |
| T3 Batch 1 | Accounting + Helpdesk domains functionally tested | 2026-Q2 |
| T3 Complete | All domains functionally tested | 2026-Q3 |
| T4 Batch 1 | Accounting + Helpdesk in production | 2026-Q3 |
