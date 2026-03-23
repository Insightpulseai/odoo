# Product Requirements Document: Odoo Copilot

## Product Definition

Odoo Copilot is the unified operational copilot for Odoo-centered finance and ERP workflows.

It consolidates the following previously separated capability areas into one governed product surface:

- Finance Q&A
- Expense Liquidation
- AP/AR document intake and OCR
- Balance sheet reconciliation
- Collections coordination
- Tax and compliance assistance
- Close orchestration
- Policy and approval guidance

The product pattern follows the finance scenario model: agents connect to ERP data, knowledge/policy documents, workflow/logging systems, and collaboration channels rather than acting as systems of record themselves.

## Goal

Create a Foundry-hosted Odoo Copilot that:

- supports bounded multi-mode assistance via internal skills
- uses approved tools and knowledge sources
- delegates ERP mutations only to governed downstream workflows
- is evaluated, monitored, and published under machine-readable policy
- preserves Odoo as the transactional authority

## Surface Classification

Odoo Copilot is one of five canonical assistant surfaces. See `docs/architecture/ASSISTANT_SURFACES.md`.

- **Role:** ERP / transactional assistant
- **Scope:** Authenticated, record-aware
- **Grounding:** Odoo runtime context → curated docs → bounded web
- **Action mode:** Read-only first, actions later by policy
- **Not:** The public landing assistant (that is the Marketing Assistant), not the orchestration shell (that is Diva), not the creative assistant (that is Studio)

## Non-Goals

- Shipping separate end-user products for each finance agent capability
- Using Foundry Local as the shared production runtime
- Making vendor copilots the primary end-user surface for core Odoo workflows
- Duplicating commodity productivity copilots when channel integration is sufficient
- Replacing Odoo as SoR
- Direct chat-driven posting of finance transactions
- Unrestricted tool invocation
- Autonomous mutation of ERP state without downstream controls

## Personas

### Operator

Needs fast answers, status, next steps, and safe action guidance.

### Finance / compliance owner

Needs evidence-backed, fail-closed assistance and no hidden posting paths.

### Architect / administrator

Needs clear tool boundaries, governance, versioning, and publish controls.

### Maker / agent maintainer

Needs a durable contract for expanding capabilities without breaking governance.

## Capability Matrix

The Odoo Copilot normalizes all finance and compliance domains (Tax, Month-End Close, AP Invoice Review, Expense Liquidation) into a unified **Detection → Investigation → Execution → Analytics** operating model.

### Core Orchestration Skills

| Skill | Role in Operating Model |
|---|---|
| `policy_guard` | Defines atomic compliance checks, selection conditions, and detection logic. |
| `scenario_runner` | Bundles checks into runnable scenarios, schedules executions, and logs runs. |
| `exception_review` | Unified workspace for findings/hits, displaying evidence, exceptions, and rationale. |
| `remediation_tasks` | Templates and tracks resolution steps for identified exceptions. |
| `auto_remediation` | Deterministic automation (auto-close safe cases, auto-route tasks, auto-generate follow-ups). |
| `risk_scoring` | Predictive triage, hit probability, and confidence scoring to prioritize human review. |
| `audit_export` | Bundles machine-readable evidence, runs, hits, tasks, and notes for external auditors. |
| `retention_guard` | Enforces data protection, anonymization, and archiving lifecycle policies on compliance data. |

### Best-fit Workflow Domains

| Domain | Application of Control Pattern |
|---|---|
| Tax Compliance | BIR VAT checks, withholding tests, filing prep validation, deadline-driven tasks. |
| Month-End Close | Accrual completeness, intercompany mismatches, close blockers, exception routing. |
| Expense Liquidation | Missing receipts, stale submissions, unauthorized merchant categories, duplicate claims. |
| AP Invoice Review | OCR mismatch, PO matching failures, duplicate invoices, unusual VAT amounts. |

## Compliance Pattern Integration

Odoo Copilot incorporates a scenario-based compliance operating model for finance workflows.

### Core objects
- **Check**: atomic detection rule
- **Scenario**: bundle of checks for a specific purpose (for example month-end close, VAT filing, liquidation audit, AP validation)
- **Run**: execution instance of a scenario
- **Finding**: exception/hit produced by a run
- **Remediation Task**: follow-up action assigned to a user or queue
- **Evidence Pack**: attachments, notes, outputs, and audit trail linked to runs/findings

### Primary workflow
1. Define checks
2. Bundle checks into scenarios
3. Execute scenario by schedule or ad hoc
4. Review findings in a unified inbox
5. Generate or assign remediation tasks
6. Track closure, escalation, and evidence
7. Export auditor-ready evidence and apply retention rules

### Representative scenario types
- Month-end close scenario
- BIR filing scenario
- Expense liquidation scenario
- AP invoice validation scenario
- Intercompany reconciliation scenario

### Representative finding types
- Missing receipt
- Duplicate invoice candidate
- Tax variance
- Filing completeness gap
- Unreconciled balance
- Missing approval
- Unsupported merchant or document classification mismatch

### Product requirement
No finance compliance workflow should terminate at a generic narrative answer when a structured finding, task, or evidence artifact should exist.

## Proposed Odoo Copilot Surfaces

### Detection
- Rule Library
- Scenario Builder
- Scenario Scheduler
- Run Monitor

### Investigation
- Findings Inbox
- Finding Detail
- Evidence Drawer
- Resolution/Task Pane

### Execution
- Assigned Tasks
- Auto-Remediation Rules
- Exception Triage Board

### Audit & Governance
- Evidence Export Center
- Retention / Archive Console
- Access Log / Read Audit

## Administrative Planes

To support enterprise-grade close and tax operations, Odoo Copilot includes five internal administrative planes.

### 1. Bootstrap & Landscape
Purpose:
- register entities, calendars, ledgers, jurisdictions, and source systems
- seed and enable scenarios/playbooks
- validate readiness before live execution

Proposed surfaces:
- System Landscape
- Bootstrap Status
- Scenario Enablement

### 2. Security & Access
Purpose:
- manage close/control roles
- assign authorization groups
- enforce separation between inquiry, review, approval, and admin actions

Proposed surfaces:
- Manage Roles
- Manage Role Assignments
- Authorization Groups

### 3. Connectivity & Integration
Purpose:
- register adapters and connected systems
- monitor synchronization and job handoff
- expose external dependency state to operators

Proposed surfaces:
- Connected Systems
- Sync Status
- External Job Results
- Adapter Registry

### 4. Monitoring & Reliability
Purpose:
- monitor run execution, connector health, and degraded mode
- capture retryable vs terminal failures
- support operator troubleshooting without losing context

Proposed surfaces:
- Run Monitor
- Connector Health
- Sync Failures
- Business Logs
- Degraded Mode Alerts

### 5. Lifecycle & Retention
Purpose:
- archive and restore close artifacts
- generate auditor-ready exports
- manage retention, anonymization, purge, and offboarding

Proposed surfaces:
- Evidence Export Center
- Archive / Restore Console
- Retention Policy Console
- Offboarding Checklist

### Product requirement
These administrative planes must be internal Odoo Copilot capabilities. They must not create separate user-facing products or bypass Odoo as the action authority.

## Close Operations Roles

Recommended role families:
- `copilot_close_admin`
- `copilot_close_designer`
- `copilot_close_operator`
- `copilot_close_approver`
- `copilot_close_auditor`
- `copilot_close_viewer`

Role visibility must govern:
- which scenarios/checks can be defined
- who can execute or rerun scenarios
- who can view findings/evidence
- who can approve, suppress, close, or purge
- who can perform export/archive/offboarding actions

## Architecture Overview

### Interaction channels

- Odoo native UI
- Teams
- Outlook
- Telegram
- email / inbound document channels
- optional web chat surfaces

### Core runtime model

1. User enters through an Odoo Copilot channel
2. Odoo Copilot gateway authenticates and assembles context
3. Skill router selects one or more internal skills/subagents
4. Tool adapters call Odoo, document extraction, workflow, and communication systems
5. Supabase records runs, events, artifacts, feedback, confidence, and escalations
6. Odoo remains the system of record for state-changing business actions

### Platform components

- **Odoo**: transactional authority
- **Microsoft Foundry**: shared multi-user agent runtime
- **Foundry Local**: local-only prototyping/testing
- **Azure Document Intelligence**: extraction/classification substrate
- **Supabase**: control plane (state, telemetry, feedback, artifacts)
- **Workflow layer**: routing / notifications / approvals / async jobs
- **Power Query**: data shaping / connectivity / repeatable preparation substrate
- **Fabric Mirroring**: near-real-time analytics replication into OneLake

## Data Plane Extensions

Odoo Copilot includes a governed data plane for ingestion, shaping, replication, and analytics access.

### Power Query role

Power Query is used for:
- connector-based source acquisition
- repeatable data shaping
- analyst-friendly transformation flows
- dataflow-based reusable preparation pipelines
- connection/governance-aware ingestion into downstream stores and reports

Power Query is not a separate end-user product in this architecture. Its outputs are surfaced through Odoo Copilot skills, review flows, dashboards, and downstream analytics experiences.

### Fabric Mirroring role

Fabric Mirroring is used for:
- near-real-time replication of operational or external data into OneLake
- mirrored SQL analytics access
- metadata mirroring where physical duplication is not required
- monitoring replication state, failures, and latency
- enabling downstream BI, lakehouse, Spark, and cross-database analytics scenarios

Fabric Mirroring is an analytics backplane and observability surface behind Odoo Copilot, not a replacement for Odoo transactional execution.

## Functional Requirements

### FR-1 — Multi-mode agent contract

The agent must expose explicit Research, Insight, Plan, Validate, Operate, and Monitor modes.

### FR-2 — Tool boundaries must be explicit

Each allowed tool must be documented and bounded by mode.

### FR-3 — Sensitive operations must delegate

Any ERP mutation must go through approved Odoo-side workflow/API paths and may not occur directly in the chat plane.

### FR-4 — Evidence-backed outputs

Finance-sensitive, compliance-sensitive, or action-bearing responses must include or depend on required evidence contracts.

### FR-5 — Fail-closed operational behavior

When evidence, policy, or certainty is insufficient, the agent must reject or escalate rather than continue.

### FR-6 — Evaluation pack required

The agent must have a maintained evaluation suite covering hallucination resistance, policy compliance, tool boundaries, and escalation behavior.

### FR-7 — Publish gates required

The agent may not be promoted or published unless evaluations, freshness, and governance checks pass.

### FR-8 — Observability required

Traces, evaluation outcomes, and operational failure paths must be inspectable.

### FR-9 — Skill-based capability expansion

New capabilities must be added as Odoo Copilot skills, not as separate products or standalone agents.

## Acceptance Criteria

- Spec bundle exists and is internally consistent.
- Mode boundaries are explicit.
- Tool boundary policy exists.
- Sensitive operations are delegated, not directly executed.
- Evaluation criteria exist for each major risk surface.
- Publish gates are defined.
- No document implies the agent is the transactional SoR.
- All finance capabilities are framed as Odoo Copilot skills.
- Foundry Local is restricted to dev/offline use.
- Azure Document Intelligence is the default extraction substrate.
- Power Query and Fabric Mirroring are positioned as backend substrates, not user-facing products.

## Risks

- Tool drift without eval drift checks
- Mode confusion causing unsafe execution expectations
- Hidden write paths through backend workflows
- Stale evaluation evidence after instruction changes
- Overbroad "Operate" capability claims
- Skill fragmentation back into standalone products

## Sub-Agent Strategy

`ipai_odoo_copilot` is the top-level bridge agent. Domain capabilities are modeled as bounded sub-agents — not standalone products.

### Sub-agent routing

Sub-agent selection is determined by:
1. **User intent** — parsed from the chat/command input
2. **Active Odoo model/view** — the current ERP context (e.g., project dashboard, invoice form)
3. **Configured domain** — which sub-agents are enabled for the user's company/role
4. **Explicit entry point** — a direct sub-agent invocation from a UI surface or shortcut

### Initial sub-agents

| Sub-Agent | Domain | Spec Reference |
|-----------|--------|----------------|
| `project_copilot` | Project management (dashboard, profitability, milestones, templates) | This PRD |
| `taxpulse_ph` | BIR tax compliance (PH) | `spec/tax-pulse-sub-agent/` |
| `finance_reconciliation` | GL, intercompany, variance, collections | This PRD |

All sub-agents inherit the constitution's authority model, mode boundaries, and failure contract.

## Project Copilot Sub-Agent

The first major business-domain sub-agent, anchored to the Odoo Project module.

### Capabilities (Release 1 — read-only advisory)
- Project dashboard summarization (status, health, blockers)
- Milestone and risk interpretation
- Profitability analysis context (margin, burn rate, budget vs actual)
- Template recommendation based on project type

### Anchoring
- Evaluation scaffold: OpenAI Academy product pack scenarios
- Odoo models: `project.project`, `project.task`, `project.milestone`, `account.analytic.line`
- Entry point: Odoo Project dashboard systray or project-level action button

### Constraints
- Release 1 is advisory-only — no project mutation from the agent
- Profitability data is read from Odoo; agent does not compute or post financial entries
- Escalation to human when confidence is insufficient

## Prompt Pack Sources

External prompt/eval packs that inform sub-agent evaluation scaffolds:

| Source | Target Sub-Agent | Use |
|--------|-----------------|-----|
| OpenAI Academy — product resource | `project_copilot` | Eval scenarios for project Q&A, status summarization, risk interpretation |
| OpenAI Academy — finserv resource | `taxpulse_ph`, `finance_reconciliation` | Eval scenarios for tax guidance, reconciliation, variance analysis |
| Microsoft Copilot Finance scenarios | `finance_reconciliation` | Benchmark for reconciliation, variance, and collections workflows |
| Balance Sheet Reconciliation Agent deck | `finance_reconciliation` | Contract reference for reconciliation entry points and evidence model |

These are eval/design inputs, not runtime dependencies. The copilot's runtime authority remains the constitution and Odoo SoR.
