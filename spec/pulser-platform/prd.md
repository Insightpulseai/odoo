# PRD — Pulser Assistant: Control Plane

## Status
Draft

## Problem

Pulser currently risks being treated as a feature inside Odoo instead of a governed assistant platform. The control plane must own tenant/environment registration, identity binding, capability-package enablement, grounding-source registration, preview/prod release channels, and evidence-backed promotion. This matches Foundry's governance role and Joule's formation/onboarding model.

Reference: [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

## Tier 1 Ownership: Pulser Control Plane

The `platform` repo owns the Pulser control plane — formations, capability packages, identity, grounding, promotion, and evidence. It is the org-specific overlay on top of Microsoft Foundry, not a duplicate of Foundry-native controls.

## Product Vision

Position `platform` as the **Pulser Control Plane** for:
- Pulser formations (binding systems, capabilities, grounding, and environments)
- Capability package registry (separately enableable and promotable units)
- Integrated system registry (Odoo, data-intelligence, external services)
- Grounding source registry (documents, knowledge bases, data products)
- Grounding pipeline registry (ingestion, chunking, indexing, refresh)
- Identity bindings (one canonical Pulser identity per human/operator)
- Preview/prod promotion records (preview always precedes production)
- Validation and evidence artifacts (no promotion without evidence)

## Core Objects

| Object | Description |
|--------|-------------|
| PulserFormation | Top-level binding: systems + capabilities + grounding + environment |
| PulserCapabilityPackage | Separately enableable agent/workflow capability unit |
| PulserIntegrationTarget | Registered integrated system (Odoo, data-intelligence, etc.) |
| PulserGroundingSource | Registered knowledge/document/data source for assistant grounding |
| PulserGroundingPipeline | Ingestion, chunking, indexing, refresh pipeline for a grounding source |
| PulserIdentityBinding | Maps human/operator identity to Pulser assistant identity |
| PulserValidationRun | Structured validation execution with typed checks |
| PulserEvidenceArtifact | Proof of deployment/validation/compliance attached to promotion |
| PulserPromotionRecord | Release-to-evidence binding for promoted formations/packages |

## Users

| Role | Primary Interaction |
|------|-------------------|
| Platform Admin | Formation setup, identity binding, capability enablement |
| Agent Developer | Capability package registration, preview testing |
| Data Engineer | Grounding source/pipeline registration and refresh |
| Finance Manager | End-user of promoted Pulser capabilities |
| Compliance Officer | Evidence review, promotion gate approval |

## Non-Goals

- Not the actual agent runtime (that is `agents`)
- Not the browser application shell (that is `web`)
- Not the Odoo transactional action layer (that is `odoo`)
- Not a reimplementation of Foundry-native resource/project controls
- Not the model deployment authority (Foundry-native)
- Not the tracing/monitoring infrastructure (Foundry-native)

## Capability Taxonomy

Benchmark: SAP Joule Marketplace listing — three capability types applied across all Pulser domains.

| Capability Type | What It Does | Odoo Examples |
|----------------|-------------|---------------|
| **Transactional** | Completes approved actions | Create draft invoice, register payment, create purchase request, assign task |
| **Navigational** | Takes user to correct workflow/screen | Open overdue invoices, vendor ledger, purchase approvals, employee expense queue |
| **Informational** | Answers with grounded business context | Policy Q&A, status summaries, KPI explanations, document-based answers |

**Design rules**:
- `PulserCapabilityPackage.capability_type` enum: `transactional`, `navigational`, `informational`
- Role-aware access is part of the product contract, not backend plumbing
- Authorization filters apply to responses, actions, navigation targets, and grounded answers
- Transactional is highest trust/risk class — rollout order: informational → navigational → transactional

### Recommended Capability Packages

Model by domain × capability type:

| Package | Type | Domain |
|---------|------|--------|
| `pulser_finance_info` | informational | Finance |
| `pulser_finance_navigation` | navigational | Finance |
| `pulser_finance_actions` | transactional | Finance |
| `pulser_collections_info` | informational | Collections |
| `pulser_collections_navigation` | navigational | Collections |
| `pulser_collections_actions` | transactional | Collections |
| `pulser_procurement_info` | informational | Procurement |
| `pulser_procurement_navigation` | navigational | Procurement |
| `pulser_procurement_actions` | transactional | Procurement |
| `pulser_bir_compliance_info` | informational | BIR Compliance |

### Product Statement

**Pulser Assistant is a role-aware business copilot that supports transactional, navigational, and informational capabilities across Odoo and connected systems.**

### Integration Target Model

Pulser is a single conversational surface across pre-integrated systems, not a single app database. Connected systems include Odoo, data-intelligence marts, external services — all backed by the same capability packages and identity model.

### Grounding as First-Class Subsystem

Grounding is explicitly part of the product, not "RAG later":
- Grounding sources (documents, knowledge bases, data products)
- Uploaded-document knowledge
- ERP-aware factual retrieval
- Summarized answers with sources/evidence

## Tax Guru Copilot — Platform Objects

Benchmark: AvaTax (tax engine/compliance behavior) + Joule (capability taxonomy) + Finance scenario patterns (KPI/role packaging).

**Product statement**: Tax Guru Copilot is a role-aware tax sub-agent that explains tax rules, guides users to the right workflow, and performs bounded tax-related actions across Odoo and connected systems, backed by grounded tax content, transaction data, and audit-ready evidence.

### Tax Capability Packages

| Package | Type | Description |
|---------|------|-------------|
| `pulser_tax_info` | informational | Tax rule explanations, policy Q&A, treatment summaries |
| `pulser_tax_navigation` | navigational | Navigate to tax config, invoice tax details, filing workspace |
| `pulser_tax_actions` | transactional | Propose tax codes, create review tasks, draft corrections |
| `pulser_tax_grounding` | informational | Tax document/knowledge grounding pipeline |
| `pulser_tax_exception_review` | transactional | Exception case management and resolution |
| `pulser_tax_policy_guidance` | informational | BIR/accounting guidance updates and summaries |
| `pulser_tax_filing_prep` | transactional | Filing readiness work items and prep tasks |

### Tax KPIs

- tax_determination_accuracy
- exception_rate
- time_to_resolve_tax_questions
- time_to_review_tax_treatment
- under_overcharged_transaction_rate
- audit_prep_time
- filing_readiness
- auto_classification_rate

### Platform Domain Objects

| Object | Description |
|--------|-------------|
| PulserTaxRuleSource | Tax rule authority (BIR, company policy, external engine, accounting guidance) with jurisdiction, version, effective dates |
| PulserTaxJurisdictionProfile | Jurisdiction metadata (country/region/city/company, default tax regime) |
| PulserTaxCapabilityProfile | Per-capability config: supported tax types, jurisdictions, action modes, required roles, grounding/eval bindings |
| PulserTaxEvidenceBundle | Transaction-level evidence: rule sources, document refs, explanation, confidence score |
| PulserTaxExceptionCase | Exception tracking: type (missing_code, ambiguous_taxability, variance, unsupported_case), severity, assignment, evidence |

### Tax Guru Domain Packs

Tax Guru Copilot includes bounded domain packs, each owning localized tax execution for a specific jurisdiction/domain.

#### TaxPulse PH Pack

**Role**: Philippine BIR tax execution and compliance pack for Odoo

**Source**: `github.com/jgtolentino/TaxPulse-PH-Pack`

**Owns**:
- BIR form data structures (1601-C, 2550Q, 1702-RT)
- Tax computation from Odoo accounting records
- 8-agency configuration mappings
- Compliance report generation
- Sync/export of tax artifacts and evidence

**Does NOT own**:
- Global tax reasoning engine (that is `agents`)
- Cross-system tax policy registry (that is `platform`)
- Full conversational copilot orchestration (that is `agents` + `web`)
- Assistant control-plane governance (that is `platform`)

**Pack hierarchy**:
```text
Tax Guru Copilot
└── Domain Packs
    ├── TaxPulse-PH-Pack (PH BIR compliance)
    ├── future VAT/GST/global pack
    ├── future withholding pack
    └── future policy-grounding pack
```

## PH Grounding Hierarchy — Platform Authority Model

Benchmark: BIR legal authority (Revenue Issuances, Revenue Memorandum Orders) as canonical tax source. Odoo 18 accounting localization as ERP execution benchmark.

### Grounding Source Tiers

| Tier | Source Class | Authority Level | Platform Role |
|------|-------------|-----------------|---------------|
| **Tier 0** | System policy, tenant controls | System-level | Enforce as hard constraints (never overridden by content) |
| **Tier 1** | BIR Revenue Issuances, Revenue Memorandum Orders, Legal Matters | **Legal authority** | Register with `source_class: bir_legal_authority` |
| **Tier 2** | BIR Tax Information (e.g., VAT threshold, withholding schedules) | Taxpayer guidance | Register with `source_class: bir_taxpayer_guidance` |
| **Tier 3** | eBIRForms, BIR eServices (filing portals, status APIs) | Execution/navigation entry | Register with `source_class: bir_execution_entry` |
| **Tier 4** | CGPA Philippines (CBOK, Competency Framework) | Professional competency benchmark | Register with `source_class: professional_competency_reference` |
| **Tier 5** | Odoo 18 accounting localization pattern | ERP execution benchmark | Register with `source_class: odoo_execution_benchmark` |
| **Tier 6** | Odoo records, TaxPulse-PH-Pack, company policy/profile data | Internal transaction context | Register with `source_class: internal_transaction_context` |

**Authority precedence**: Tier 1 > Tier 2 > Tier 3 > Tier 4 > Tier 5 > Tier 6. Internal ERP context (Tier 6) and Odoo execution benchmark (Tier 5) NEVER override BIR legal authority (Tier 1). CGPA (Tier 4) is evaluative/supporting, not legal authority. Odoo localization (Tier 5) tells how PH tax rules land in ERP, not what the rules are.

### Evidence Schema Objects

#### `PulserPHGroundingSource`

```yaml
PulserPHGroundingSource:
  source_key: string
  source_class: enum
    - bir_legal_authority
    - bir_taxpayer_guidance
    - bir_execution_entry
    - professional_competency_reference
    - odoo_execution_benchmark
    - internal_transaction_context
  source_name: string
  source_url: string
  authority_level: enum
    - legal_authority
    - guidance
    - execution_entry
    - competency
    - execution_model
    - internal_context
  jurisdiction: "PH"
  active: boolean
```

#### `PulserPHCitation`

```yaml
PulserPHCitation:
  citation_key: string
  source_key: string
  source_title: string
  source_url: string
  authority_level: enum
  retrieved_at: datetime
  effective_date: date|null
  section_label: string|null
  snippet_summary: string
  confidence: number
```

#### `PulserTaxEvidenceBundle` (expanded)

```yaml
PulserTaxEvidenceBundle:
  evidence_key: string
  capability_key: string
  answer_type: enum  # explanation, recommendation, navigation, action_proposal, exception_review
  jurisdiction: "PH"
  authoritative_citations: [PulserPHCitation]    # Tier 1-2 (BIR legal/guidance)
  supporting_citations: [PulserPHCitation]        # Tier 3-4 (BIR services, CGPA)
  execution_model_citations: [PulserPHCitation]   # Tier 5 (Odoo localization)
  internal_context_refs:
    - type: string
      ref: string
  legal_basis_summary: string
  guidance_summary: string|null
  execution_notes: string|null
  ambiguity_flags: [string]
  confidence_score: number
  requires_human_review: boolean
  created_at: datetime
```

`execution_model_citations` exists because PH tax answers that end in Odoo actions must distinguish **what the rule is** (BIR) from **how Odoo should operationalize it** (localization model).

#### `TaxAuthorityBadge`

```yaml
TaxAuthorityBadge:
  badge_type: enum
    - BIR_Legal
    - BIR_Guidance
    - BIR_Service
    - CGPA_Competency
    - Odoo_Execution
    - Internal_Context
  label: string
  priority_rank: integer
```

Render rule: show BIR_Legal first when present, BIR_Guidance second. Show Odoo_Execution only when the answer includes an Odoo implementation recommendation.

#### `PulserTaxAnswerRecord`

```yaml
PulserTaxAnswerRecord:
  answer_key: string
  answer_type: enum
    - explanation
    - recommendation
    - navigation
    - action_proposal
    - exception_review
  question_text: string
  answer_text: string
  evidence_bundle_ref: string  # link to PulserTaxEvidenceBundle
  authority_tier_used: integer
  unsupported_flag: boolean
  created_at: datetime
```

#### `PulserTaxExceptionCase` (expanded)

```yaml
PulserTaxExceptionCase:
  case_key: string
  exception_type: enum
    - missing_authority
    - conflicting_sources
    - unsupported_case
    - ambiguous_rule_application
    - missing_code
    - ambiguous_taxability
    - variance
    - stale_source
  severity: enum [low, medium, high, critical]
  source_record_ref: string
  evidence_gap: string
  required_authority_tier: integer
  open_questions: [string]
  escalation_recommendation: string
  assigned_role_hint: string|null
  assignee: string|null
  status: enum [open, investigating, resolved, escalated]
  resolution_evidence_ref: string|null
```

## Functional Requirements

### FR-1 — Formation management
The system must support creating, updating, and retiring Pulser formations that bind systems, capabilities, grounding, and environments.

### FR-2 — Capability package registry
Each capability package must be independently enableable, testable, and promotable.

### FR-3 — Identity binding
Each human/operator must have exactly one canonical Pulser identity binding, enforced by Entra ID.

### FR-4 — Grounding source registration
All grounding sources must be registered with metadata (type, refresh cadence, owner, access policy).

### FR-5 — Grounding pipeline management
Grounding pipelines must be tracked with status, last refresh timestamp, and quality metrics.

### FR-6 — Preview/prod channels
Every formation and capability package must support preview and production channels. Preview always precedes production.

### FR-7 — Promotion with evidence
No formation or capability package may be promoted to production without attached validation evidence.

### FR-8 — Validation framework
The system must support typed validation runs (smoke, contract, safety, quality) with structured results.

## Success Metrics

- At least one Pulser formation registered with systems, capabilities, and grounding
- At least one capability package promoted through preview → production with evidence
- All grounding sources registered with refresh status
- Identity bindings enforced for all active Pulser users
- Zero direct-to-production promotions (all go through preview first)

## Benchmark

Joule's formation/onboarding model: formations bind integrated products, capabilities, and grounding under governance. Preview/production separation. Identity/trust strictness. Evidence-backed promotion.
