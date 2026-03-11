# Tasks — Odoo 19 EE Surface Parity (Goal-Based)

## Tier-0

- [ ] Define Tier-0 surfaces in `docs/parity/EE_SURFACE_CATALOG.yaml`
- [ ] Implement probes for:
  - [ ] Hosting lifecycle parity (Odoo.sh-like)
  - [ ] Upgrade safety parity
  - [ ] Support workflow parity

## Tier-1

- [ ] Add AI Agents surface checks (AI app enabled + key provisioning + guardrails)
- [ ] Add IAP operational checks (credits visibility + usage tracking + audit trail)

## Engine & CI

- [ ] Implement `scripts/parity/parity_check.py`
- [ ] Add JSON report output + Markdown summary output
- [ ] Add CI gate (Tier-0 hard fail; score threshold configurable)
