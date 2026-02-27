# Odoo Editions SSOT

## Canonical source

The authoritative Enterprise-vs-Community comparison for feature parity work is:

- **https://www.odoo.com/page/editions**

This repo treats that page as the **EE delta target list reference** for the
"CE + OCA + Bridges" parity strategy.

---

## Parity taxonomy

Every Enterprise feature target must be mapped to exactly one of:

| Code | Meaning |
|------|---------|
| `ce_core` | Covered by Odoo Community core (Odoo SA open-source modules) |
| `oca_module` | Covered by OCA 19.0 module(s) |
| `bridge_connector` | Covered by an external "Integration Bridge" service + thin connector if required |
| `defer` | Explicitly out-of-scope for now (document why + revisit trigger) |

---

## PPM scope clarification (Odoo 19 CE + OCA only)

For **PPM (Project / Portfolio / Program Management)** we use:

- **Odoo 19 Community Edition core** features, plus
- **OCA 19.0 modules** where applicable.

We will **not** pursue Enterprise-only PPM parity via custom ipai_\* parity modules.
Any remaining gaps are handled as **process + automation** (runbooks, approvals,
evidence workflows) rather than new parity add-ons.

**Hard rule**: PPM targets must use `ce_core` or `oca_module` only.
If a PPM feature can only be addressed via a bridge/external service, that is a
**process decision** (not a "PPM parity module") and must be documented as such.

---

## Audit workflow (evidence-first)

For each feature in `odoo_editions_targets.json`:

1. Confirm it exists on the Editions SSOT page (keep the `edition_ref` citation).
2. Decide parity taxonomy target (`ce_core` / `oca_module` / `bridge_connector` / `defer`).
3. If **`oca_module`**: record candidate OCA repo/module(s) (validate on 19.0 before finalising).
4. If **`bridge_connector`**: record:
   - Bridge service name
   - Connector addon (if any) and minimal surface area
   - Security model (server-only secrets, audit trail)
   - Observability requirements
5. Record risks: data migration impact, module upgrade risk, user workflow impact.
6. Store outputs as PRs and keep `odoo_editions_targets.json` up-to-date.

---

## Notes

- The Editions page is a product comparison; our mapping must remain conservative and
  evidence-backed. Do not guess module names — mark as `(to-fill)` until validated.
- `ce_core` must be confirmed in an actual Odoo 19 CE install before finalising.
- High-risk items (OCR, complex manufacturing, Studio) are explicitly routed to
  `bridge_connector` or `defer` unless a validated OCA alternative exists.
- This file is the SSOT; `odoo_editions_targets.json` is the machine-readable
  implementation of its taxonomy.
