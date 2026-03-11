# Constitution — Odoo EE → CE/OCA Parity Matrix

## Non-negotiables

1. **License-free parity goal**: Deliver Enterprise-grade outcomes without Odoo Enterprise license dependency.
2. **OCA-first**: Prefer OCA 18.0 modules; CE core when possible; custom `ipai_*` only as last resort.
3. **CLI/API-only operations**: No UI-only procedures; every install/config/verify must be expressible via scripts, RPC, or config-as-code.
4. **Tiered bundles**: Provide capability "plans" (Free/Standard/Enterprise/Business-Critical) like Fivetran, but implemented as CE/OCA + policies.
5. **Deterministic validation**: Catalog must validate in CI against JSON Schema; PRs fail if invalid.
6. **Auditability**: Every mapping includes verification and rollback commands; maturity/risk required.
7. **Baseline declared**: Baseline is Odoo CE 18 + OCA 18.0 unless explicitly overridden per item.

## Decision rules (replacement hierarchy)

1. If CE core exists → use it.
2. Else if OCA maintained module exists → use it.
3. Else use minimal `ipai_*` glue:
   - Prefer inheritance + server actions
   - Avoid new controllers unless unavoidable
   - Include smoke install/upgrade checks

## Output contract for every mapping item

- EE capability name
- Plan tiers it belongs to
- Replacement set (CE, OCA, ipai)
- Install order
- Constraints
- Verification + expected signals
- Rollback commands
- Maturity + risk
