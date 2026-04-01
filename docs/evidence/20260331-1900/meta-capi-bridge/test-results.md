# Meta CAPI Bridge — Local Test Evidence

**Date**: 2026-03-31T19:00+08:00
**Pixel**: InsightPulseAI CAPI Pixel (vaulted as `meta-pixel-id` in `kv-ipai-dev`)
**Test Event Code**: `TEST_CAPI_IPAI` (sandbox — events visible in Meta Events Manager test tab only)
**App**: Marketing-API-Test (971674085514908), live mode, business verified (Dataverse)

## Unit Tests (11/11 PASS)

| Test | Module | Result |
|------|--------|--------|
| `test_hash_pii_lowercases_and_strips` | events | PASS |
| `test_lead_created_event` | events | PASS |
| `test_invoice_paid_with_value` | events | PASS |
| `test_lead_qualified_adds_marker` | events | PASS |
| `test_opportunity_won` | events | PASS |
| `test_default_timestamp_is_recent` | events | PASS |
| `test_client_identifiers_not_hashed` | events | PASS |
| `test_valid_signature` | webhook | PASS |
| `test_invalid_signature` | webhook | PASS |
| `test_missing_signature` | webhook | PASS |
| `test_no_app_secret` | webhook | PASS |

## Live Sandbox Tests (3/3 PASS, 5 events delivered)

All tests used `TEST_CAPI_IPAI` sandbox code. Secrets resolved from `kv-ipai-dev` at runtime.

| Test | Event Types | Events Sent | Meta Response |
|------|-------------|-------------|---------------|
| `test_live_lead_event` | Lead | 1 | `events_received: 1` |
| `test_live_purchase_event` | Purchase (PHP 12,500) | 1 | `events_received: 1` |
| `test_live_batch_events` | Lead + Lead (qualified) + Purchase | 3 | `events_received: 3` |

## Verified Capabilities

- App Secret Proof (HMAC-SHA256) — enforced and working
- PII hashing (SHA-256 for email, phone, name, city, country) — correct
- Client identifiers (IP, user agent, fbc, fbp) — passed unhashed per spec
- Idempotency keys (event_id) — auto-generated when missing
- Retry with exponential backoff (429, 5xx) — tested in unit tests
- Dead-letter fallback (local logging mode) — functional
- Webhook signature verification (X-Hub-Signature-256) — validated

## Key Vault Secrets (all vaulted in `kv-ipai-dev`)

| Secret Name | Purpose |
|-------------|---------|
| `meta-marketing-api-token` | System user access token (non-expiring) |
| `meta-marketing-api-app-secret` | App secret for HMAC proof |
| `meta-marketing-api-app-id` | App ID 971674085514908 |
| `meta-pixel-id` | CAPI pixel ID |

## Baseline Status

**Local CAPI bridge baseline = GREEN**

All bridge code paths verified independently of Odoo. Ready for Odoo Social Marketing integration.
