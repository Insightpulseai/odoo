# OPRG Plane Mapping — Concrete scenario → system routing

> Scenario-by-scenario mapping showing exactly where each OPRG (Operational
> Pilot Readiness Gates / Pulser PH pilot) concern lives. Applies the
> plane-separation doctrine in `docs/architecture/plane-separation.md`
> to real work items.

---

## How to read this table

| Column | Meaning |
|---|---|
| **OPRG scenario** | Business-facing scenario as understood by founders / ops / finance |
| **Odoo model** (system of record) | Where the business record lives |
| **Azure Boards item** | Engineering/delivery tracking reference (where applicable) |
| **MCP query surface** | How an AI assistant reads this info cross-plane |
| **Write auth** | Who can mutate (human / Pulser with approval / CI) |

**One-line rule:** business record → Odoo · delivery work → Boards · AI reads → MCP · AI writes → Pulser with maker-checker.

---

## 1. Finance — Intercompany invoice readiness

| Element | Value |
|---|---|
| **OPRG scenario** | "Is this intercompany invoice ready to post?" |
| **Odoo model** | `account.move` (filtered: `move_type=out_invoice`, companies differ) |
| **Odoo fields** | `state`, `partner_id`, `line_ids`, `x_intercompany_readiness` (computed) |
| **Azure Boards** | ISSUE-PH-014 — *Implement AR invoice readiness and draft invoice creation* |
| **GitHub repo** | `Insightpulseai/odoo` → `addons/ipai/ipai_ph_eopt_invoice/` |
| **MCP query surface** | Odoo MCP: `env['account.move'].search_read([...], ['state', 'x_readiness'])` |
| **Write auth** | Finance user with approval band B (Pulser may propose, not auto-post) |
| **Reads across planes** | Assistant uses Odoo MCP for readiness; Azure DevOps MCP for "is the readiness-logic PR merged?" |

## 2. Finance — 2307 packet completeness & release

| Element | Value |
|---|---|
| **OPRG scenario** | "Is the 2307 packet complete and releasable?" |
| **Odoo model** | `account.move` + attachments (`ir.attachment`) + `ipai_ph_2307.packet` |
| **Odoo fields** | `has_2307_certificate`, `packet_state` (draft/ready/released), `attachment_ids` |
| **Azure Boards** | ISSUE-PH-026 — *Implement 2307 readiness and evidence pack* |
| **GitHub repo** | `Insightpulseai/odoo` → `addons/ipai/ipai_ph_2307/` |
| **MCP query surface** | Odoo MCP: read packet state + attachments |
| **Write auth** | Finance user with approval band C (release gate requires human maker + checker; no agent auto-release) |
| **Reads across planes** | Odoo MCP for packet state; Azure DevOps MCP for release-gate CI status |

## 3. Admin — Fit-out request & document checklist

| Element | Value |
|---|---|
| **OPRG scenario** | "What's missing in this fit-out request?" |
| **Odoo model** | `project.task` (project: Admin/Facilities/Fit-out) + OCA DMS folders |
| **Odoo fields** | `stage_id`, `x_checklist_state`, `documentation_folder_id`, `checklist_line_ids` |
| **Azure Boards** | (none — operational, not engineering) |
| **GitHub repo** | N/A |
| **MCP query surface** | Odoo MCP: task + checklist lines + linked DMS docs |
| **Write auth** | Admin operator (Pulser may suggest missing items, but checklist closure is human) |
| **Reads across planes** | Odoo MCP only — fit-out is pure business ops |

## 4. Platform — Release-gate eval enforcement

| Element | Value |
|---|---|
| **OPRG scenario** | "Are release-gate evals passing for the release?" |
| **Odoo model** | (none — engineering gate) |
| **Azure Boards** | ISSUE-PH-002 — *Turn release-gate eval definitions into enforced runs* |
| **GitHub repo** | `Insightpulseai/agents` → `agents/evals/` + `Insightpulseai/platform` → pipeline definitions |
| **Artifacts** | Azure Pipelines build logs, eval judge reports, `docs/evidence/<stamp>/evals/` |
| **MCP query surface** | Azure DevOps MCP: build status + test results + pipeline artifacts |
| **Write auth** | CI (pipeline runs eval); human approves release after eval pass |
| **Reads across planes** | Azure DevOps MCP for pipeline; GitHub for artifact source |

## 5. Integration — Documents taxonomy / metadata schema

| Element | Value |
|---|---|
| **OPRG scenario** | "How are fit-out docs classified for BIR and audit?" |
| **Odoo model** | OCA DMS: `dms.directory` + `dms.category` + custom `x_doc_taxonomy` |
| **Azure Boards** | ISSUE-PH-040 — *Implement Documents taxonomy and metadata schema* |
| **GitHub repo** | `Insightpulseai/odoo` → `addons/ipai/ipai_dms_taxonomy/` |
| **MCP query surface** | Odoo MCP: read categorized documents by taxonomy |
| **Write auth** | Admin operator (manual tagging) + Document Intelligence (agent proposes, human accepts) |
| **Reads across planes** | Odoo MCP |

## 6. Integration — Evidence retention policy

| Element | Value |
|---|---|
| **OPRG scenario** | "Are source attachments retained per BIR/legal policy?" |
| **Odoo model** | `ir.attachment` + retention lifecycle rules on DMS |
| **Azure Boards** | ISSUE-PH-041 — *Implement evidence retention and source-attachment policy* |
| **GitHub repo** | `Insightpulseai/odoo` → `addons/ipai/ipai_dms_retention/` |
| **MCP query surface** | Odoo MCP: attachment age + retention state |
| **Write auth** | Automated job (cron) with override by compliance officer |
| **Reads across planes** | Odoo MCP |

## 7. Platform — PG MCP server availability

| Element | Value |
|---|---|
| **OPRG scenario** | "Can Pulser read Odoo DB for grounding?" |
| **Odoo model** | (read-only PG connection target) |
| **Azure Boards** | ISSUE-PH-045 — *Deploy or verify PostgreSQL MCP server and read-only connection* |
| **GitHub repo** | `Insightpulseai/agent-platform` + deployment on ACA |
| **Artifact** | `IPAI PG MCP Server` Entra app (registered 4/12/2026) |
| **MCP query surface** | (The PG MCP IS the query surface for grounding) |
| **Write auth** | Read-only (by design) |
| **Reads across planes** | PG MCP reads Odoo DB; Pulser agents consume |

## 8. Platform — Schema query adapter for grounding

| Element | Value |
|---|---|
| **OPRG scenario** | "How do Pulser agents reason about Odoo schema?" |
| **Azure Boards** | ISSUE-PH-046 — *Implement read-only schema query and grounding adapter* |
| **GitHub repo** | `Insightpulseai/agents` → `agents/knowledge/odoo_schema/` |
| **MCP query surface** | PG MCP (reads schema); Foundry MCP (indexes for retrieval) |
| **Write auth** | None (read-only schema) |
| **Reads across planes** | PG MCP + Foundry MCP + Odoo MCP |

## 9. UAT — Pilot readiness scenarios

| Element | Value |
|---|---|
| **OPRG scenario** | "Run UAT scenarios mapped to SC-PH acceptance criteria" |
| **Odoo model** | (scenarios executed against real Odoo; records created during UAT) |
| **Azure Boards** | ISSUE-PH-054 — *Create UAT scenario pack mapped to SC-PH criteria* |
| **GitHub repo** | `Insightpulseai/platform` → `tests/uat/ph-pilot/` |
| **Artifacts** | Test results + evidence PDFs under `docs/evidence/<stamp>/uat/` |
| **MCP query surface** | Azure DevOps MCP: test plan + test results |
| **Write auth** | UAT tester (writes UAT record); Pulser reads during scenarios |
| **Reads across planes** | Odoo MCP (during scenarios) + Azure DevOps MCP (for test results) |

## 10. Cross-plane — "Are we pilot-ready?" summary

| Element | Value |
|---|---|
| **OPRG scenario** | "Can we proceed with OPRG pilot for customer X?" |
| **Inputs aggregated** | Odoo (finance readiness, 2307 state, fit-out checklists complete) + Boards (release gates passed, UAT complete) + GitHub (no blocking PRs) + CI (all pipelines green) |
| **Owning plane** | None single — this is a cross-plane rollup |
| **How Pulser answers** | Parallel MCP calls: Odoo MCP + Azure DevOps MCP + (optionally) Azure MCP for resource health |
| **Output** | Summary with per-plane facts + single go/no-go recommendation |
| **Write auth** | Human decision; Pulser only synthesizes |

---

## Classification check — for any new item, ask

```
1. Does this item record a business transaction / financial event?
   → Odoo. Stop.

2. Does this item describe code, tests, infra, or release work?
   → Azure Boards. Link repo + PR via AB#. Stop.

3. Does this item need AI to read context across planes (summarize, compare)?
   → MCP (Azure DevOps MCP or Odoo MCP per plane owner).

4. Does this item need AI to mutate state (create record, transition workflow)?
   → Pulser agent, supervisor-mediated, maker-checker approval band.
```

---

## What's explicitly NOT in this table (and why)

- **Pulser sprint items themselves** — these are Boards work items (already covered by the 9-Epic plan in `spec/microsoft-marketplace-gtm/tasks.md` reconciliation).
- **Marketplace GTM collateral** — not OPRG scope; lives in `spec/microsoft-marketplace-gtm/`.
- **Agent registrations (Entra Agent IDs)** — security plane, not OPRG scope; see `spec/pulser-agent-365-registration/`.
- **Finance copy of Boards items** (duplicating for visibility) — anti-pattern; do not create.

---

## Implementation checklist

- [ ] Verify each ISSUE-PH-* referenced above exists in `ipai-platform` project
- [ ] Add missing ones as PBIs with this mapping in their description
- [ ] For OPRG Odoo modules (`ipai_ph_2307`, `ipai_dms_taxonomy`, etc.), confirm presence in `addons/ipai/`
- [ ] Confirm Odoo MCP build per ISSUE-PH-045 target spec
- [ ] Confirm schema adapter per ISSUE-PH-046 covers all models referenced above
- [ ] Add this doc to `CLAUDE.md` "Cross-Repo Invariants" section as canonical mapping reference

---

## Related

- `docs/architecture/plane-separation.md` — the four planes + boundary rules
- `docs/templates/repo-to-boards-contract.md` — AB# linking conventions
- `docs/templates/ado-copilot-work-item.md` — Copilot-launchable work item template
- `docs/templates/basic-vs-scrum-decision.md` — ADO process decision
- `CLAUDE.md` Invariants #10, #10a, #11, #22, #23 — MCP-first, three-protocol, Odoo adoption, execution doctrine
