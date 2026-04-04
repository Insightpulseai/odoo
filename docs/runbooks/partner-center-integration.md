# Partner Center Integration

## Doctrine

Partner Center and the commercial marketplace are **commercial control-plane surfaces only**.
They do not replace Odoo as execution authority or platform services as runtime authority.

```
Partner program / marketplace enrollment
  != marketplace runtime integration
  != CSP reseller automation
```

## Three lanes

### Lane A — Partner Program (enablement dependency)

| Item | Status | Notes |
|------|--------|-------|
| MAICPP enrollment (Launch tier) | Adopt now | Free. Entra tenant `402de71a` exists. |
| Solutions Partner for Data & AI | Target | Maps to Databricks + Azure AI + DocIntel workload |
| Solutions Partner for Digital & App Innovation | Target | Maps to ACA + Odoo SaaS workload |
| Partner Location Account (PLA) ID | Required | Needed for enrollment |

Lane A is a **business-enablement dependency**, not a runtime dependency.
No code artifacts. Tracked in Plane/Odoo project management.

### Lane B — Marketplace Listing (go-to-market)

| Item | Status | Notes |
|------|--------|-------|
| Publisher account | Evaluate | Required before any SaaS offer submission |
| SaaS offer packaging | Evaluate | Define plans, pricing, MACC eligibility |
| Offer metadata and assets | Evaluate | Screenshots, descriptions, support URLs |
| Co-sell readiness | Defer | Requires solution docs, reference arch, customer refs |

Lane B is **sequential**: publisher account → offer packaging → submission → review → listing → co-sell.

### Lane C — Fulfillment + Metering Runtime

| Item | Status | Notes |
|------|--------|-------|
| SaaS Fulfillment API v2 | Evaluate | Landing page, activation, webhook lifecycle |
| Metering Service API | Evaluate | Custom dimensions, hourly usage events |
| Referrals API | Defer | Not actionable until listing is live |

Lane C is where code lives. Everything below applies to Lane C only.

## Implementation doctrine

### REST-first

- Use `azure-identity` (`ConfidentialClientApplication` or `ManagedIdentityCredential`) for Entra token acquisition
- Use `httpx` for direct REST calls
- No SDK dependencies — .NET SDK is archived at v3.4.0, no official Python SDK exists
- SaaS Fulfillment and Metering APIs are <10 endpoints each

### Client structure (when implemented)

```
platform/services/partner-center-client/
  auth.py               # Entra token acquisition
  fulfillment.py        # SaaS Fulfillment API v2
  metering.py           # Marketplace Metering Service
  referrals.py          # Co-sell Referrals (later)
  errors.py             # Error normalization
  audit.py              # Evidence/audit hooks
```

Do not build one monolithic wrapper. Each module is independent and testable.

### Auth model

- SaaS Fulfillment uses a **fixed Entra app ID** (Microsoft-mandated for SaaS offers)
- Metering uses the same app registration
- Referrals API uses app+user tokens with MFA (enforced since April 2026)
- All credentials via Azure Key Vault (`kv-ipai-dev`), never hardcoded

## SaaS Fulfillment lifecycle

```
Azure Marketplace customer purchase
  │
  ▼
Landing Page (ACA: ipai-website-dev or dedicated)
  - Resolve marketplace purchase token
  - Call SaaS Fulfillment API: resolve subscription
  - Provision tenant in Odoo (create company + subscription record)
  │
  ▼
Activation Callback → SaaS Fulfillment API v2
  - POST: subscription activated
  │
  ▼
Webhook Handler (FastAPI endpoint on ipai-odoo-dev-web)
  - Receives: ChangePlan, ChangeQuantity, Suspend, Reinstate, Unsubscribe
  - Updates Odoo subscription records
  │
  ▼
Metering Emitter (ipai-odoo-dev-worker or cron)
  - Hourly: collect usage, emit to Metering Service API
```

### Authority boundaries

Marketplace **gates but does not own**:

- Subscription entitlement (active/suspended/cancelled)
- Plan/tier access (which features are available)
- Suspension/cancellation effects (restrict access)

Marketplace **does not become**:

- Finance transaction authority (Odoo owns accounting)
- Posting authority (Odoo owns journal entries)
- Document processing authority (platform services own runtime)

## Metering requirements

### Custom dimensions (candidates)

| Dimension | Event source | Immutable key |
|-----------|-------------|---------------|
| `per_document_ocr_processed` | Document Intelligence callback | `document_id + processing_timestamp` |
| `per_ai_inference` | Foundry agent run completion | `run_id + agent_id` |
| `per_bir_form_filed` | BIR filing confirmation | `filing_id + tax_period` |
| `per_user_seat` | Odoo `res.users` active count | `subscription_id + billing_period` |

### Idempotency

Each usage event **must** have a unique immutable key. The metering client must deduplicate before emission. Retries must not double-count.

### Event sourcing

Usage events originate from Odoo/platform runtime logs, not aggregate state. The metering emitter reads from the event source (e.g., `ir.logging`, platform telemetry) and transforms into metering API payloads.

### Retry safety

The Metering API accepts a 24-hour submission window with hourly aggregation. Failed submissions must be retried with the same event key. No silent drops. Failed events go to a dead-letter queue with alerting.

### Reconciliation

Usage events must be reconcilable back to runtime logs:

```
Odoo runtime log → usage event → metering API → Microsoft invoice
```

Each link in this chain must be auditable. Evidence path stored in `docs/evidence/`.

## Key dates

| Date | Event |
|------|-------|
| April 2026 | MFA enforced on all app+user Partner Center API calls |
| Current | .NET SDK archived — REST-only going forward |

## Registry of record

- Benchmarks: `agents/registry/template_benchmarks.yaml`
- Adaptation: `platform/templates/adaptation-map.yaml` (partner_center section)
- Runbook: this file
