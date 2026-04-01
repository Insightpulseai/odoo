# PRD — Pulser Assistant: Runtime Layer

## Status
Draft

## Problem

Pulser needs a dedicated implementation layer for agents, workflows, tool bindings, memory/context, evals, and interop instead of scattering that logic across Odoo or web apps. Microsoft Agent Framework is explicitly built for both **agents** (open-ended reasoning with tools) and **graph-based workflows** (deterministic multi-step processes), with sessions, context providers, middleware, MCP integration, and human-in-the-loop workflow control.

Reference: [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)

## Tier 1 Ownership: Pulser Runtime Layer

The `agents` repo owns the Pulser runtime implementation — agent templates, workflow templates, tool bindings, context providers, safety middleware, evaluations, and interoperability adapters.

## Product Vision

Position `agents` as the **Pulser Runtime Layer** for:
- Pulser agent templates (open-ended reasoning with tool access)
- Pulser workflow templates (graph-based, checkpointed, HITL-enabled)
- Tool bindings (Odoo adapters, platform queries, data-intelligence lookups)
- Context/memory providers (session state, record context, conversation history)
- Safety middleware (pre/post execution policy checks, content safety)
- MCP / A2A / API interoperability
- Evaluation suites (per-capability package safety and quality gates)
- Host/runtime contracts (Foundry Agent Service, Azure Functions, A2A)

## Core Surfaces

| Surface | Description |
|---------|-------------|
| PulserAgentTemplate | Reusable agent with tool access, memory, and system prompt |
| PulserWorkflowTemplate | Graph-based multi-step workflow with checkpointing and HITL |
| PulserToolBinding | Tool definition for Odoo/platform/data-intelligence connectors |
| PulserContextProvider | Session, memory, and record-context management |
| PulserSafetyMiddleware | Pre/post execution policy checks and content safety |
| PulserEvalSuite | Evaluation datasets and runners per capability package |
| PulserInteropAdapter | MCP server exposure, A2A endpoints, API adapters |
| PulserHostContract | Hosting configuration for Foundry Agent Service / ACA / Functions |

## Users

| Role | Primary Interaction |
|------|-------------------|
| Agent Developer | Create/modify agent and workflow templates |
| Platform Admin | Review eval results, approve capability promotions |
| Finance Manager | End-user interacting through agents (via web/Odoo) |
| QA Engineer | Run eval suites, review safety middleware results |

## Non-Goals

- Not the registry/control plane (that is `platform`)
- Not the main UI shell (that is `web`)
- Not the canonical business-process data model layer (that is `data-intelligence`)
- Not direct ownership of Odoo persistence logic (that is `odoo`)
- Not a reimplementation of Foundry Agent Service hosting (Foundry-native)

## Capability Type Runtime Logic

Benchmark: SAP Joule capability taxonomy applied to agent/workflow runtime.

Each capability type has distinct runtime behavior:

### Informational
- Retrieval/grounding pattern: search grounding sources, assemble context, generate answer
- Required outputs: answer, confidence level, evidence bundle, source references
- Safety: lowest risk — no mutations, evidence-backed answers

### Navigational
- Resolver logic: map user intent to Odoo menu/action/record/report target
- Required outputs: destination type, destination reference, permission-aware open target
- Safety: low risk — read-only navigation, permission-filtered targets

### Transactional
- Stronger safety rules: pre-execution policy checks, approval workflows
- Required outputs: action proposal, affected records, risk level, required approvals, execution result
- Default action mode: `suggest_only` or `approval_required`
- Direct execution limited to narrow, reversible, low-risk actions

## Tax Guru Copilot — Agent Objects

Benchmark: AvaTax (tax determination core) + Joule (capability taxonomy) + Finance scenario patterns (KPI/role packaging).

### Tax Determination Workflow

Tax Guru needs a determination layer, not just prompt logic:
- Jurisdiction lookup
- Tax type selection
- Product/service taxability classification
- Exception detection
- Use-tax / withholding / VAT/GST logic
- Tax evidence/explanation bundle

For PH-first context: VAT/non-VAT, withholding classifications, BIR rule guidance, invoice/expense/procurement tax treatment, exception workflows.

### Agent Domain Objects

| Object | Description |
|--------|-------------|
| PulserTaxDeterminationRequest | Incoming tax determination: company, transaction type, counterparty, line items, jurisdiction context, source record |
| PulserTaxDeterminationResult | Recommended treatment, tax components, explanation, evidence, confidence, escalation flag |
| PulserTaxPolicyAnswer | Policy Q&A response: question, answer summary, rule source refs, evidence, confidence |
| PulserTaxActionProposal | Proposed tax action: type, payload, risk level, approval required flag |

### Tax Safety Rules

- Informational tax outputs require evidence when grounded context exists
- Navigational tax outputs must be permission-aware
- Transactional tax outputs default to `suggest_only` or `approval_required`
- Direct execution limited to narrow, reversible, low-risk tax actions
- Tax reasoning and determination workflows live in `agents`, not in Odoo

### Tax Domain Pack Integration

Tax Guru agents consume domain packs (e.g., TaxPulse PH Pack) as execution and evidence providers.

TaxPulse PH Pack is treated as:
- A **transactional adapter** for PH BIR compliance
- A **localized PH compliance source** (BIR forms, agency mappings)
- A **tax artifact producer** (reports, evidence bundles, sync events)

Tax Guru reasoning remains external to the pack. Agents call into the pack for:
- Form status and computed values
- Sync/report status
- Exception triggers
- Evidence references

## PH Source Selection Policy

Benchmark: BIR legal authority hierarchy applied to agent source selection and citation rules. Odoo 18 accounting localization as ERP execution benchmark.

### Source Hierarchy (6 Tiers)

1. **Tier 1 — Legal authority**: BIR Revenue Issuances, Legal Matters. Final legal basis and rule interpretation.
2. **Tier 2 — Taxpayer guidance**: BIR Tax Information. Plain-language explanation and filing guidance.
3. **Tier 3 — Execution-entry/navigation**: eBIRForms, BIR eServices. Official filing or service channel destinations.
4. **Tier 4 — Professional competency**: CGPA CBOK, Competency Framework. Answer-quality evaluation, analytical rigor, ethics, communication style.
5. **Tier 5 — ERP execution benchmark**: Odoo 18 accounting localization pattern. How PH tax should be represented in Odoo: localization module structure, tax groups, taxes, tax reports.
6. **Tier 6 — Internal transaction context**: Odoo records, TaxPulse-PH-Pack, company policy/profile data. Case context, not legal authority.

### Answer Types and Contracts

```yaml
TaxGuruPHAnswerContract:
  answer_type: enum
    - explanation        # "What rule applies?" / "Why was this taxed this way?"
    - recommendation     # "What should we do next?"
    - navigation         # "Where do I file / where do I go?"
    - action_proposal    # "Prepare/update/create something in Odoo"
    - exception_review   # Sources conflict or case not safely determinable
```

#### A. Explanation

```yaml
TaxGuruPHExplanation:
  answer_key: string
  question: string
  summary: string
  legal_basis_summary: string
  guidance_summary: string|null
  authoritative_citations: [PulserPHCitation]
  supporting_citations: [PulserPHCitation]
  internal_context_refs: [string]
  confidence_score: number
  ambiguity_flags: [string]
  requires_human_review: boolean
```

Rules: Must include at least one BIR citation (Tier 1 or 2). Legal conclusions prefer Tier 1. Internal ERP context may refine but not override BIR authority.

#### B. Recommendation

```yaml
TaxGuruPHRecommendation:
  answer_key: string
  summary: string
  recommended_next_steps: [string]
  rationale: string
  legal_basis_summary: string|null
  evidence_key: string
  confidence_score: number
  risk_level: enum [low, medium, high]
  requires_human_review: boolean
```

#### C. Navigation

```yaml
TaxGuruPHNavigation:
  answer_key: string
  summary: string
  official_destinations:
    - label: string
      destination_type: enum  # bir_service, form, odoo_view, report
      target_ref: string
      official: boolean
      reason: string
  supporting_citations: [PulserPHCitation]
```

Rules: Prefer eBIRForms/eServices for official destinations. Render official BIR entries separately from internal Odoo destinations.

#### D. Action Proposal

```yaml
TaxGuruPHActionProposal:
  answer_key: string
  summary: string
  proposed_action: string
  action_mode: enum [read_only, suggest_only, approval_required, direct_execution]
  affected_records: [string]
  execution_rationale: string
  evidence_key: string
  confidence_score: number
  approval_required: boolean
```

Rules: Default PH tax actions to `suggest_only` or `approval_required`. Only narrow reversible actions may use `direct_execution`.

#### E. Exception Review

```yaml
TaxGuruPHExceptionReview:
  answer_key: string
  summary: string
  exception_type: enum [missing_authority, conflicting_sources, unsupported_case, ambiguous_rule_application]
  open_questions: [string]
  evidence_key: string
  escalation_recommendation: string
  assigned_role_hint: string|null
```

### Source-Selection Rules

Agents must select grounding sources in authority-tier order:

1. **Tier 1 first**: If a BIR Revenue Issuance or Revenue Memorandum Order covers the query, cite it as primary authority
2. **Tier 2 supplement**: BIR Tax Information supplements Tier 1 for plain-language explanation
3. **Tier 3 for navigation**: eBIRForms/eServices references for filing and status queries
4. **Tier 4 for reasoning**: CGPA CBOK for professional reasoning context — never as legal authority
5. **Tier 5 for execution model**: Odoo localization cited only when the answer requires ERP implementation mapping
6. **Tier 6 last**: Odoo records, company policy — case context only, always subordinate to official sources

### Citation Rules

- **Explanations**: Must include at least one BIR citation (Tier 1-2). Legal conclusions prefer Tier 1.
- **Recommendations**: Must cite legal basis when available. Risk level must be assessed.
- **Navigation**: Must cite Tier 3 (eBIRForms/eServices) for official filing destinations. Separate official from internal Odoo destinations.
- **Action proposals**: Must cite Tier 1-2 authority for the proposed action. Odoo localization (Tier 5) cited for execution mapping. No tax action proposal without authority citation.
- **Exception reviews**: Must document what authority is missing and what tier is needed to resolve.
- **No unsupported legal conclusion without citation**: If insufficient authority (Tier 1-2) exists, set `unsupported_flag: true` and escalate.
- **Authority conflict resolution**: If Tier 1 and Tier 6 conflict, Tier 1 wins. Flag as `PulserTaxExceptionCase` with `exception_type: conflicting_sources`.

### Capability-to-Source Mapping

| Capability Package | Required Sources | Minimum Authority |
|-------------------|-----------------|-------------------|
| `pulser_tax_info` | Tier 1-2 (BIR issuances, tax information) | Tier 2 |
| `pulser_tax_navigation` | Tier 3 (eBIRForms, eServices) | Tier 3 |
| `pulser_tax_actions` | Tier 1-2 + Tier 5 (legal authority + execution model) | Tier 1 |
| `pulser_tax_grounding` | Tier 1-5 (all PH grounding sources) | Tier 2 |
| `pulser_tax_exception_review` | Tier 1-2 + Tier 6 (authority + ERP context) | Tier 1 |
| `pulser_tax_policy_guidance` | Tier 1-2 + Tier 4 (BIR + CGPA) | Tier 2 |
| `pulser_tax_filing_prep` | Tier 1-3 (authority + filing portals) | Tier 2 |

### Response Contract Rules

- Every tax answer must include a `PulserTaxEvidenceBundle`
- Evidence bundle distinguishes: `authoritative_citations` (Tier 1-2), `supporting_citations` (Tier 3-4), `execution_model_citations` (Tier 5)
- `confidence_score` and `requires_human_review` must be computed
- If `authoritative_citations` is empty for a compliance question, set `unsupported_flag: true`
- Exception cases must include `evidence_gap`, `open_questions`, and `escalation_recommendation`
- Odoo implementation recommendations may cite the localization benchmark (Tier 5) but it never substitutes for BIR legal authority

## Functional Requirements

### FR-1 — Agent templates
Support single-agent patterns with tool access, memory, and configurable system prompts.

### FR-2 — Workflow templates
Support graph-based multi-step workflows with explicit routing, checkpointing, and human-in-the-loop control.

### FR-3 — Tool bindings
Provide typed tool definitions for Odoo ERP actions, platform queries, and data-intelligence lookups.

### FR-4 — Context providers
Support session state, conversation history, and record-aware context assembly.

### FR-5 — Safety middleware
All high-impact actions must pass through safety middleware with configurable policy checks.

### FR-6 — Evaluations
Each capability package must have eval suites covering safety, quality, and functional correctness.

### FR-7 — Interoperability
Support MCP server exposure, A2A agent endpoints, and REST API adapters.

### FR-8 — Agent vs. workflow distinction
Use agents for open-ended reasoning/tool use. Use workflows for deterministic business processes. This distinction must be explicit in template contracts.

## Success Metrics

- At least one agent template operational on Foundry Agent Service
- At least one workflow template operational with checkpointing
- Eval suites passing for all promoted capability packages
- Safety middleware active on all finance-sensitive actions
- MCP interop operational for at least one external consumer
- Agent/workflow distinction enforced in all new templates

## Benchmark

Agent Framework: agents for open-ended reasoning, workflows for explicit processes, sessions/context for state, middleware for policy, MCP/A2A for interop, DevUI for dev/test.
