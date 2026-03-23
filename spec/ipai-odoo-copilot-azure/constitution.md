# Constitution — IPAI Odoo Copilot Azure

## Purpose

Define the canonical contract for the Foundry-hosted Odoo Copilot agent, including its modes, tool boundaries, evaluation requirements, publication gates, and restrictions around ERP mutation.

This agent exists to provide:
- research and insight
- planning and validation
- monitored operational assistance
- bounded workflow invocation

It does not replace Odoo as the source of transactional authority.

## Authority Model

### Transactional authority
- Odoo is the sole transactional authority for ERP and finance-sensitive state.
- The agent may not directly become a second transactional writer.

### Agent authority
- Foundry is the agent plane for prompt orchestration, tool composition, evaluations, tracing, and publication.
- Foundry agent versions are not themselves ERP truth.

### Control-plane authority
- Supabase may hold control-plane state, evidence manifests, agent run state, and operational mirrors.
- Supabase is not the authoritative writer for Odoo finance entities.

### Analytics authority
- Fabric is analytical and read-only for Odoo-derived analytical projections.

## Operating Modes

The agent supports the following bounded modes:

### Research
- retrieves and synthesizes information
- may search knowledge and files
- may not mutate ERP state

### Insight
- explains findings, implications, comparisons, and recommendations
- may not mutate ERP state

### Plan
- produces proposed workflows, tasks, or implementation plans
- may not mutate ERP state

### Validate
- checks policy, evidence, completeness, and readiness conditions
- may call governed read-only or validation workflows
- may not post or mutate ERP truth directly

### Operate
- may invoke approved downstream workflows only
- any ERP mutation must happen through explicit governed Odoo-side APIs/workflows
- must fail closed on missing evidence, ambiguity, or policy mismatch

### Monitor
- observes health, traces, evaluations, and state transitions
- may surface alerts or required interventions
- may not mutate ERP state directly

## Invariants

- No direct ERP finance mutation from the Foundry chat surface.
- All sensitive actions require explicit downstream governed execution paths.
- Evidence is mandatory for finance-sensitive or compliance-sensitive recommendations and actions.
- Ambiguous or under-evidenced results must fail closed or escalate.
- Tool use must be explicit, bounded, and auditable.
- Publication may not exceed evaluation evidence.

## Tool Boundary Policy

### Allowed tool categories
- file search / knowledge retrieval
- code interpreter for bounded analysis
- evaluation and monitoring surfaces
- approved backend workflow invocations

### Restricted tool categories
- direct database writes to Odoo
- direct finance-object writes in Supabase mirrors
- any hidden mutation path not represented by an approved workflow contract

## Failure Contract

The agent must reject, quarantine, or escalate when:
- required evidence is missing
- output confidence is insufficient
- a requested action would exceed allowed mode/tool boundaries
- downstream workflow policy rejects execution
- ambiguous transactional classification is detected

## Publication Doctrine

An agent version may be published only when:
- instruction set is frozen and reviewed
- mode boundaries are documented
- evaluation pack passes
- prohibited tool/action paths are blocked
- evidence freshness is within policy
- release gates and governance policy allow publication

## Odoo Copilot Consolidation Doctrine

Odoo Copilot is the single product surface for Odoo-centered operational AI.

All previously discussed finance and ERP assistants are treated as internal Odoo Copilot skills/subagents, not standalone end-user products. This includes Finance Q&A, Expense Liquidation, Reconciliation, AP/AR document intake, Collections, Tax/Compliance, Close Orchestration, and Policy/Guidance capabilities.

### Authority model
- Odoo remains the transactional system of record and action authority.
- Microsoft Foundry is the shared multi-user runtime for production agent execution.
- Foundry Local is restricted to local prototyping, offline development, and workstation-sensitive testing only; it is not a shared production runtime.
- Azure Document Intelligence is the default document extraction substrate for invoice, receipt, bank statement, read/layout, and custom finance-document pipelines.
- Supabase remains the control-plane state, telemetry, feedback, artifact, and escalation store.
- Teams, Outlook, Excel, Telegram, email, and similar endpoints are channels into Odoo Copilot, not separate copilots/products.
- External vendor assistants (for example SAP Joule, Avalara/AvaTax, or similar tools) may be exposed only as optional adapters/tools behind Odoo Copilot, never as the primary product surface.

### Capability taxonomy
Odoo Copilot skills are organized into these domains:
1. Knowledge & Q&A
2. Document intake & OCR
3. Transactional action execution
4. Reconciliation & close
5. Collections & communications
6. Expense liquidation
7. Tax & compliance

Within these domains, the copilot relies on 8 core orchestration skills modeled after the continuous auditing pattern:
1. `policy_guard` (atomic checks)
2. `scenario_runner` (bundled scenario execution)
3. `exception_review` (findings/hits inbox)
4. `remediation_tasks` (templated resolution)
5. `auto_remediation` (automation of hits/tasks)
6. `risk_scoring` (confidence/classification)
7. `audit_export` (auditor-grade evidence packs)
8. `retention_guard` (archiving, stripping, retention controls)

## Compliance Operating Model Doctrine

Odoo Copilot adopts a compliance operating model based on six first-class concepts:

1. **Checks** — atomic detection rules that evaluate records, documents, deadlines, balances, or workflow states
2. **Scenarios** — governed bundles of checks executed together for a business purpose
3. **Runs** — immutable executions of a scenario over a defined scope and time window
4. **Findings** — exceptions/hits produced by checks during a run
5. **Remediation Tasks** — templated follow-up actions generated for findings
6. **Evidence & Audit** — attachments, notes, decisions, exports, and retention controls tied to runs and findings

### Governance rules
- Odoo Copilot must treat findings/exceptions as first-class operational objects, not transient chat outputs.
- Checks may be executed ad hoc, on schedule, or as part of a closing/filing playbook.
- Scenarios must support inactive/draft, active, and disabled/archived lifecycle states.
- Runs must preserve logs, scope, evidence, timestamps, and resulting findings.
- Findings must support assignment, comments, attachments, confidence/risk scoring, suppression/closure states, and linked remediation tasks.
- Remediation tasks should support templates, manual creation, and safe auto-routing.
- Auditor/export and retention controls are mandatory for regulated finance workflows.

## Close Control Plane Doctrine

Odoo Copilot includes a distinct close-control administrative plane that governs setup, access, connectivity, monitoring, and lifecycle management for regulated finance workflows.

### Administrative planes
1. **Bootstrap & Landscape**
   - define source systems, entities, calendars, jurisdictions, ledgers, and scenario enablement
   - validate prerequisites before scenarios/runs are allowed to execute

2. **Security & Access**
   - define role-bound access for design, operations, approval, audit, and admin functions
   - separate read/review permissions from state-changing remediation permissions

3. **Connectivity & Integration**
   - register and monitor connected systems, adapters, and sync health
   - define read/write scope, auth requirements, evidence returned, and failure semantics per adapter

4. **Monitoring & Reliability**
   - monitor runs, connector health, sync failures, degraded mode, and business logs
   - preserve operator visibility when dependencies fail

5. **Lifecycle & Retention**
   - govern archive, restore, retention, anonymization, export, purge, and offboarding
   - require explicit administrative workflow for destructive actions

### Governance rules
- Administrative-plane capabilities are part of Odoo Copilot, not separate products.
- All remediation outcomes must resolve back to Odoo records/workflows.
- Findings, runs, tasks, evidence packs, and exports must remain accessible to authorized admins/auditors across their lifecycle.
- Connector failure must degrade gracefully: findings stay visible, blocked actions are explicit, retries/escalations are logged.

## Data Connectivity and Analytics Doctrine

Odoo Copilot includes backend data-integration and analytics capabilities, but these are exposed as governed internal skills and adapters rather than separate user-facing products.

### Data preparation posture
- Power Query is the default Microsoft-aligned data shaping and connectivity substrate for analyst-friendly extraction, transformation, and repeatable refresh-oriented preparation flows.
- Power Query usage is adapter-scoped: Odoo Copilot may invoke or depend on Power Query/dataflow outputs, but end users should experience these as Odoo Copilot capabilities rather than separate tooling concepts.
- Power Query connections must be treated as governed assets with explicit connector settings, authentication, gateway selection, and privacy-level handling.

### Mirroring posture
- Fabric Mirroring is the preferred Microsoft-native near-real-time analytics replication path when operational data or external sources need to be replicated into an analytics plane.
- Database mirroring, metadata mirroring, and open mirroring are considered analytics/data-platform capabilities behind Odoo Copilot, not standalone copilot surfaces.
- Fabric Mirroring is appropriate for analytical replication into OneLake and cross-database analytics, but it does not replace Odoo as the transactional system of record.

### Capability placement
- Odoo remains the action authority.
- Odoo Copilot remains the single end-user product surface.
- Power Query and Fabric Mirroring are backend adapters/substrates used by Odoo Copilot skills for ingestion, shaping, replication, and analytics-ready access.

## Drift Policy

The following are prohibited:
- implying the copilot itself is the ERP source of truth
- allowing Operate mode to bypass Odoo-side gates
- broadening tools without policy and eval updates
- publishing new capabilities without updated evaluation evidence
- framing individual skills as standalone end-user products or separate copilots
- using Foundry Local as a shared production runtime
- making vendor copilots the primary UX surface for core Odoo workflows
- exposing Power Query or Fabric Mirroring as separate user-facing copilots
- treating the analytics mirror plane as the transactional authority

## Service-Plane Split Reference

The Odoo Copilot architecture operates across five distinct service planes. Each plane has a single authority and a defined boundary:

| Plane | Authority | Role |
|-------|-----------|------|
| Odoo | Transactional SoR | ERP state, finance entities, workflow lifecycle, operational mutations |
| Microsoft Foundry | AI/agent runtime | Prompt orchestration, tool composition, evaluations, tracing, publication (`microsoft-foundry/foundry-agent-webapp` for Entra+Agent pattern, `microsoft-foundry/mcp-foundry` for MCP Server integration) |
| Databricks | Governed analytics | Unity Catalog, DLT pipelines, lakehouse, governed transformations |
| Azure Document Intelligence | OCR/extraction bridge | Invoice, receipt, bank statement, BIR document extraction (resource: `data-intel-ph` in `rg-data-intel-ph`) |
| Azure DevOps | Promotion spine | CI/CD, release gates, environment promotion |

Odoo.sh is benchmark-only — it is not a runtime target for this platform.

## Odoo 19 AI Agent Alignment

Odoo 19 introduces a native AI agent abstraction with four configuration surfaces: **purpose**, **prompt**, **topics**, and **tools**. These are the in-app agent model for registration and selection.

`ipai_odoo_copilot` aligns to this vocabulary:
- Agent registration uses Odoo 19 native agent records
- Agent selection/routing uses Odoo 19 topic and tool bindings
- Foundry remains the external runtime for orchestration, evaluation, and publication
- Odoo AI agents are the UX/config surface; Foundry is the execution plane

The copilot does not replace or bypass the native Odoo 19 agent model — it extends it with Foundry-backed orchestration.

## External Benchmark Sources

The following external sources are benchmarks or optional complements, not runtime authority:

| Source | Classification | Notes |
|--------|---------------|-------|
| OpenAI Academy product pack | Eval/prompt benchmark | Scaffolds for `project_copilot` evaluations |
| OpenAI Academy finserv pack | Eval/prompt benchmark | Scaffolds for `taxpulse_ph` and `finance_reconciliation` evaluations |
| AvaTax (Avalara) | Future bridge target | Not available in PH market; benchmark-only until global tax engine is justified |
| Sovos | E-invoicing watch item | Not currently PH-active; adapter target if BIR mandates e-invoicing (see competitor analysis) |
| Notion 3.0 | Optional bounded knowledge surface | Not a core platform plane; read-only knowledge complement |
| SAP Joule | Benchmark-only | Per existing doctrine — adapter behind Odoo Copilot, never primary surface |

These sources may inform evaluation packs and prompt design but do not establish runtime authority or replace the service-plane split defined above.

## Competitor Awareness Doctrine

Odoo Copilot maintains awareness of the competitive landscape to inform capability design without adopting external dependencies prematurely. Full analysis: `docs/architecture/AGENT_FACTORY_VS_AVALARA_AVATAX.md`.

### Competitive positioning

| Competitor Category | Examples | Odoo Copilot Posture |
|---|---|---|
| Global tax engines | AvaTax, Vertex, ONESOURCE | Future bridge adapters via `ipai_tax_compliance_bridge` when multi-country expansion is justified |
| PH-native tax SaaS | Taxumo, JuanTax | Tax Pulse supersedes for Odoo-integrated use; no integration planned |
| Enterprise copilots | SAP Joule, Microsoft Copilot for Finance | Benchmark-only; ecosystem-locked to SAP/D365 respectively |
| Global e-invoicing | Sovos | Watch item; adapter if BIR mandates electronic invoicing |
| Compliance platforms | Sovos, Wolters Kluwer CCH Tagetik | No current overlap; monitor for PH e-invoicing mandates |

### Defensive moat (4 layers)

1. **PH-native regulatory depth** — BIR forms, TRAIN brackets, ATC codes, alphalist, eFPS XML. No global player covers this.
2. **Odoo-native integration** — Direct module access, Odoo state machine for filing lifecycle, no API connector overhead.
3. **White-box auditability** — JSONLogic rules, versioned rates JSON, compliance check catalog. Every computation traceable to a repo commit.
4. **Agentic governance** — Advisory/Ops/Actions topology, approval gates, human-expert-gated filing, exactly-once supervisor.

### Rules for competitive response

- Never preemptively integrate a competitor product without a published mandate or confirmed business requirement
- Competitors are adapters behind Odoo Copilot, never primary surfaces
- Benchmark competitor capabilities for eval design, not for runtime dependency
- If a competitor enters PH market (e.g., Sovos e-invoicing), the response is an adapter module, not an architecture change
