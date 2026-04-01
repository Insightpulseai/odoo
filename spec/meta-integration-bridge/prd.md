# PRD — Meta Integration Bridge

## Problem / Opportunity
Current Meta integration work is underspecified and mis-prioritized. Repo audit shows WhatsApp conversational messaging is already covered by the active OCA module, while the actual remaining gaps are:
1. server-side attribution via Conversions API,
2. Marketing API audience sync + ad insights,
3. the Azure-hosted bridge layer and related operational controls.

## Current State
- Meta Ads API: development only, contract exists at `ssot/external/meta_ads_integration.yaml`, not live.
- WhatsApp: active production via `addons/oca/social/mail_gateway_whatsapp/`.
- Facebook/Instagram embeds: active via upstream Odoo website features.
- Legacy IPAI WhatsApp connector: deprecated at `archive/root/addons/ipai/ipai_whatsapp_connector/`.

## Goals
- Deliver production-grade server-side attribution to Meta via Conversions API.
- Operationalize Marketing API for audience sync and ad-insight ingestion.
- Preserve Odoo/module boundaries by enforcing external bridge adapters.
- Avoid rebuilding WhatsApp capabilities already delivered by OCA unless a documented gap remains.

## Non-Goals
- No direct Odoo-to-Meta API calls.
- No duplicate WhatsApp conversational messaging implementation.
- No Threads, Instagram publishing, Messenger bot, or Commerce platform scope in v1.
- No resurrection of deprecated `ipai_whatsapp_connector`.

## Workstreams

### Workstream A — Conversions API
Primary use cases:
- lead_created
- lead_qualified
- opportunity_won
- invoice_paid / purchase_completed
- refund_issued

Success criteria:
- deterministic outbound contract
- idempotent delivery
- retry and dead-letter handling
- attribution validation against Meta event diagnostics

### Workstream B — Marketing API
Primary use cases:
- custom audience sync
- campaign/ad insight ingestion
- CRM-to-ads reporting in Databricks

Success criteria:
- hashed audience payloads
- scheduled sync jobs
- bronze/silver/gold insight pipeline
- campaign-to-revenue reporting model

### Workstream C — Optional WhatsApp Cloud Overlay
Gate condition:
Only activate if a documented gap remains beyond `mail_gateway_whatsapp`, such as approved template messaging, Cloud API-specific status hooks, or non-conversational outbound workflows not already handled by OCA.

Success criteria:
- no overlap with OCA conversational scope
- explicit gap analysis approved before implementation

## Blockers / Preconditions
The existing Meta Ads SSOT contract identifies these blockers that must be resolved before production activation:
1. assign ad account `1491166555865337` to system user `claude-automation`
2. generate system user token with `ads_management`
3. enable App Secret Proof in app settings
4. store token in Key Vault as `meta-ads-api-token`
5. update site URL from `prismalab.insightpulseai.com` to `insightpulseai.com`
6. complete business verification for the app

## Functional Requirements
- The system shall emit canonical business events from Odoo into a bridge queue or webhook layer.
- The bridge shall transform canonical events into Meta-specific payloads.
- The bridge shall support System User or equivalent server-to-server auth patterns.
- The bridge shall enforce idempotency keys on all outbound event deliveries.
- The bridge shall verify Meta webhook signatures before processing inbound callbacks.
- The bridge shall persist delivery status, retry state, and dead-letter outcomes.
- The system shall minimize PII and hash audience identifiers before Marketing API sync.
- The system shall land ad insights in Databricks and expose normalized reporting outputs.

## NFRs / Guardrails
- No plaintext secrets in repo.
- All secrets referenced via Key Vault.
- All bridges observable with request IDs, retry counts, and error classes.
- Rate limiting and exponential backoff required.
- Replay tooling required for failed deliveries.
- Contract tests required for each canonical event type.

## Open Questions
- Final canonical event taxonomy for purchase vs invoice-paid vs payment-posted.
- Whether Meta system-user token lifecycle is fully automatable in current tenant setup.
- Target BI surface for marketing performance consumption.
