# Partner Center — Platform Contracts

## Status
Scaffold (no clients implemented yet)

## Scope

This subtree owns the **API client contracts and SSOT models** for Microsoft Partner Center automation. It does **not** own:
- scheduled jobs or runners → `automations/partner-center/` (TBD)
- Azure app registrations / Key Vault wiring → `infra/azure/partner-center/` (TBD)
- operator/assistant UX → `agent-platform/partner-center/` (TBD, optional)
- runbooks / checklists / evidence → [`docs/marketplace/`](../../docs/marketplace/)
- CI workflows → [`.github/workflows/`](../../.github/workflows/)

## Auth model

- **IPAI is ISV** (not CSP / not CPV).
- **Auth:** App-only + certificate. **No PAT tokens.**
- **MFA enforcement** live since 2026-04-01 (Microsoft mandate).
- **Secrets:** Azure Key Vault `kv-ipai-dev` only — never in repo.
- Anchor: memory `reference_partner_center_auth.md`.

## Supported workflows (planned)

Per [`docs/marketplace/partner-center-automation-matrix.md`](../../docs/marketplace/partner-center-automation-matrix.md), the API-supported lanes targeted here are:

| Lane | Contract | Phase |
|---|---|---|
| Marketplace offers (Product Ingestion API) | `offers/` | Phase 1 (read), Phase 2 (write) |
| Marketplace offer assets/state sync | `offers/state/` | Phase 1 |
| Support requests (REST API) | `support/` | Phase 1 |
| Billing/report extraction | `billing/` | Phase 2 |
| CSP customer/account operations | `customers/` | Phase 3 (only if business motion shifts to CSP) |
| Orders/subscriptions | `orders/` | Phase 3 (CSP-conditional) |

## Repo boundaries — automation lane decision

| Lane | Mode | Owner |
|---|---|---|
| API-supported | Build thin wrapper here | `platform/partner-center/` |
| Portal-first | Document only — no client code | `docs/marketplace/` |
| Defer/manual | Track in checklists | `docs/marketplace/` |

See [`docs/marketplace/partner-center-automation-matrix.md`](../../docs/marketplace/partner-center-automation-matrix.md) §A/§B/§C for the full per-workspace decision matrix.

## Planned subtree (when implementation begins)

```text
platform/partner-center/
├── README.md            # this file
├── schemas/             # offer / submission / support / billing JSON schemas
├── offers/              # Product Ingestion API client + payload models
├── support/             # service request client (get/list/update)
├── billing/             # invoice/utilization extract client
├── clients/             # shared HTTP client + auth (cert-based, app-only)
└── tests/               # contract tests against Partner Center sandbox
```

## Doctrine alignment

- **CLAUDE.md § Engineering Execution Doctrine** — Partner Center SDK = clone-as-reference (not fork). IPAI builds only the thin Python/TypeScript wrapper delta.
- **Cross-Repo Invariant #23** — Reuse-first; the Microsoft .NET SDK is the contract reference, not the production runtime.
- **Adoption register §E.2** — `microsoft/partner-center-sdk-for-dotNET`, `Partner-Center-Labs`, `Partner-Center-PowerShell` are clone-reference; `Partner-Center-Storefront` is later/reference-only.

## Anchors

- **Decision matrix:** [`docs/marketplace/partner-center-automation-matrix.md`](../../docs/marketplace/partner-center-automation-matrix.md)
- **Companion runbook:** [`docs/runbooks/partner-center-integration.md`](../../docs/runbooks/partner-center-integration.md)
- **Auth memory:** `reference_partner_center_auth.md`
- **Marketplace gap matrix:** [`ssot/azure/marketplace_readiness_gap_matrix.csv`](../../ssot/azure/marketplace_readiness_gap_matrix.csv)
- **Adoption register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) §E.2 Partner Center references

## Status of implementation

**NONE.** This is doctrine + scaffold only. Implementation begins when:
1. PR #738 (doctrine) merges.
2. ADO Issue is created under epic `#7 [OBJ-007] Revenue-Ready Product Portfolio` for Phase 1 work.
3. Iteration assignment lands in R2-Core-Execution-60d (Phase 1 = read paths).
