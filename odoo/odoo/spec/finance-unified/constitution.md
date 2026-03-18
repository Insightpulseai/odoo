# Constitution — Unified Finance System

> Immutable rules governing the BIR tax compliance, month-end close,
> and finance PPM/Clarity parity modules as one coordinated system.

---

## Rule 1: One System, Not Five Modules

BIR tax compliance, BIR notifications, BIR-Plane sync, finance PPM,
and month-end close seed are **one business system** with a shared
process model, shared team, and shared calendar. They must be treated
as a coordinated unit for planning, testing, deployment, and documentation.

## Rule 2: One Canonical Seed Authority

Odoo XML/CSV data files inside `ipai_finance_close_seed/data/` are the
**single source of truth** for operational seed data (stages, tags, team,
projects, milestones, tasks).

- `ipai_finance_closing_seed.json` (repo root) is a **derived export** for
  reference and external tooling. It is not authoritative.
- `supabase/seeds/002_finance_seed.sql` is a **deprecated downstream
  projection**. It must not be used for new Odoo deployments.

Any change to seed data starts in the XML/CSV files. Derived formats
are regenerated from those files, never hand-edited independently.

## Rule 3: Deprecated Modules Stay Dead

| Module | Status | Disposition |
|--------|--------|-------------|
| `ipai_finance_workflow` | `installable: False` | Superseded by `ipai_finance_close_seed`. Do not reactivate. |
| `ipai_finance_tax_return` | `installable: False` | Migrated to `ipai_enterprise_bridge`. Do not reactivate. |

No agent or developer may set `installable: True` on a deprecated finance
module. If functionality is needed, it must be added to an active module.

## Rule 4: No Duplicate SSOT Surfaces

There must be exactly **one** canonical document describing the unified
finance system: `docs/modules/FINANCE_UNIFIED_SYSTEM.md`.

The 24+ existing module doc stubs (`ipai_finance_ppm.md`,
`ipai_finance_close_seed.md`, `ipai_bir_tax_compliance.md`, etc.) may
continue to exist as per-module status reports, but they are **not**
authoritative for system-level architecture, process model, or seed
ownership. They must not contradict the unified doc.

## Rule 5: BIR and Close Calendars Must Be Testable

The seed data encodes real Philippine regulatory deadlines (BIR filing
dates) and real month-end close schedules. These are not optional
decoration — they are compliance-critical.

Tests must validate:

- All 12 monthly BIR filing cycles are present
- All quarterly and annual BIR forms are scheduled
- All 5 month-end close phases have tasks
- Stage and milestone references resolve to existing records
- Team member references resolve to existing partner/employee records

## Rule 6: Version Alignment

All active finance modules must target the same Odoo major version.
Currently: **19.0**. Any module still on `18.0.x.x.x` must be migrated
before the next release cut.

## Rule 7: No Module Sprawl

New finance functionality must be added to an existing active module
unless it introduces a genuinely new domain boundary. The bar for a
new `ipai_finance_*` or `ipai_bir_*` module is:

- It has its own Odoo models (not just data/views on existing models)
- It has no existing active module that owns the same domain
- It ships with at least one test file

## Rule 8: Dependency Direction

```
ipai_finance_ppm          (standalone — project, account, analytic)
ipai_bir_tax_compliance   (standalone — base, mail, account, project)
ipai_bir_notifications    (depends on → ipai_bir_tax_compliance)
ipai_bir_plane_sync       (depends on → ipai_bir_tax_compliance)
ipai_finance_close_seed   (data-only — project, hr)
```

Dependencies flow **toward** the two foundation modules (`ipai_finance_ppm`
and `ipai_bir_tax_compliance`). No foundation module may depend on a
satellite module. Circular dependencies are forbidden.
