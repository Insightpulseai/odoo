# Azure Boards Mapping (Basic process)

> Canonical hierarchy: **Epic → Issue → Task**. IPAI uses Basic process (not Scrum) per
> [ssot/governance/planning-surface-authority-map.yaml#methodology.agile_or_scrum](../../ssot/governance/planning-surface-authority-map.yaml).

## Hierarchy

| Level | ADO Basic work item | Maps to capability template | Example |
|---|---|---|---|
| Epic | Epic | Business capability / major release slice | "Expense & Commercial Controls" |
| Issue (= Feature) | Issue | Bounded workflow or product capability (deliverable slice) | "Rate Card Approval Workflow" |
| Story | Issue (with `story` tag) | User- or operator-visible behavior | "Portal user can opt in/out of optional budget lines" |
| Task | Task | Implementation unit | "Add visibility policy checks on rate card line API" |
| Bug | Task (type=Bug) | Defect against acceptance criteria | "Hidden vendor names exposed to portal users" |

## Scrum hierarchy note

If IPAI later migrates to Scrum process (revisit criteria in
[planning-surface-authority-map.yaml](../../ssot/governance/planning-surface-authority-map.yaml)), the
mapping becomes:

| IPAI today (Basic) | ADO Scrum equivalent |
|---|---|
| Epic | Epic |
| Issue (Feature-level) | Feature |
| Issue (Story-level) | Product Backlog Item |
| Task | Task |
| Bug | Bug |

Migration is additive — process inheritance preserves history.

## Naming conventions

| Level | Pattern | Example |
|---|---|---|
| Epic | `<Capability domain>` | `AI Runtime / Agent Platform` |
| Issue | `<Domain>: <Deliverable slice>` | `AI Runtime: Bind Foundry provider to ipai-copilot-resource` |
| Task | `<Verb> <concrete implementation step>` | `Add Foundry provider settings loader` |

## Area Paths (canonical 12)

From [azure-boards-taxonomy.yaml#area_paths](../../ssot/governance/azure-boards-taxonomy.yaml):

```
ipai-platform\odoo
ipai-platform\agent-platform
ipai-platform\agents
ipai-platform\web
ipai-platform\data-intelligence
ipai-platform\platform
ipai-platform\infra
ipai-platform\docs
ipai-platform\automations
ipai-platform\design
ipai-platform\templates
ipai-platform\identity-security
```

Rule: Area Paths reflect **repo boundaries**, NOT sprint cadence.

## Iteration Paths

```
FY26\Q2\Sprint 01
FY26\Q2\Sprint 02
FY26\Q2\Sprint 03
FY26\Q2\Sprint 04
```

Rule: Iterations reflect **time cadence**, NOT repo names.

## Tag taxonomy (18 canonical)

See [azure-boards-taxonomy.yaml#tags.canonical_set](../../ssot/governance/azure-boards-taxonomy.yaml):

`foundry` · `agent-framework` · `odoo` · `erp` · `prismalab` · `w9` · `identity` · `security` · `aca` · `entra` · `guest-access` · `retrieval` · `evals` · `observability` · `release` · `docs` · `breaking-change` · `production`

Rule: Tags are cross-cutting lenses. Do not invent new tags without adding to SSOT.

## Workflow states (Basic, lean)

```
New → Active → (Blocked) → Resolved → Closed
```

Optional if reporting needs emerge: `Ready for Validation`, `Ready for Release`.

## Complete worked example

```
Epic:     Expense & Commercial Controls  [ipai-platform\odoo]  [tag: erp, production]
│
├─ Issue:     Rate Card Approval Workflow  [tag: erp, finance]
│  │
│  ├─ Story:  Portal user can opt in/out of optional budget lines
│  │         [tag: guest-access]
│  │  │
│  │  ├─ Task:  Add visibility policy checks on rate card line API
│  │  ├─ Task:  Add approval state machine persistence
│  │  └─ Task:  Wire audit events (opt_in, opt_out, request_submitted)
│  │
│  └─ Bug:    Hidden vendor names exposed to portal users  [tag: security]
│
└─ Issue:     Expense Mobile Companion (PWA)  [tag: erp, production]
   │
   ├─ Story:  Submitter captures receipt via getUserMedia
   │         [tag: production]
   │  └─ Task:  Implement PWA camera capture component
   └─ Story:  Manager receives Web Push on approval request
              [tag: production, observability]
```

## Link from spec to ADO

In [unified-capability-template.md §13](unified-capability-template.md), populate:

| Level | ID | Title | Area Path | Iteration |
|---|---|---|---|---|
| Epic | E-001 | Expense & Commercial Controls | `ipai-platform\odoo` | `FY26\Q2\Sprint 01` |
| Feature | F-001 | Rate Card Approval Workflow | `ipai-platform\odoo` | `FY26\Q2\Sprint 02` |
| Story | S-001 | Portal opt in/out | `ipai-platform\odoo` | `FY26\Q2\Sprint 02` |
| Task | T-001 | Visibility policy checks | `ipai-platform\odoo` | `FY26\Q2\Sprint 02` |

Store ADO work item IDs alongside (e.g., `E-001 → ADO #123`) for traceability. When executing
via [docs/runbooks/azure-boards-setup.md](../../docs/runbooks/azure-boards-setup.md), capture returned IDs.

## Related

- Unified template: [unified-capability-template.md](unified-capability-template.md)
- Go-live readiness template: [go-live-readiness-template.md](go-live-readiness-template.md)
- Taxonomy SSOT: [ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml)
- Setup runbook: [docs/runbooks/azure-boards-setup.md](../../docs/runbooks/azure-boards-setup.md)
