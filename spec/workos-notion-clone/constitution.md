# Notion Clone Module Constitution (Odoo CE 18 + OCA 18)

## Purpose
Deliver a **Notion-equivalent Work OS** inside `jgtolentino/odoo-ce` using **Odoo CE 18 + OCA 18** as the execution/runtime engine. The module suite must provide a credible clone of Notion's core "felt experience":
- pages + nested pages
- blocks
- databases (typed properties)
- relations + rollups-lite
- views (table/kanban/calendar)
- templates
- permissions/sharing
- comments/mentions
- search

## Core Principles
1. **Clone-first**: match user journeys, defaults, and interaction patterns, not just data models.
2. **OCA-first, delta-only**: use Odoo core + OCA where it helps; custom `ipai_workos_*` modules only for gaps.
3. **Deterministic build**: artifacts (catalog, parity report, specs) must be regenerable from repo + commit.
4. **Evidence-based parity**: every "parity" claim needs tests or measurable checks.
5. **Upgradeable**: no core forks; extend via views, inheritance, assets, OWL components, bounded modules.
6. **White-label ready**: design tokens and theme overrides are first-class (per tenant).

## Non-negotiables
- No dependency on Notion at runtime (no integration required for parity).
- Every shipped capability has: workflow states (where applicable), permission rules, audit trail, and at least one automated test.
- CI blocks regressions for P0 capabilities.

## Pulser SDK Requirement
Repo must include Pulser SDK job wiring to run:
- `build_catalog`, `build_equivalence_matrix`, `generate_spec_kit`, `parity_audit`, `odoo_test`, `seed_demo_tenant`, `release_package`
