# Repo Layout Rationale

> **Why this repo doesn't look like upstream `odoo/odoo`.**

## Context

Upstream `odoo/odoo` is a **source distribution repository**. It places CE addons
directly under `/addons/` and runs from that tree. The upstream layout serves the
needs of the Odoo project itself: a single codebase shipping one product.

This repository (`Insightpulseai/odoo`) is a **production wrapper and governance
layer**. It manages three separate addon stacks with distinct ownership, update
cadences, and quality gates. We intentionally diverge from the upstream layout to
enforce structural boundaries.

## Three-Stack Addon Architecture

```
addons/
  odoo/    # Stack 1: CE core (upstream mirror, read-only)
  oca/     # Stack 2: OCA ecosystem (EE-parity modules)
  ipai/    # Stack 3: Integration bridge connectors only
```

### Stack 1 — `addons/odoo/` (CE Core)

- Mirrors the upstream Odoo CE addon tree
- Read-only in this repository; updated only via version bumps
- Provides the base ERP: accounting, sales, inventory, HR, etc.

### Stack 2 — `addons/oca/` (OCA EE-Parity)

- OCA modules vendored via `gitaggregate` (see `oca-aggregate.yml`)
- Implements Enterprise Edition feature parity using community modules
- OCA-first policy: prefer existing OCA modules over custom implementations

### Stack 3 — `addons/ipai/` (Integration Bridges)

- **Reserved for connectors to external services (bridges)**
- Allowed: OCR gateways, IoT daemons, email bridges, queue adapters, OIDC providers
- Forbidden: EE-parity business logic (must go in `addons/oca/`)
- Thin adapters only; no standalone business logic

## Canonical `addons_path` Order

All environments (dev, staging, prod) must configure `addons_path` to include
all three stacks in this priority order:

1. `addons/odoo` — CE core
2. `addons/oca` — OCA modules
3. `addons/ipai` — IPAI bridges

This ensures CE base classes load first, OCA extensions second, and IPAI
integration glue last.

## Policy Gates

| Rule | Enforcement |
|------|-------------|
| EE-only features must be satisfied via CE or OCA | CI keyword detection (`check_parity_boundaries.sh`) |
| `ipai_*` cannot replicate EE-only modules | Manifest parsing + baseline tracking |
| `ipai_*` allowed only for external-service connectors | Justification file required |
| No hybrid modules (EE parity + bridge in one) | Decision tree in `ADDONS_STRUCTURE_BOUNDARY.md` |

## Related Documents

- [`ADDONS_STRUCTURE_BOUNDARY.md`](ADDONS_STRUCTURE_BOUNDARY.md) — Full directory taxonomy, boundary rules, and decision trees
- [`ADDONS_PATH_INVARIANTS.md`](ADDONS_PATH_INVARIANTS.md) — CI-enforced addons_path invariants
- [`MONOREPO_CONTRACT.md`](MONOREPO_CONTRACT.md) — Full monorepo governance contract
- [`REPO_SSOT_MAP.md`](REPO_SSOT_MAP.md) — Canonical root locations
- [`../../oca-aggregate.yml`](../../oca-aggregate.yml) — OCA git-aggregator config
