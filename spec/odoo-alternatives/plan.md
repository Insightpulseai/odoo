# Plan — Odoo Alternatives (EE → CE/OCA)

## Phase 0 — Repo Baseline

- Confirm runtime: Bun/Node, Next.js App Router, Prisma, Postgres.
- Add `catalog/` + schema validation script.
- Add CI workflows enforcing Spec Kit and validations.

## Phase 1 — Catalog Schema + Seed Data

- Define `catalog/schema.json` (JSON Schema).
- Create `catalog/alternatives.yaml` with initial mappings.
- Add script `scripts/validate_catalog.mjs` to validate YAML against schema.

## Phase 2 — UI Integration

- Add category pages and detail pages sourced from catalog.
- Implement search indexing (local, build-time).
- Add "copy commands" blocks.

## Phase 3 — Contribution Workflow

- Add `CONTRIBUTING.md` guidelines for mapping format.
- Add PR template referencing validations.
- Add CI required checks for PR merges.

## Phase 4 — Verification Automation (Optional)

- Add dockerized Odoo CE + OCA test harness to run smoke installs (later milestone).
- Maintain "last verified" per mapping.

## Phase 5 — Release + Governance

- Tag releases by Odoo baseline version.
- Add deprecation policy for stale mappings.
