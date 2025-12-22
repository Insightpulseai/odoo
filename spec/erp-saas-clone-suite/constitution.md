# ERP SaaS Clone Suite — Constitution

## 1. Project Identity

**Mission**: Build an **agent-first, spec-driven Odoo CE/OCA 18 "clone factory"** that delivers best-of-breed SaaS UX (Salesforce, ServiceNow, Notion, Cheqroom, Clarity PPM) on top of an enterprise-grade Odoo backbone.

**Core Thesis**: Mix "look" tokens (Fiori-like, modern SaaS feel) with "backend discipline" (SAP-grade workflows, OCA compliance) via thin `ipai_*` delta modules, enforced by catalog-driven parity gates.

## 2. Non-Negotiable Rules

### 2.1 Odoo License Compliance

* **CE + OCA only** — no Enterprise Edition modules or code.
* All custom code lives in `ipai_*` modules under `addons/`.
* Follow OCA contribution guidelines for any code intended for upstream.

### 2.2 Spec Kit Enforcement

Every significant feature or capability must have:

```
spec/<slug>/
├── constitution.md   # Non-negotiable rules and guardrails
├── prd.md            # Product requirements with acceptance criteria
├── plan.md           # Implementation phases and dependencies
└── tasks.md          # Actionable checklist with ownership
```

* CI blocks merge if any `spec/<slug>/` is missing required files.
* All tasks must reference a `capability_id` from `catalog/equivalence_matrix.csv`.

### 2.3 Catalog-Driven Development

* `catalog/best_of_breed.yaml` — targets to clone with hero flows.
* `catalog/equivalence_matrix.csv` — capability mapping with parity scores.
* `kb/parity/rubric.json` — scoring weights for parity assessment.
* `kb/parity/baseline.json` — locked P0 scores to prevent regression.

### 2.4 Parity Gates

* **P0 capabilities** (must-have for launch) cannot regress — CI fails if score drops.
* **P1/P2 capabilities** tracked but not blocking.
* Scores updated via manual assessment or automated checks.

### 2.5 Module Architecture

Follow the **Config → OCA → Delta** hierarchy:

1. **Config**: Use Odoo standard configuration first.
2. **OCA**: Prefer OCA modules over custom development.
3. **Delta**: Only add `ipai_*` modules for true gaps.

Module families:

* `ipai_platform_*` — cross-cutting primitives (workflow, approvals, audit, theme)
* `ipai_crm_*` — CRM vertical (Salesforce-like)
* `ipai_itsm_*` — ITSM vertical (ServiceNow-like)
* `ipai_workos_*` — Productivity vertical (Notion-like)
* `ipai_assets_*` — Asset management (Cheqroom-like)
* `ipai_ppm_*` — Portfolio management (Clarity-like)

## 3. Technology Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| ERP | Odoo 18 CE + OCA | Primary application |
| Database | PostgreSQL 15 | Per-tenant isolation |
| Workflow | n8n | Cross-system orchestration |
| Identity | Keycloak | SSO via SAML/OIDC |
| Chat | Mattermost | Notifications + AI assistants |
| BI | Superset | Dashboards on Supabase |
| CI/CD | GitHub Actions | Spec + parity gates |

## 4. Quality Gates

### 4.1 Merge Requirements

* [ ] Spec Kit validation passes
* [ ] Parity audit shows no P0 regressions
* [ ] OCA linting passes (pre-commit hooks)
* [ ] Unit tests pass for affected modules
* [ ] Documentation updated if API changes

### 4.2 Release Criteria

* All P0 capabilities at score ≥ 70/100
* No critical security findings
* Demo flow runs end-to-end
* Deployment runbook validated

## 5. Success Metrics

| Metric | Target |
|--------|--------|
| P0 capability coverage | 100% |
| Average P0 parity score | ≥ 70/100 |
| Time to scaffold new capability | < 30 min |
| CI gate pass rate | > 95% |

## 6. Constraints

* No SaaS billing system in v1 (manual tenant provisioning)
* No public marketplace (curated `ipai_*` + OCA catalog only)
* Agent automation runs outside Odoo runtime
* All secrets via `.env` files, never hardcoded
