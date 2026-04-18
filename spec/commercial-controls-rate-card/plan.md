# Plan — Commercial Controls / Rate Card Workflow

## Domain addition: Commercial Controls / Rate Card Workflow

### New bounded workflow
Introduce a governed workflow for:
- rate card management
- budget line requests
- portal opt-in / opt-out
- procurement approval

### Main entities
- RateCard
- RateCardLine
- VendorProfile
- BudgetRequest
- BudgetRequestLine
- ApprovalStep
- ApprovalDecision
- BillingMode
- VisibilityPolicy

### Main roles
- portal_user
- project_coordinator
- finance_reviewer
- finance_director
- admin

### Non-goals
- No automatic procurement commitment from Pulser suggestions
- No vendor identity exposure by default to portal users
- No approval bypass outside RBAC and workflow policy

## Placement

| Concern | Location |
|---|---|
| Canonical workflow SSOT | [platform/ssot/workflows/rate-card-approval.yaml](../../platform/ssot/workflows/rate-card-approval.yaml) |
| Architecture doc | [docs/architecture/RATE_CARD_APPROVAL_WORKFLOW.md](../../docs/architecture/RATE_CARD_APPROVAL_WORKFLOW.md) |
| Odoo implementation surface | `addons/ipai/ipai_commercial_controls/` (new module, deferred) |
| Portal UX (guests) | `web/apps/ipai-landing/` or ERP portal — TBD per deployment target |
| Pulser facilitation pack | Add to `agents/domain/finance/` + bind in [platform/ssot/agents/pulser-pack-matrix.yaml](../../platform/ssot/agents/pulser-pack-matrix.yaml) |

## Related doctrine

- Finance Director = Khalil (external guest per [ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml) — role: `client_finance_approver`)
- Pulser facilitative scope: `pulser_finance` pack (see [platform/ssot/agents/pulser-pack-matrix.yaml](../../platform/ssot/agents/pulser-pack-matrix.yaml))
- Audit retention per [platform/ssot/policy/azure-ai-governance-baseline.yaml](../../platform/ssot/policy/azure-ai-governance-baseline.yaml)
