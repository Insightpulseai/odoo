# EE Parity Policy (CE + OCA + Bridges)

> Quick-reference policy for addon placement.
> Full rules and decision trees: [`ADDONS_STRUCTURE_BOUNDARY.md`](ADDONS_STRUCTURE_BOUNDARY.md)

## Allowed

| What | Where | Example |
|------|-------|---------|
| CE modules | `addons/odoo/` | `account`, `sale`, `stock` |
| OCA modules (EE-parity) | `addons/oca/` | `subscription_oca`, `helpdesk_mgmt` |
| External-service connectors | `addons/ipai/` | `ipai_ocr_gateway`, `ipai_auth_oidc`, `ipai_sms_gateway` |
| Mail/queue/email bridges | `addons/ipai/` | `ipai_mail_bridge_zoho`, `ipai_slack_connector` |

## Not Allowed

| What | Why |
|------|-----|
| `ipai_*` modules that replicate EE-only features | EE parity belongs in `addons/oca/` |
| `ipai_*` modules with standalone business logic | Business logic is CE or OCA territory |
| Hybrid modules (EE parity + bridge in one) | Split into OCA module + IPAI bridge |

## PR Review Checklist

If a PR adds or modifies `addons/ipai/*`, verify:

- [ ] Module connects to an **external service** (API, daemon, hardware, cloud)
- [ ] Module does NOT replicate Enterprise-only Odoo functionality
- [ ] Module includes no business logic that belongs in CE/OCA
- [ ] `__manifest__.py` description states which external service it bridges
- [ ] If the module calls an external API, a minimal interface contract is documented
      (RPC endpoints, queue names, or payload schema)

## Bridge Taxonomy

A module is a **bridge** if it connects Odoo to something that runs outside the
Odoo process:

| Bridge Type | Examples |
|-------------|----------|
| Cloud API | OCR services, AI inference endpoints, Zoho Mail API |
| Queue/Bus | RabbitMQ, Redis pub/sub, n8n webhook receivers |
| Auth Provider | OIDC, WorkOS, Auth0 |
| Hardware/IoT | POS terminals, barcode scanners, printers |
| Data Sync | Plane API, Supabase Edge Functions, ETL connectors |

If it **only extends Odoo models/views** and talks to no external service,
it is NOT a bridge and belongs in `addons/oca/`.

## Allowed Exception: Temporary Compatibility Shims

An `ipai_*` module may exist in `addons/ipai/` as a **temporary compatibility
shim** if and only if ALL of the following constraints are met:

| # | Constraint |
|---|-----------|
| 1 | The module contains **only** JS and/or XML shims — no Python models, views, security rules, or data files |
| 2 | It fixes a **hard boot failure** caused by removed upstream APIs (not a nice-to-have) |
| 3 | The `__manifest__.py` description explicitly states **"TEMPORARY"** and lists concrete removal criteria |
| 4 | A `README.md` in the module directory documents purpose, constraints, and sunset plan |
| 5 | The module must **never** implement business logic, EE-parity features, or standalone functionality |
| 6 | Removal criteria are reviewed on the same monthly cadence as the EE Parity Policy |

**Current temporary shims**:

| Module | Shims | Removal trigger |
|--------|-------|-----------------|
| `ipai_mail_compat` | `mail.Discuss.mobileTopbar` stub, `Record.one/many/attr` aliases | OCA 19.0 branches drop Odoo 17 API references |

This exception exists because the alternative — forking OCA module source — would
violate the OCA module isolation rule (`.claude/rules/ssot-platform.md` Rule 10).
Temporary shims are the lesser policy violation.

## Enforcement

- **CI**: `check_parity_boundaries.sh` blocks new violations on every PR
- **Baseline**: Existing violations tracked in `scripts/ci/baselines/parity_boundaries_baseline.json`
- **Monthly review**: First Monday of each month
- **Goal**: Zero baseline violations by 2026-08-20

## References

- [`ADDONS_STRUCTURE_BOUNDARY.md`](ADDONS_STRUCTURE_BOUNDARY.md) — Full boundary rules and decision trees
- [`ADDONS_PATH_INVARIANTS.md`](ADDONS_PATH_INVARIANTS.md) — `ipai_*` namespace reservation policy
- [`REPO_LAYOUT.md`](REPO_LAYOUT.md) — Why this repo differs from upstream `odoo/odoo`
