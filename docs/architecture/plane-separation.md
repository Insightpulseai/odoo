# Plane Separation — Odoo / Boards / GitHub / MCP

> Canonical operating model for IPAI. Four distinct planes, explicit boundaries,
> AI assistants read across them but do not blur their truths.

---

## The four planes

```
┌────────────────────────────────────────────────────────────────────┐
│ Business Operations Plane  — Odoo CE + OCA 18                      │
│   invoices, 2307 packets, fit-out requests, DMS, approvals,        │
│   accounting records, payroll, procurement, expense claims         │
└────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────┐
│ Engineering / Delivery Plane — Azure Boards (ipai-platform)        │
│   epics, features, PBIs, tasks, bugs, impediments, sprints,        │
│   release tracking, infra work, eval work, spec-bundle execution   │
└────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────┐
│ Source Control Plane — GitHub (Insightpulseai org in ipai ent.)    │
│   code, PRs, branches, commits, releases, Actions (scoped),        │
│   GitHub Pages, Dependabot, GHAS, code scanning                    │
└────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────┐
│ AI Access Plane — MCP Servers                                      │
│   Azure DevOps MCP  → Boards + Repos + Pipelines + Tests read      │
│   Odoo MCP (planned) → ERP reads for Pulser copilots               │
│   Azure MCP         → Azure resource read/write for ops agents     │
│   Foundry MCP       → AI Projects clients                          │
│   Microsoft Learn MCP → docs retrieval                             │
└────────────────────────────────────────────────────────────────────┘
```

Each plane has one authoritative system. Planes never overlap. Cross-plane
traffic goes through typed contracts (AB# links, MCP calls, webhook events),
never direct data copying.

---

## Classification rules — where does this task/item belong?

### Rule 1 — Business/finance/admin task → Odoo CE + OCA 18

| Example | Lives in Odoo as |
|---|---|
| Prepare intercompany invoice | `account.move` |
| Review and approve 2307 packet | `account.move` + OCA approval layer |
| Collect fit-out corporate documents | OCA DMS |
| Route finance/admin approval chain | `ir.actions.server` + approval workflow |
| Process payroll cycle | `hr.payslip` |
| Year-end tax filing (BIR 2307/1601/1604) | `ipai_bir_compliance` module |

**Never** model these as Azure Boards items. They aren't engineering work; they're
operational records with legal/financial state.

### Rule 2 — Engineering/release/backlog task → Azure Boards

| Example | Lives in Boards as |
|---|---|
| Add 2307 release blocker when PDF missing | PBI / Issue |
| Upgrade OCA-dms to newer branch | Task |
| Write BIR eval judge | Task |
| Entra Agent ID registration for pulser-finance | Task |
| Publish Pulser SaaS marketplace offer | Epic |
| Fix 401 on pulser-api callback | Bug |

**Never** model these as Odoo records. They aren't business transactions; they're
delivery tracking.

### Rule 3 — Code change → GitHub

| Example | Lives in GitHub as |
|---|---|
| Implementation of a PBI | branch + PR on `Insightpulseai/odoo` |
| Infra change | branch + PR on `Insightpulseai/infra` |
| Agent prompt edit | branch + PR on `Insightpulseai/agents` |
| Spec bundle update | branch + PR on `Insightpulseai/platform` |

**Always** link back to a Boards item via `AB#<id>` (per
`docs/templates/repo-to-boards-contract.md`).

### Rule 4 — AI needs to read across planes → MCP servers

| Question | MCP answer path |
|---|---|
| "What's blocking our sprint?" | Azure DevOps MCP → Boards work items |
| "Which PRs need review?" | Azure DevOps MCP → Repos/PRs |
| "What's the customer's last invoice?" | Odoo MCP → `account.move` read |
| "What Azure resources run the demo env?" | Azure MCP → resource query |
| "How do I configure Azure AI Content Safety?" | Microsoft Learn MCP → docs |

**Never** try to have one MCP answer for another plane. Azure DevOps MCP does NOT
know Odoo invoices. Odoo MCP does NOT know sprint blockers.

### Rule 5 — AI needs to *execute* → Pulser supervisor-mediated agents (not MCP directly)

Writes to Odoo, writes to Boards (state transitions), writes to Azure (ops) all
go through Pulser's agent framework with maker-checker gates — never direct
MCP writes from an assistant. Reads through MCP are fine; writes require the
approval band flow.

---

## Decision tree — quick classification

```
Is it a business record? (invoice, approval, payslip, compliance document)
├── Yes → Odoo CE + OCA 18
└── No
    ├── Is it engineering delivery work? (implementation, infra, release)
    │   ├── Yes → Azure Boards
    │   └── No
    │       ├── Is it a code change?
    │       │   ├── Yes → GitHub (with AB# back-link)
    │       │   └── No
    │       │       ├── Does an AI need to read across planes? → MCP
    │       │       └── Does an AI need to execute an action? → Pulser
```

---

## What AI assistants (Pulser, Copilot, Claude) are allowed to do

| Action | Allowed | Mechanism |
|---|---|---|
| Read Boards items/PRs/builds | ✅ | Azure DevOps MCP |
| Read Odoo records | ✅ | Odoo MCP (scoped) |
| Read Azure resources | ✅ | Azure MCP |
| Read Microsoft docs | ✅ | Microsoft Learn MCP |
| Write to Boards (state transition, comments) | ⚠️ With maker-checker | Pulser supervisor flow |
| Write to Odoo (create invoice, approve document) | ⚠️ With maker-checker | Pulser supervisor + Odoo bridge |
| Write to Azure (deploy, restart, scale) | ⚠️ With maker-checker | Pulser + Azure DevOps Pipeline trigger |
| Push code directly | ❌ | Human authors PRs; Copilot drafts from work items |
| Bypass approval bands for high-risk actions | ❌ | Not allowed regardless of role |

---

## Cross-plane linking contract

```
Odoo record ←──────→ Boards work item ←──────→ GitHub PR ←──────→ Build/Deploy
(2307 packet)       (PBI #1234)              (PR #56)           (Pipeline run)

Link mechanism:
  Odoo →  Boards:  Odoo field `x_devops_item_id` (integer)
  Boards → GitHub: AB#1234 in branch/PR/commit
  GitHub → Pipeline: `trigger:` in azure-pipelines.yml
```

Each link is one-way readable from either end via MCP reads. Each link is
updated only via its owning plane's natural flow (Odoo record touch, Boards
state transition, PR merge, Pipeline build).

---

## Boundary violations — what NOT to do

| Anti-pattern | Why it breaks |
|---|---|
| Tracking 2307 certificate status in Azure Boards | Odoo is SoR for compliance; Boards ≠ ERP |
| Tracking sprint velocity in Odoo | Odoo isn't engineering PM |
| Syncing Boards items into Odoo `project.task` | Double-write; eventual drift; violates SoR rule |
| Putting engineering backlog into Pulser memory | Pulser is consumer, not owner |
| MCP writes bypassing Pulser approval bands | Violates 3-tier defense doctrine |
| Having AI assistant create Odoo invoices "directly via MCP" | High-risk mutation without governance |

---

## Rollout status (as of 2026-04-18)

| Plane | System | Status |
|---|---|---|
| Business Ops | Odoo CE 18 + OCA | ✅ Production on Azure Container Apps |
| Engineering Delivery | Azure Boards `ipai-platform` | ✅ Project exists, needs Epic seeding (9-Epic plan) |
| Source Control | GitHub `Insightpulseai` org in `ipai` Enterprise | ⚠️ Org move from Dataverse → ipai pending |
| AI Access — Azure DevOps MCP | Installed | ✅ Wired in this Claude Code session |
| AI Access — Odoo MCP | Planned | ❌ Not yet built (see `spec/odoo-mcp-server/`) |
| AI Access — Azure MCP | Installed | ✅ Used throughout session |
| AI Access — Foundry MCP | Installed | ✅ Queries `ipai-copilot-resource` |
| AI Access — Microsoft Learn MCP | Installed | ✅ Used for research |

---

## References

- `docs/templates/ado-copilot-work-item.md` — Copilot-launch-ready work items
- `docs/templates/repo-to-boards-contract.md` — AB# linking conventions
- `CLAUDE.md` Invariant #10, #10a, #11 — three-protocol model, MCP-first, SaaS authority
- `ssot/governance/platform-authority-split.yaml` — platform deploy authority matrix
- [Azure DevOps MCP Server overview](https://learn.microsoft.com/en-us/azure/devops/mcp)
- [Azure Boards ↔ GitHub integration](https://learn.microsoft.com/en-us/azure/devops/boards/github)
