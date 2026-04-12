---
name: pulser-odoo-architecture
description: Validate and enforce the Pulser for Odoo architecture lane — Odoo as system of record, Foundry as assistive AI plane, Azure as runtime
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [architecture, odoo, foundry, pulser, service-plane, boundary]
---

# pulser-odoo-architecture

**Impact tier**: P1 -- Operational Readiness

## Purpose

Define and validate the three-lane architecture for Pulser for Odoo: Odoo CE 18
is the sole operational system of record for all business truth; Azure AI Foundry
(`ipai-copilot` project) is the bounded, approval-gated AI plane; Azure Container
Apps is the runtime and hosting platform. This skill is the foundational boundary
reference that all other Pulser skills consult when making lane-crossing decisions.

## When to Use

- Before implementing any feature that touches more than one service plane.
- When an agent or tool proposes creating parallel workflows, ledgers, or approval
  engines outside Odoo.
- During architecture reviews, PR reviews, or spec sign-off for Pulser features.
- When a new Azure service is proposed for the Pulser stack.

## When Not to Use

- For Odoo module internals that are entirely within the Odoo lane.
- For pure Foundry SDK mechanics (use `pulser-odoo-foundry-runtime` instead).
- For deployment sequencing (use `pulser-odoo-deploy` instead).

## Inputs Expected

- Access to repo SSOT files and architecture docs (read-only).
- A proposed feature, PR, or design that crosses a service-plane boundary.

## Source Priority

1. Repo SSOT / `AGENTS.md` / `CLAUDE.md` / spec bundles
2. Existing architecture anchor docs in repo (`docs/architecture/`)
3. Microsoft Learn MCP official documentation
4. Official Microsoft GitHub samples only when needed
5. Anything else only if absolutely necessary, clearly marked secondary

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `AGENTS.md` | Agent team roles, Odoo vs Foundry boundary statements |
| `CLAUDE.md` | Non-negotiables, service-plane split rule, CE-only constraint |
| `ssot/agent-platform/foundry_tool_policy.yaml` | Tool preference order, approval gates, bounded tool use |
| `ssot/ai/agents.yaml` | Agent definitions — confirm no agent owns business truth |
| `docs/architecture/ACTIVE_PLATFORM_REFERENCE_MODEL.md` | Authoritative platform lanes |
| `docs/architecture/target-platform-architecture.md` | Target-state service topology |
| `docs/architecture/ai/CONSOLIDATION_FOUNDRY.md` | Foundry migration status, v1 vs v2 |
| `spec/copilot-target-state/` | Pulser target-state spec (if present) |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure AI Foundry overview agent service architecture")`
   -- retrieves Foundry project structure, agent service scope, control-plane vs data-plane.
2. `microsoft_docs_search("Azure Container Apps microservices architecture Odoo ERP")`
   -- retrieves ACA as ERP hosting platform, managed identity, networking patterns.
3. `microsoft_docs_search("Azure AI Foundry agent tool approval human-in-the-loop")`
   -- retrieves approval gate patterns, human-in-the-loop tool design for enterprise.
4. `microsoft_docs_search("Azure well-architected AI workload responsible AI boundary")`
   -- retrieves WAF AI workload guidance: autonomy limits, human oversight, audit.

## Microsoft Learn MCP Topic Keys

- foundry_overview
- foundry_agent_service
- azure_container_apps
- ai_well_architected_guidance

## Workflow

1. **Inspect repo** -- Read `CLAUDE.md` service-plane split rule and `AGENTS.md`.
   Record which business functions are declared Odoo-owned (workflow, approvals,
   accounting, tax, expense, liquidation). Read `ssot/agent-platform/foundry_tool_policy.yaml`
   to confirm tool preference order and which tool types require `approval: required`.
2. **Query MCP** -- Run queries 1-4. Capture Foundry's agent service scope
   (assistive, not authoritative), WAF AI guidance on human oversight, and
   ACA patterns for ERP hosting.
3. **Compare** -- Evaluate the proposed feature or PR against these boundary rules:
   (a) Does any Foundry agent write to Odoo without an approval gate?
   (b) Does the design introduce a parallel ledger, approval engine, or tax engine
   outside Odoo? (c) Does a new Azure service replace an Odoo primitive rather
   than extend it? (d) Is AI Search / Fabric / Cosmos added as a default
   requirement rather than an optional grounding component?
4. **Patch** -- If violations are found: reroute writes through Odoo ORM with
   approval gates, remove parallel engines, downgrade optional Azure services
   to "optional when SSOT requires", add `approval: required` to any tool that
   mutates Odoo state.
5. **Verify** -- No Foundry agent has write access to Odoo records without an
   explicit approval gate. No parallel accounting, approval, or tax engine
   exists outside Odoo. All new Azure services are classified in
   `ssot/azure/runtime_topology.yaml` as required, optional, or future.

## Output Contract

| Artifact | Location | Format |
|----------|----------|--------|
| Architecture boundary decision | `docs/architecture/ai/CONSOLIDATION_FOUNDRY.md` | Markdown update |
| Tool approval gate additions | `ssot/agent-platform/foundry_tool_policy.yaml` | YAML |
| SSOT service classification | `ssot/azure/runtime_topology.yaml` | YAML |
| Evidence pack | `docs/evidence/<stamp>/pulser-odoo-architecture/` | Markdown + diffs |

## Safety and Guardrails

- Odoo CE 18 only. No Enterprise modules, no odoo.com IAP dependencies.
- Foundry is assistive only. It never owns business truth or approval authority.
- No parallel engines. Foundry may surface, suggest, or draft — Odoo records and approves.
- Azure AI Search, Fabric, and Cosmos are optional grounding services, not default requirements.
- Anti-patterns that must be flagged: parallel ledger, parallel approval engine, parallel tax engine,
  Foundry agent with unconditional write access to Odoo, AI service replacing Odoo primitive.

## Verification

- [ ] Service-plane split confirmed: Odoo=operational SoR, Foundry=AI plane, Azure=runtime.
- [ ] No Foundry agent tool mutates Odoo records without `approval: required`.
- [ ] No parallel accounting, tax, or approval engine proposed outside Odoo.
- [ ] Optional Azure services are classified as optional in SSOT (not forced MVP requirements).
- [ ] `ssot/agent-platform/foundry_tool_policy.yaml` reflects current tool preference order.
- [ ] Evidence directory contains architecture boundary assessment and MCP excerpts.

## Related Skills

- `pulser-odoo-deploy` -- deployment doctrine for the Pulser for Odoo release
- `pulser-odoo-foundry-runtime` -- Foundry-side agent configuration and runtime governance
- `azure-foundry-architecture` -- Foundry SDK v2, agent registration, model deployments
- `azure-aca-runtime` -- ACA scaling, probes, managed identity, revision management
- `azure-ai-evals-governance` -- eval pipelines, content safety, governance gates

## Completion Criteria

- [ ] Architecture boundary document updated with current Odoo/Foundry/Azure lane assignments.
- [ ] Every cross-lane tool in `foundry_tool_policy.yaml` has an explicit approval gate classification.
- [ ] No anti-pattern (parallel engine, unconditional write) present in any Pulser module spec or SSOT.
- [ ] Optional vs required Azure services clearly classified for MVP scope in SSOT.
- [ ] Evidence directory contains boundary assessment, MCP excerpts, and any diff.
