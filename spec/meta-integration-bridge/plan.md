# Plan — Meta Integration Bridge

## Phase 0 — Unblock Existing Meta Ads Contract
- resolve the 6 SSOT blockers in `ssot/external/meta_ads_integration.yaml`
- verify ad-account assignment, token generation, and Key Vault storage
- normalize site/app metadata and business verification state
- capture evidence for each unblocker

## Phase 1 — Event Contract and Bridge Skeleton
- define canonical outbound business events
- finalize SSOT contract fields
- scaffold Azure Function bridge adapters
- add observability, retry, idempotency, and signature verification framework

## Phase 2 — Conversions API
- implement outbound CAPI mappings
- validate with sandbox/test-event diagnostics
- add dead-letter and replay handling
- capture evidence pack

## Phase 3 — Marketing API
- implement audience sync
- ingest ad insights to Databricks
- define reporting dataset / dashboard contract
- capture evidence pack

## Phase 4 — Optional WhatsApp Cloud Overlay
- only execute if a documented gap remains beyond OCA `mail_gateway_whatsapp`
- scope template messaging / Cloud API-only needs
- preserve non-overlap with OCA conversational authority

## Dependencies
- Azure Function runtime
- Azure Key Vault
- Odoo queue/webhook emitters
- Databricks ingestion/storage model
- Existing SSOT external integration contract file (`ssot/external/meta_ads_integration.yaml`)
