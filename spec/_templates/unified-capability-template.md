# Unified Capability Template

> Copy this entire file to `spec/<capability-slug>/prd.md` (or split into
> `constitution.md` / `prd.md` / `plan.md` / `tasks.md` per the
> spec-kit pattern). Every capability must fill every section before
> the readiness review gate.

**Capability slug**: `<slug>`
**Owner (business)**: `<name_or_role>`
**Owner (technical)**: `<name_or_role>`
**Status**: `draft | in_design | in_implementation | in_uat | ready_for_release | released`
**Last updated**: `<YYYY-MM-DD>`

---

## 1. Vision

Long-term aspirational outcome. What does success look like 12–24 months from now?

- Initiative / capability name:
- Strategic theme:
- Problem statement:
- Target customer / business unit:
- Why now:

## 2. Mission / outcome

Fundamental purpose. Why does this capability exist?

- Intended business outcome:
- In-scope value streams:
- Out-of-scope areas:
- Success definition:

## 3. Objectives / KRs

Quantifiable goals. VMOKRAPI style.

| Objective | KR1 | KR2 | KR3 | Baseline | Target date |
|---|---|---|---|---|---|
|   |   |   |   |   |   |

## 4. Business case

- Expected value ($, strategic, operational):
- Cost / budget envelope:
- Risks:
- Assumptions:
- Dependencies:
- Go / no-go criteria:

## 5. Scope

**In scope**:
-

**Out of scope**:
-

## 6. Actors / roles / RBAC

| Actor | Role | Goals | Permissions | Visibility |
|---|---|---|---|---|
|   |   |   |   |   |

## 7. Workflow / approvals / states

- Trigger(s):
- State machine:
- Approval gates:
- Exceptions / failure modes:
- Audit events emitted:

## 8. Data model / visibility

| Entity | Fields | Sensitive fields | Visibility policy | Retention |
|---|---|---|---|---|
|   |   |   |   |   |

## 9. Integrations / architecture

| Target | Integration pattern | Authority SSOT |
|---|---|---|
| Odoo | (XML-RPC / REST / webhook / bus / mail_server / ir.attachment / queue_job) | [ssot/odoo/interoperability-template.yaml](../../ssot/odoo/interoperability-template.yaml) |
| Entra | (OAuth / MI / Agent ID / Guest) | [ssot/identity/entra-identity-matrix.yaml](../../ssot/identity/entra-identity-matrix.yaml) |
| Foundry | (AzureAIAgentClient / hosted agent / raw OpenAI) | [ssot/agent-platform/agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml) |
| Databricks | (Unity Catalog / Vector Search / SQL Warehouse / MLflow) | [ssot/data-intelligence/databricks-plane-charter.yaml](../../ssot/data-intelligence/databricks-plane-charter.yaml) |
| Document Intelligence | (OCR pipeline) | [ssot/agent-platform/foundry-chat-and-function-calling-reference.yaml](../../ssot/agent-platform/foundry-chat-and-function-calling-reference.yaml) |
| Notifications | (Zoho SMTP / Web Push) | [ssot/identity/mailbox-authority.yaml](../../ssot/identity/mailbox-authority.yaml) |
| External systems | (specify) | (link) |

## 10. AI / Pulser behavior

- Pulser pack binding: `<pack_id>` (from [platform/ssot/agents/pulser-pack-matrix.yaml](../../platform/ssot/agents/pulser-pack-matrix.yaml))
- Allowed actions:
- Forbidden actions:
- Required judges:
- Human-in-loop requirements:
- Mutation policy: `read_only | guarded_write | full_write`
- `pulser_can_commit_without_approval`: `false` (must be false for finance/ERP mutations)

## 11. Security / compliance

- Data classification: `public | internal | confidential | restricted | pii`
- RBAC (reference actors/roles table above):
- Approval rules:
- Audit / logging:
- Secrets / identity model:
  - Managed identity used: `<id-ipai-dev-*>`
  - Key Vault references:
  - Keyless auth compliant: `yes | no`
- PII handling:
- Retention:

## 12. Analytics / dashboards

- KPIs:
- Dashboards (Power BI / Databricks):
- Databricks outputs (UC path):
- Control-tower metrics:

## 13. Delivery plan (Epic / Features / Stories)

| Level | ID | Title | ADO Area Path | ADO Iteration |
|---|---|---|---|---|
| Epic | E-000 |   |   |   |
| Feature | F-000 |   |   |   |
| Story | S-000 |   |   |   |
| Story | S-000 |   |   |   |
| Task | T-000 |   |   |   |

See [templates/azure-boards-mapping.md](azure-boards-mapping.md) for the mapping rules.

## 14. Readiness gates

Mirror [ssot/release/go-live-readiness.yaml#core_readiness_checklist](../../ssot/release/go-live-readiness.yaml).

- [ ] SIT complete + signed off
- [ ] UAT complete + signed off
- [ ] Performance testing complete + signed off
- [ ] Security review complete
- [ ] RBAC verified per actors table
- [ ] Rollback plan documented + tested in preprod
- [ ] Support plan + on-call rota confirmed
- [ ] User training delivered
- [ ] License allocation sufficient
- [ ] Critical open issues mitigated

## 15. Go-live decision

- Go-live gate scope: `true | false | decide_now` (matches [ssot/release/go-live-scope-matrix.yaml](../../ssot/release/go-live-scope-matrix.yaml))
- Decision authority:
- Go / No-go recommendation:
- Evidence pack:

## 16. Support / hypercare

- Hypercare window length (48/72/96h):
- On-call primary:
- On-call secondary:
- Escalation chain:
- Paging mechanism:
- Incident severity matrix:

## 17. Risks / dependencies

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
|   |   |   |   |   |

## 18. Evidence links

- Spec bundle: [spec/\<slug\>/](.)
- Architecture doc: [docs/architecture/\<doc\>](../../docs/architecture/)
- SSOT: `ssot/**/*.yaml`
- Runbook: [docs/runbooks/\<runbook\>](../../docs/runbooks/)
- Evidence pack: `docs/evidence/<YYYYMMDD-HHMM>/<slug>/`
- ADO Epic: `<url_or_id>`
- Related commits: `<hashes>`

---

## Related SSOTs

- Unified template authority: [ssot/governance/unified-capability-template-authority.yaml](../../ssot/governance/unified-capability-template-authority.yaml)
- Odoo interoperability: [ssot/odoo/interoperability-template.yaml](../../ssot/odoo/interoperability-template.yaml)
- Boards taxonomy: [ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml)
- Planning authority: [ssot/governance/planning-surface-authority-map.yaml](../../ssot/governance/planning-surface-authority-map.yaml)
- VMOKRAPI mapping: [ssot/governance/vmokrapi-spatres-mapping.yaml](../../ssot/governance/vmokrapi-spatres-mapping.yaml)
- Go-live readiness: [ssot/release/go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml)
- Go-live scope: [ssot/release/go-live-scope-matrix.yaml](../../ssot/release/go-live-scope-matrix.yaml)
