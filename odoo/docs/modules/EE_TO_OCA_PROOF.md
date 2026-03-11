# EE→OCA Parity: Why Universal Replacement Is Not Provable

## The Claim

> "All Odoo Enterprise-only modules have OCA replacements."

This claim is **globally false**. OCA provides many replacements and alternatives, but:

1. Some EE features are **platform services** (IAP, Odoo.sh, Studio) — not just modules. OCA can provide *alternatives* but not always 1:1 replacements with the same UX and backing services.
2. Some OCA alternatives are **partial/adjacent** — they cover the business outcome but not the full EE experience.
3. Community analyses acknowledge that EE implementations can be more polished and that OCA alternatives are not always equivalent ([source](https://oec.sh/blog/odoo-community-vs-enterprise)).

## The Defensible Statement

> For any given EE-only module/feature, there **may** be an OCA alternative. Coverage must be established **case-by-case** with evidence.

## How We Prove Coverage

### Source of Truth

The Odoo [Editions comparison page](https://www.odoo.com/page/editions) is the authoritative feature surface for EE-only capabilities.

### Classification System

For each EE-only feature, we classify the parity path using a 4-way system:

| Path | Meaning |
|------|---------|
| `oca_direct` | OCA module provides a direct replacement |
| `oca_partial` | OCA module covers the outcome but not full EE UX |
| `bridge` | External service + `ipai_*` connector fills the gap |
| `gap` | No known open replacement; gap accepted or to be built |

### Evidence Requirement

Every entry in the proof matrix must have at least one `evidence_link` (URL) supporting the classification. Claims without evidence are not accepted.

## Proof Matrix

**SSOT**: [`ssot/parity/ee_to_oca_proof_matrix.yaml`](../../ssot/parity/ee_to_oca_proof_matrix.yaml)

### Current Coverage (as of 2026-03-03)

| Category | EE Feature | Path | 19.0? |
|----------|-----------|------|-------|
| Productivity | Spreadsheet | `oca_direct` | needs_port |
| Productivity | Documents | `oca_direct` | needs_port |
| Productivity | Sign | `oca_partial` | unknown |
| Finance | Advanced Accounting | `oca_partial` | needs_port |
| Finance | Vendor Bill OCR | `bridge` | yes |
| Finance | Expense Advance | `oca_partial` | unknown |
| AI/Platform | AI Tools | `bridge` | yes |
| AI/Platform | Ask AI | `bridge` | yes |
| Services | Helpdesk | `oca_partial` | needs_port |
| Platform | Studio | `gap` | n/a |
| Platform | Odoo.sh | `gap` | n/a |
| Platform | IAP | `gap` | n/a |
| Services | Social Marketing | `gap` | n/a |
| Services | Loyalty | `gap` | n/a |

### Summary

- **14 EE features** tracked
- **2** have direct OCA replacements (`oca_direct`)
- **4** have partial OCA alternatives (`oca_partial`)
- **3** are covered by IPAI bridges (`bridge`)
- **5** are gaps (platform services or non-applicable features)
- **64%** of tracked features have an OCA or bridge alternative
- **0%** universal replacement claimed

## Proven Replacements (with citations)

### Spreadsheet (`spreadsheet_edition` → `spreadsheet_oca`)

The OCA module `spreadsheet_oca` **explicitly states** it is "an alternative to the proprietary module `spreadsheet_edition`" on the [Odoo Apps Store](https://apps.odoo.com/apps/modules/16.0/spreadsheet_oca). Available for 16.0; 19.0 port needed.

### Documents (`documents` → OCA/dms)

OCA maintains a dedicated [OCA/dms repository](https://github.com/OCA/dms) for document management. Odoo [forum answers](https://www.odoo.com/forum/help-1/cant-find-documents-modul-in-oddo-17-community-edition-270485) explicitly recommend OCA DMS as the Community alternative to Documents.

### Sign (`sign` → OCA/sign)

OCA maintains an [OCA/sign repository](https://github.com/OCA/sign) with signature-related addons. The [OCA shop](https://odoo-community.org/shop/purchase-sign-715953) offers Purchase Sign for sign flows on business documents. Classified as `oca_partial` because Odoo's EE [Sign app](https://www.odoo.com/app/sign) is a more polished standalone product.

## Why Some Gaps Are Acceptable

| Gap Feature | Why Acceptable |
|-------------|----------------|
| Studio | Custom `ipai_*` override modules cover specific needs; drag-drop builder waived |
| Odoo.sh | Self-hosted on DigitalOcean with CI/CD pipelines; managed hosting not needed |
| IAP | Self-hosted services (PaddleOCR, Gemini) replace IAP credit-based services |
| Social Marketing | Not in business scope |
| Loyalty | Not in business scope |

## Related SSOTs

| File | Purpose |
|------|---------|
| `ssot/parity/ee_to_oca_proof_matrix.yaml` | Evidence-based proof matrix (this doc's SSOT) |
| `ssot/parity/ee_to_oca_matrix.yaml` | Operational EE→OCA mapping (status tracking) |
| `ssot/parity/odoo_enterprise.yaml` | Feature-level parity status (go-live gates) |

## Maintenance

1. When evaluating a new EE feature for parity, **add an entry** to `ee_to_oca_proof_matrix.yaml`
2. Every entry **must** have at least one `evidence_link`
3. Do not claim `oca_direct` without a source explicitly stating the module is an alternative
4. Mark `odoo19_support: unknown` when not yet verified — do not assume
5. Update `summary` counts when adding/removing entries
