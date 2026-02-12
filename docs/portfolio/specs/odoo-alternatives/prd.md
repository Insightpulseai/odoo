# PRD — Odoo Alternatives (EE → CE/OCA)

## 1) Product Summary

A public/internal catalog that maps **Odoo Enterprise features** to **Odoo CE + OCA** replacements, including install order, dependency notes, and CLI verification steps. Built as a searchable directory (OpenAlternative-style).

## 2) Goals

- Provide a **trustworthy, reproducible** migration reference from EE-only features to CE/OCA.
- Reduce "unknowns" by standardizing mapping structure and adding verification/rollback guidance.
- Enable fast discovery by category: Accounting, HR, Project, DMS, Helpdesk, Field Service, Sign/OCR, BI, etc.

## 3) Non-Goals

- Not a marketplace for paid proprietary plugins.
- Not a full ERP implementation guide; only mapping + operational guardrails.
- Not a replacement for official Odoo/OCA docs.

## 4) Personas

- **Solution Architect**: needs a migration plan from EE to CE/OCA.
- **Implementer/DevOps**: needs install order + scripts to verify.
- **Finance Ops**: needs clarity on accounting/tax coverage and risks.

## 5) Core User Flows

1. Search an EE feature → see recommended CE/OCA replacements.
2. Filter by category / maturity / risk level.
3. Copy install order + verification commands (one-click copy in UI; CLI-first in docs).
4. Contribute a mapping via PR with automated validation.

## 6) Data Model (Catalog)

Each mapping item:

```yaml
id: string (kebab-case)
ee_feature: string
category: enum
replacements:
  ce: [string]
  oca: [string] (repo/module identifiers)
  ipai: [string] (optional)
install_order: [string]
constraints: [string]
verification:
  commands: [string]
  expected_signals: [string]
rollback:
  commands: [string]
links:
  odoo: string?
  oca: [string]?
  notes: string?
maturity: enum (alpha/beta/stable)
risk: enum (low/med/high)
```

## 7) MVP Scope

- Seed catalog with ~30 high-impact EE features across Finance/HR/Docs/Helpdesk/Field Service/BI.
- Build pages:
  - Home (search + categories)
  - Feature detail
  - Category listing
  - Contribution guide
- Add CI gating:
  - Spec Kit presence
  - Catalog schema validation
  - Lint/typecheck/build

## 8) Success Metrics

- % of mappings with CLI verification
- PR acceptance time
- Reduction in "custom module" usage due to OCA-first guidance

## 9) Risks

- OCA module maintenance variance; mitigate with maturity/risk labels and last-verified metadata.
- Odoo version drift (18 → 19); mitigate with declared baseline and compatibility notes.
