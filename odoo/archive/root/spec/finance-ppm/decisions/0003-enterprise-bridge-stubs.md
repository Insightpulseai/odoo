# ADR-0003: Enterprise Bridge Stubs (Delta)

| Field | Value |
|-------|-------|
| **Capability** | Minimal model/field compatibility stubs for EE model references |
| **Parity target** | Delta (`ipai_enterprise_bridge`) |
| **Date** | 2026-02-16 |
| **Status** | Accepted |

## Context

Several custom modules and third-party integrations reference Odoo Enterprise
model names or fields (e.g., `planning.slot`, `helpdesk.ticket`). On CE,
these imports would fail with `ImportError` or `KeyError`.

## CE Attempt

CE cannot provide models that only exist in EE. No configuration or
server action can create stub models for missing EE dependencies.

## OCA Search

OCA modules solve individual feature gaps (e.g., `helpdesk_mgmt` for helpdesk)
but do not provide a unified compatibility layer for all EE model references.

## Decision

Created `ipai_enterprise_bridge` as a thin glue layer that:
- Provides **safe stubs** and redirections for EE model references
- Routes to CE/OCA equivalents where they exist
- Logs warnings (not errors) for genuinely missing EE features
- **Does NOT reimplement** any EE product — only prevents import failures

This is a delta module, not a bridge, because it is an installable Odoo
module (`ir.module.module`) that runs inside the Odoo process.

## Consequences

- Must be updated when new EE model references are encountered
- Scope is deliberately minimal — stubs only, no feature reimplementation
- Not a substitute for actual OCA modules that provide real functionality
