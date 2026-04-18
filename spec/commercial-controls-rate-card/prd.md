# PRD — Commercial Controls / Rate Card + Budget Approval Workflow

## Rate Card and Budget Approval Workflow

### Goal
Support client-visible budget line requests while keeping vendor pricing controls, procurement authority, and approval routing governed.

### Core requirements

1. **Rate card visibility controls**
   - Vendor / consultant legal name can be hidden from most users.
   - Specialization / capability label remains visible.
   - Internal coordinator can view source vendor identity when permitted.
   - Client portal users never see hidden vendor identity unless explicitly allowed.

2. **Pulser-facilitated budget composition**
   - Pulser can recommend rate-card lines based on specialization, task type, or requested service.
   - Pulser can assemble draft budget lines, but cannot approve procurement.

3. **Client budget line requests**
   - Client portal users can request additional budget lines.
   - Client portal users can opt in or opt out of optional budget items.
   - Requested changes create workflow events and approval tasks.

4. **Billing mode controls**
   - Budget lines support billing mode flags, including hard-cost / paper-billing / offline-billing handling if required by client process.
   - Billing mode changes are controlled and auditable.

5. **Procurement authority**
   - Final procurement decision authority remains with Khalil (Finance Director).
   - No request becomes committed procurement without the required approval state.

6. **Approval workflow**
   - Multi-step approval workflow required.
   - Workflow must support: `submitted`, `under_review`, `coordinator_validated`, `finance_review`, `approved`, `rejected`, `cancelled`.
   - Approval comments and decision timestamps must be stored.

7. **RBAC**
   - Portal user: request / opt in / opt out / view approved-visible lines only
   - Project coordinator: create/edit draft lines, reveal hidden vendor identity if permitted, route for approval
   - Finance approver: review commercial validity, recommend approval or rejection
   - Khalil / FD: final approval authority
   - Admin: configure workflow and policy, but not bypass audit trail

## Related

- [plan.md](plan.md)
- [tasks.md](tasks.md)
- [../../platform/ssot/workflows/rate-card-approval.yaml](../../platform/ssot/workflows/rate-card-approval.yaml)
- [../../docs/architecture/RATE_CARD_APPROVAL_WORKFLOW.md](../../docs/architecture/RATE_CARD_APPROVAL_WORKFLOW.md)
- [../../ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml) (Khalil Vera Cruz as finance director/approver)
