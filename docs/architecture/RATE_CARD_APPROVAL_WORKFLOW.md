# Rate Card Approval Workflow

## Purpose

Govern budget-line requests and procurement decisions while preserving controlled visibility over vendor identity and pricing authority.

## Key rules

- Vendor / consultant identity may be hidden from general client users.
- Specialization and commercial category may remain visible.
- Pulser may facilitate recommendations and draft composition only.
- Portal users may opt in or opt out of optional commercial lines.
- Final procurement decision authority remains with Khalil (Finance Director).
- All approval actions must pass through auditable workflow states.
- RBAC must prevent portal users or coordinators from performing final procurement approval.

## Canonical sources

- Workflow SSOT: [platform/ssot/workflows/rate-card-approval.yaml](../../platform/ssot/workflows/rate-card-approval.yaml)
- Spec bundle: [spec/commercial-controls-rate-card/](../../spec/commercial-controls-rate-card/)
- Finance director identity: [ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml) (Khalil Vera Cruz, `client_finance_approver`)

## State machine

```
draft ──▶ submitted ──▶ coordinator_validated ──▶ finance_review ──▶ approved
  │                                                      │
  │                                                      └──▶ rejected
  │
  └──▶ cancelled
```

## RBAC summary

| Role | Request | Validate | Review | Approve | Admin |
|---|---|---|---|---|---|
| portal_user | ✅ opt-in/out | — | — | — | — |
| project_coordinator | ✅ draft | ✅ | — | — | — |
| finance_reviewer | — | — | ✅ | recommend only | — |
| finance_director (Khalil) | — | — | ✅ | ✅ **final** | — |
| admin | — | — | — | ❌ (no bypass) | ✅ configure |

## Visibility policy

| Field | portal_user | coordinator | finance_reviewer | finance_director | admin |
|---|---|---|---|---|---|
| vendor_identity | hidden | conditional | visible | visible | visible |
| specialization_label | visible | visible | visible | visible | visible |

## Billing modes

`standard` · `hard_cost` · `paper_billing` · `offline_billing`

## Pulser boundaries

| Capability | Allowed |
|---|---|
| Recommend rate-card lines by specialization | ✅ |
| Assemble draft budget lines | ✅ |
| Commit procurement | ❌ |
| Override approval | ❌ |

## Audit events (all required)

`rate_card_line_created` · `budget_line_requested` · `budget_line_opted_in` · `budget_line_opted_out` · `request_submitted` · `request_validated` · `request_sent_to_finance` · `request_approved` · `request_rejected` · `billing_mode_changed` · `vendor_identity_viewed`

## Related

- [ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml) (11 TBWA\SMP guests including Khalil = Finance Director)
- [platform/ssot/agents/pulser-pack-matrix.yaml](../../platform/ssot/agents/pulser-pack-matrix.yaml) (`pulser_finance` pack governs Pulser facilitation)
- [platform/ssot/policy/azure-ai-governance-baseline.yaml](../../platform/ssot/policy/azure-ai-governance-baseline.yaml) (audit retention + risk assessment principles)
