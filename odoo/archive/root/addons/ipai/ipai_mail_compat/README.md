# ipai_mail_compat — Temporary Migration Shim

> **Status**: TEMPORARY — remove when upstream OCA modules ship native Odoo 19 code.

## Purpose

This module exists **solely** to prevent Odoo 19 webclient boot failures caused
by OCA modules ported from Odoo 17 that still reference APIs removed in Odoo 18+.

It is **not** a bridge, connector, or EE-parity module. It is a temporary
compatibility shim permitted under the policy exception documented in
[`docs/architecture/EE_PARITY_POLICY.md`](../../../docs/architecture/EE_PARITY_POLICY.md)
§ Temporary Compatibility Shims.

## What It Does

| Shim | Problem | Fix |
|------|---------|-----|
| `discuss_compat.xml` | `mail.Discuss.mobileTopbar` template removed in Odoo 18+; OCA modules that `t-inherit` it crash the webclient | Empty stub template so extensions load without error |
| `record_compat.js` | `Record.one()` / `.many()` / `.attr()` replaced by `fields.One()` / `.Many()` / `.Attr()` in Odoo 19; OCA JS patches throw `TypeError` | Re-attaches old aliases on the Record class |

## What It Must NEVER Do

- Implement business logic (EE parity or otherwise)
- Add Python models, views, security rules, or data files
- Grow beyond pure JS/XML shims for removed upstream APIs
- Become a catch-all compatibility layer
- Serve as precedent for placing parity logic in `addons/ipai/`

## Removal Criteria

Remove this module when **all** of the following are true:

1. OCA `mail_tracking` no longer inherits `mail.Discuss.mobileTopbar`
2. OCA `web_responsive` / any OCA JS no longer calls `Record.one()`
3. All OCA modules in `oca-aggregate.yml` target 19.0 natively
4. `addons/oca/` is fully checked out and integration-tested on Odoo 19

## Sunset Plan

| Phase | Trigger | Action |
|-------|---------|--------|
| **Active** | OCA modules still reference Odoo 17 APIs | Keep module installed |
| **Deprecate** | OCA 19.0 branches drop legacy API usage | Log deprecation warning, open removal issue |
| **Remove** | All removal criteria met | Delete `addons/ipai/ipai_mail_compat/` entirely |

**Review cadence**: Check removal criteria on the first Monday of each month
(same cadence as EE Parity Policy monthly review).

## Policy Reference

- [`docs/architecture/EE_PARITY_POLICY.md`](../../../docs/architecture/EE_PARITY_POLICY.md) — §Temporary Compatibility Shims
- [`docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md`](../../../docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md) — Full boundary rules
