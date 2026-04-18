# Tasks — Commercial Controls / Rate Card Workflow

## Commercial Controls / Rate Card Workflow

- [ ] Define rate card entity model and visibility policy
- [ ] Define hidden vendor identity behavior and reveal permissions
- [ ] Define specialization labels and Pulser recommendation inputs
- [ ] Define budget request lifecycle and state machine
- [ ] Define client portal opt-in / opt-out interactions
- [ ] Define billing mode flags including hard-cost / paper-billing handling
- [ ] Define approval routing with final FD approval
- [ ] Define Khalil final procurement authority rule
- [ ] Define RBAC matrix for portal, coordinator, finance, FD, admin
- [ ] Define audit log requirements for every budget/approval event
- [ ] Define notification triggers for request, review, approval, rejection
- [ ] Define reporting views for approved vs pending commercial items

## Implementation follow-ups (out of scope for this spec)

- [ ] Scaffold `addons/ipai/ipai_commercial_controls/` Odoo module
- [ ] Wire Pulser recommendation task into `agents/domain/finance/pack.manifest.yaml`
- [ ] Bind workflow events into `agent-platform/src/agent_platform/policy/approval_bands.py`
- [ ] Create portal opt-in UI surface (ERP portal vs external portal app — TBD)
- [ ] Integrate notification triggers with Zoho SMTP outbound mail
- [ ] Add reporting views to Power BI semantic model

## Related

- [prd.md](prd.md)
- [plan.md](plan.md)
