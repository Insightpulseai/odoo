# Plan — Pulser Assistant: Control Plane

## Status
Draft

## Architecture Approach

### Registry Services
- **Formation registry**: CRUD for PulserFormation objects with system/capability/grounding bindings
- **Capability package registry**: Independent enablement, versioning, and promotion state tracking
- **Integration target registry**: Registered systems (Odoo, data-intelligence, external services) with connection status
- **Grounding registry**: Sources + pipelines with refresh status and quality metrics
- **Identity registry**: Entra ID-backed identity bindings for all Pulser users

### Environment/Channel Model
- **Preview channel**: Isolated environment for testing new formations, capabilities, and grounding changes
- **Production channel**: Promoted assets only, evidence-gated
- **Channel switching**: Operator-controlled, with audit trail
- Mirrors Joule's preview/production separation benchmark

### Promotion/Evidence Service
- Promotion state machine: `draft → preview → validated → promoted → retired`
- Evidence binding: each promotion record links to validation runs and evidence artifacts
- Promotion gate: blocks production promotion if critical validations fail
- AzDO pipeline integration for automated promotion gates

### Repo-to-Runtime Mapping
- Registration adapters for `agents` (capability packages → agent templates)
- Registration adapters for `web` (surfaces → hosted UI components)
- Registration adapters for `odoo` (integration target → adapter modules)
- Cross-repo traceability: formation → capability → repo source → deployed artifact

## Design Principles

1. **One identity per human**: Each operator has exactly one canonical Pulser identity, bound to Entra ID
2. **One formation binds all**: A formation object binds systems, capabilities, grounding, and environment — the unit of governance
3. **Evidence-gated promotion**: Every production promotion requires validation evidence
4. **Separately promotable capabilities**: Capability packages are independently enableable and promotable within a formation
5. **Preview precedes production**: New assistant behaviors or grounding changes must pass through preview first
6. **Grounding as managed asset**: Grounding sources and pipelines are first-class registered objects, not hidden file uploads

- **Capability taxonomy**: All capability packages must be classified as transactional, navigational, or informational (Joule benchmark)
- **Role-aware by design**: Authorization is part of the product contract — responses, actions, navigation targets, and grounded answers are all permission-filtered

## Cross-Repo Integration

| Repo | `platform` provides | `platform` consumes |
|------|-------------------|-------------------|
| `agents` | Capability package registration, promotion state | Agent template metadata, eval results |
| `web` | Surface registration, formation metadata | UI deployment status |
| `odoo` | Integration target registration, action policies | Adapter module status, telemetry events |
| `data-intelligence` | Grounding source registration | Gold mart metadata, refresh status |
| `infra` | — | Azure resource provisioning status |

## Foundry Delegation

Per `docs/contracts/FOUNDRY_DELEGATION_CONTRACT.md`:
- Foundry owns: model deployment, agent hosting, tool catalog, memory, tracing, evaluations, RBAC
- `platform` owns: formations, capability packages, identity bindings, grounding registries, promotion, evidence, cross-repo registration

### Phase P5 — Tax Guru Control Plane Objects

- Add PulserTaxRuleSource, PulserTaxJurisdictionProfile to platform registry
- Add PulserTaxCapabilityProfile with capability_type enum binding
- Add PulserTaxEvidenceBundle and PulserTaxExceptionCase models
- Register tax capability packages (7 packages, 3 capability types)
- Add tax KPI tracking to evidence model

### Phase P6 — PH Grounding Hierarchy and Evidence Schema

- Register PH grounding sources (6 tiers) as PulserPHGroundingSource objects:
  - Tier 1: BIR Revenue Issuances, Legal Matters (`bir_legal_authority`)
  - Tier 2: BIR Tax Information (`bir_taxpayer_guidance`)
  - Tier 3: eBIRForms, eServices (`bir_execution_entry`)
  - Tier 4: CGPA CBOK, Competency Framework (`professional_competency_reference`)
  - Tier 5: Odoo 18 accounting localization (`odoo_execution_benchmark`)
  - Tier 6: Odoo records, TaxPulse-PH-Pack, company policy (`internal_transaction_context`)
- Implement source_class enum with all 6 classes
- Add PulserPHCitation model with source_key, authority_level, snippet_summary, effective_date
- Expand PulserTaxEvidenceBundle with three citation groups: authoritative (Tier 1-2), supporting (Tier 3-4), execution_model (Tier 5)
- Add TaxAuthorityBadge for UI rendering with priority_rank
- Add PulserTaxAnswerRecord with 5 answer types: explanation, recommendation, navigation, action_proposal, exception_review
- Expand PulserTaxExceptionCase with evidence_gap, open_questions, escalation_recommendation
- Enforce authority precedence: BIR legal > BIR guidance > BIR execution-entry > CGPA competency > Odoo execution benchmark > internal context
- Odoo execution benchmark (Tier 5) cannot override BIR legal authority (Tier 1)
- Register BIR Revenue Issuances grounding pipeline (Tier 1)
- Register CGPA CBOK grounding pipeline (Tier 4) — evaluative only, never legal authority
- Register Odoo 18 localization grounding pipeline (Tier 5) — execution model only
