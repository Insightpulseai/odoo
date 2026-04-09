# Constitution — Meta Integration Bridge

## Purpose
Govern Meta platform integrations (Conversions API, Marketing API) as external system bridges for InsightPulseAI. WhatsApp conversational messaging is already covered by OCA and is not in scope unless a documented gap remains.

## Scope Boundary
This spec governs Meta platform gaps that are not already covered by active upstream/OCA capabilities.

## Existing Coverage Rule
- Do not duplicate WhatsApp conversational messaging already covered by OCA.
- Treat `addons/oca/social/mail_gateway_whatsapp/` as the current production authority for two-way WhatsApp messaging.
- Treat `archive/root/addons/ipai/ipai_whatsapp_connector/` as deprecated and non-authoritative.

## Architecture Doctrine
- Odoo must not call Meta APIs directly from business logic.
- All new Meta traffic must traverse a bridge adapter layer.
- Canonical runtime path:
  - Odoo -> queue_job/webhook -> Azure Function -> Meta APIs
  - Meta Webhooks -> Azure Function -> Odoo/FastAPI ingress
  - Meta Ad Insights -> Databricks Bronze -> Silver/Gold -> BI consumption
- Secrets must be stored in Azure Key Vault.
- Retry, idempotency, signature verification, and rate limiting are mandatory.

## Delivery Order
1. Conversions API bridge
2. Marketing API bridge
3. Optional WhatsApp Cloud overlay only if a gap remains beyond the active OCA WhatsApp module

## Governance
- Changes to event contracts require spec update before implementation.
- No direct Odoo-to-Meta calls in any workstream.
- All bridge adapters must be observable with request IDs, retry counts, and error classes.
- PII must be hashed before any audience sync operations.
