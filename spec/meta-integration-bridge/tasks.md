# Tasks — Meta Integration Bridge

## A. Current-State / Blockers
- [x] Confirm `ssot/external/meta_ads_integration.yaml` is the canonical Meta Ads contract
- [x] Resolve ad-account assignment blocker for system user `claude-automation`
- [x] Generate access token (primary app 971674085514908) — vaulted 2026-03-31
- [ ] Enable App Secret Proof on primary app (971674085514908)
- [x] Store token in Key Vault as `meta-marketing-api-token` — done 2026-03-31
- [ ] Update site URL to `insightpulseai.com`
- [ ] Complete app business verification for primary app
- [ ] Switch primary app from development to live mode
- [ ] Consolidation decision: deprecate secondary app (951394464039117) or keep both

## B. Contract / SSOT
- [ ] Define canonical event schema for lead_created
- [ ] Define canonical event schema for lead_qualified
- [ ] Define canonical event schema for opportunity_won
- [ ] Define canonical event schema for invoice_paid / purchase_completed
- [ ] Extend `ssot/external/meta_ads_integration.yaml` with runtime/security/reliability fields
- [ ] Record OCA WhatsApp authority and deprecated IPAI connector status in SSOT/spec

## C. Platform / Bridge
- [ ] Create Azure Function adapter for outbound Meta requests
- [ ] Add Key Vault-backed secret resolution
- [ ] Add idempotency middleware
- [ ] Add retry / dead-letter / replay workflow
- [ ] Add webhook signature verification
- [ ] Add structured logging and correlation IDs

## D. Conversions API
- [ ] Map canonical events to CAPI payloads
- [ ] Add sandbox/test-event validation path
- [ ] Persist delivery status and diagnostics result
- [ ] Add contract tests and failure-path tests

## E. Marketing API
- [ ] Implement audience hashing and sync
- [ ] Implement scheduled ad-insight extraction
- [ ] Land raw data in Databricks bronze
- [ ] Add normalized silver/gold models
- [ ] Define reporting contract for BI surface

## F. Optional WhatsApp Cloud Overlay
- [ ] Produce documented gap analysis versus `addons/oca/social/mail_gateway_whatsapp/`
- [ ] Confirm whether template messaging or Cloud API-only workflows are actually needed
- [ ] Proceed only after approved non-overlap decision

## G. Evidence / Readiness
- [ ] Capture sandbox verification evidence for CAPI
- [ ] Capture security review for secrets, webhook verification, and PII handling
- [ ] Capture go-live checklist and rollback criteria
