# Plan — Odoo EE → CE/OCA Parity Matrix

## Phase 0 — Spec kit + CI gates

- Add spec-kit validation
- Add catalog JSON schema validation
- Add lint/build gates (optional, repo-dependent)

## Phase 1 — Define plan taxonomy

- Define plan tiers and their required capability groups
- Define category taxonomy (Finance, HR, DMS, Support, Field Service, Governance, Security, BI)

## Phase 2 — Seed parity mappings

- Add initial 25–40 mappings for EE-only capabilities most relevant to operations
- Include install order + verification + rollback per item

## Phase 3 — Verification harness (optional milestone)

- Add dockerized Odoo CE + OCA smoke runner to validate installs
- Record "last_verified" timestamps per item
