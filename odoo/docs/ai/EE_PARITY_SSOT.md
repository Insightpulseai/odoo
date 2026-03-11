# Odoo Enterprise Parity SSOT

**SSOT file**: `ssot/parity/odoo_enterprise.yaml`
**CI gate**: `scripts/ci/check_odoo_enterprise_parity.py`
**CI workflow**: `.github/workflows/odoo-ee-parity-gate.yml`

## Parity definition

Outcome parity, not module parity. A feature is "met" when the business outcome is
achievable via CE + OCA + ipai_* connectors, not necessarily via the identical module.

## Status values

- `met`: fully implemented, evidence exists
- `partial`: implementation started, not complete
- `missing`: required but not implemented (CI fails if `required: true`)
- `waived`: explicitly out of scope (documented decision)

## Current snapshot (2026-03-02)

| Category | met | partial | missing | waived |
|----------|-----|---------|---------|--------|
| Finance | 3 | 2 | 0 | 1 |
| Productivity | 2 | 0 | 0 | 3 |
| Services | 1 | 0 | 1 | 1 |
| Customization | 1 | 1 | 0 | 0 |
| Platform | 1 | 2 | 0 | 2 |

All required features are met, partial, or waived. Gate passes on this commit.

## Update workflow

1. Edit `ssot/parity/odoo_enterprise.yaml`
2. Run `python scripts/ci/check_odoo_enterprise_parity.py` locally
3. Open PR — CI gate runs automatically on parity/addons path changes

## Related

- `ssot/parity/ee_to_oca_matrix.yaml` — module-level OCA equivalence mapping (complementary)
- `docs/ai/EE_PARITY.md` — strategic parity overview and feature mapping table
