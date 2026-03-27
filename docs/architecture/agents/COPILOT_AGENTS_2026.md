# Copilot / Agents Target State (2026)

> Durable architecture note for the InsightPulse AI copilot and agent plane.
> Machine-readable SSOT: `ssot/agents/copilot_agents_target_state.yaml`
> Build plan: `ssot/agents/copilot_agents_build_plan.yaml`

---

## Product Split

### Diva Goals (App)

Diva Goals is the **strategy and execution control plane**. It provides:

- Strategy / goal review
- Evidence-backed status
- Approvals
- Readiness / capability surfaces
- Governance views

Diva Goals is a product family of 6 modules: Goals, Execution Graph, People Capability, Agent Capability, Reviews, and Governance. All modules require Goals as a prerequisite.

### Diva Copilot (Copilot Family)

Diva Copilot is the **umbrella copilot family** — a thin shell architecture, not a monolithic agent. The shell provides conversation management, mode switching, context assembly, and skill/KB routing. Domain logic lives in skills and backend agents, never in the shell.

---

## Visible Copilots (5)

These are the user-facing copilot brands:

| Copilot | Audience | Key Skills |
|---------|----------|------------|
| **Diva Strategy Copilot** | Portfolio and strategy owners | Strategy review, portfolio alignment, evidence traceability |
| **Diva Odoo Copilot** | ERP operators, finance, back-office | Inherited from Odoo Copilot core |
| **Diva Tax Guru** | Finance and tax compliance | Tax advisory, BIR workflow, tax evidence collection |
| **Diva Capability Copilot** | HR, L&D, team leads | Capability gap analysis, learning path design, agent readiness |
| **Diva Governance Copilot** | Approvers, compliance officers | Drift/orphan detection, policy sufficiency judgment |

Each visible copilot activates a subset of skills and KB segments. No copilot operates outside its declared skill and KB scope.

---

## Backend Agents (10 + 1 optional)

These are **not** end-user brands. They are the worker, judge, and orchestration agents behind the copilot family.

| Agent | Type | Role | Boundary |
|-------|------|------|----------|
| `diva_orchestrator` | core | Workflow coordination, step sequencing | Never generates content directly |
| `evidence_harvester` | worker | Evidence collection from Odoo, Databricks, external | Read-only; never synthesizes |
| `status_synthesizer` | maker | Goal status narrative from evidence | Citation required; never invents data |
| `review_pack_writer` | maker | Review document assembly | Cannot approve its own output |
| `capability_mapper` | analyst | Skills-to-roles mapping, gap ID | Does not assign learning plans |
| `drift_detector` | analyst | Goal drift, orphan task detection | Detection only; no remediation |
| `policy_judge` | judge | Proposal evaluation against policy | Binary pass/fail; no remediation |
| `readiness_judge` | judge | Readiness assessment for promotion | Fail-closed on missing evidence |
| `approval_coordinator` | control | Approval routing, sign-off tracking | No authority to auto-approve |
| `taxpulse` | specialist | Tax computation, BIR filing prep | Never files or posts without approval |

### Optional (recommended)

| Agent | Type | Role | Boundary |
|-------|------|------|----------|
| `tax_policy_judge` | judge | Tax policy compliance evaluation | Binary pass/fail; no remediation |

The optional `tax_policy_judge` provides a proper maker/judge split in the tax domain, preventing `taxpulse` from both computing and validating tax outputs.

---

## Workflow Topology (5 workflows)

All workflows use **sequential orchestration** by default with **maker-checker** at gate transitions.

| Workflow | Domain | Trigger | Key Agents |
|----------|--------|---------|------------|
| `goal_status_synthesis` | Goals | Scheduled / on-demand | orchestrator → harvester → synthesizer → judge |
| `review_pack_generation` | Reviews | Stage transition | orchestrator → harvester → synthesizer → writer → judge → coordinator |
| `capability_readiness_review` | Capability | Scheduled / promotion request | orchestrator → mapper → readiness_judge |
| `learning_plan_recommendation` | Capability | Gap detected | orchestrator → mapper |
| `odoo_tax_assist` | Tax | Copilot invocation | orchestrator → taxpulse → policy_judge |

Fan-out is permitted only for evidence collection (parallel harvest, sequential synthesis). No autonomous loops.

---

## KB Segmentation (8 segments)

All copilot responses must be grounded in one or more KB segments. Free-form advice without a grounding citation is blocked.

| KB Segment | Domain | Consumers |
|------------|--------|-----------|
| `kb_strategy` | Strategic planning, OKR methodology | Strategy, Governance |
| `kb_execution` | Execution tracking, progress aggregation | Strategy |
| `kb_people_capability` | Skills taxonomies, competency frameworks | Capability |
| `kb_agent_capability` | Agent skills, readiness criteria, promotion gates | Capability |
| `kb_governance` | Policy templates, compliance rules, drift thresholds | Strategy, Governance |
| `kb_tax_policy_ph` | BIR regulations, TRAIN law, PH tax policy | Tax Guru |
| `kb_odoo_tax_runtime` | Odoo tax module config, filing workflows | Tax Guru, Odoo |
| `kb_tax_evidence` | Tax computation evidence, filing artifacts, audit trails | Tax Guru |

Retrieval protocol: **MCP** via `knowledge_base_retrieve` tool. This is the only supported retrieval interface for Foundry Agent Service.

---

## Microsoft Runtime Boundary

### Provision

| Component | Count | Purpose |
|-----------|-------|---------|
| Foundry resource | 1 | Central agent runtime/governance hub |
| Foundry project | 1 | Single project for all Diva assets |
| Foundry Agent Service | 1 | Managed agent execution boundary |
| Azure AI Search service | 1 | KB-backed retrieval for grounded agents |
| Agent Framework workflow set | 5 | Explicit, testable workflow definitions |
| Knowledge bases | 8 | Segmented by authority and domain |
| Managed identities | 3 min | Web runtime, jobs/automation, agent/data |

### Not Provisioned (explicit exclusions)

| Component | Count | Reason |
|-----------|-------|--------|
| Entra Domain Services | 0 | For legacy LDAP/Kerberos, not Foundry/Agent Framework |
| Extra Entra subdomains | 0 | Agents/copilots do not need identity subdomains |

### Near-Term Caveat

Hosted agents in Foundry Agent Service are **in preview**. Private networking for network-isolated Foundry resources is not supported during preview. Target architecture uses hosted agents as the long-term runtime, but the near-term execution posture keeps custom app/API glue in the controlled runtime plane until GA.

---

## Repo Ownership

| Repo Concern | Owns |
|--------------|------|
| `agents` | Visible copilots, backend agents, skills, judges, workflows, KB registry |
| `platform` | Control-plane state, approvals, runtime contracts, agent session metadata |
| `web` | Diva Goals app shell, copilot panels, approval drawers, review surfaces |
| `odoo` | Thin copilot adapter, record context builder, approved action queue |
| `data-intelligence` | Evidence normalization, review marts, readiness metrics, drift metrics |
| `docs` | Architecture authority, runbooks, governance docs |
| `infra` | Azure runtime substrate, Foundry wiring, Search wiring, MI provisioning |

Ownership is non-overlapping. Cross-boundary changes require a contract doc.

---

## Explicit Exclusions

1. **No Entra Domain Services** — agents use managed identities, not LDAP/Kerberos
2. **No extra Entra subdomains** — copilots and agents do not require identity subdomains
3. **No monolithic "Diva assistant"** — every copilot has a bounded skill and KB scope
4. **No direct Odoo posting from agents** — all mutations go through the approved action queue
5. **No free-form advice** — all responses grounded in KB segments with citations
6. **No autonomous loops** — every cycle has a bounded iteration limit
7. **No self-approving agents** — maker and judge roles are always separate

---

## Governance References

| Constitution | Rules | Scope |
|-------------|-------|-------|
| `spec/ipai-odoo-copilot-azure/constitution.md` | C1-C9 | Odoo Copilot core |
| `spec/diva-goals/constitution.md` | D1-D10 | Diva Goals product family |
| `spec/tax-pulse-sub-agent/constitution.md` | C1-C8 | TaxPulse sub-agent |

### Proposal State Machine

```
draft → evidence_collected → synthesized → judged → approved → published
                                              ↓
                                    needs_human_review (confidence < 0.85)

Blocked states: blocked_insufficient_evidence, blocked_policy_violation, blocked_confidence_low
```

`approved → published` requires human confirmation. No exceptions.

---

## Counts Summary

| Category | Count |
|----------|-------|
| App products | 1 (Diva Goals) |
| Copilot families | 1 (Diva Copilot) |
| Visible copilots | 5 |
| Backend agents | 10 (+1 optional) |
| Workflows | 5 |
| KB segments | 8 |
| Foundry resources | 1 |
| Foundry projects | 1 |
| Agent Services | 1 |
| AI Search services | 1 |
| Managed identities | 3 min |
| Entra Domain Services | 0 |
| Extra Entra subdomains | 0 |

---

*Created: 2026-03-23*
*SSOT: `ssot/agents/copilot_agents_target_state.yaml`*
