# Feature Specification: PulseTax — Agentic Tax Control Plane

**Feature Branch**: `[001-pulsetax-agentic-control-plane]`
**Created**: `2026-04-10`
**Status**: `Draft`
**Input**: Reverse of "AvaTax: Agentic Tax and Compliance"

---

## Summary

Build an **agentic tax and compliance control plane** for ERP, commerce, and finance systems that goes beyond tax calculation to deliver:

1. **Deterministic tax decisions** with explainable rules and evidence
2. **Localized compliance packs** for PH first, then ASEAN and broader APAC
3. **Closed-loop compliance operations** across quote, invoice, payment, filing, reconciliation, and audit
4. **Human-governed agent workflows** for exception handling, document validation, filing preparation, and regulatory change management

The product should feel like the operational layer that finance and tax teams actually run, not just a calculation API.

---

## Problem Statement

Existing tax engines are strong at real-time calculation and broad jurisdiction coverage, but they often leave customers to assemble the rest of the compliance operating model themselves: source-document validation, filing workpapers, jurisdiction-specific evidence, exception queues, approval flows, reconciliation, and audit traceability.

This gap is especially painful in markets where:

* localized compliance workflows are fragmented
* tax data quality from ERP/AP/AR systems is inconsistent
* tax teams need explainability, not just answers
* electronic invoicing and structured reporting obligations are tightening
* companies need both **automation** and **controllership-grade review**

In the Philippines specifically, the compliance surface is not just "calculate VAT correctly." It includes BIR-oriented e-invoicing, structured invoice data, certification flows, withholding-aware operations, and document/evidence integrity.

---

## Product Vision

**PulseTax** is the tax operating system for modern finance teams:

* **Agentic** enough to automate routine compliance work
* **Deterministic** enough for controllers and auditors to trust
* **Localized** enough to win in PH/ASEAN
* **Composable** enough to plug into Odoo, Dynamics, SAP, NetSuite, Shopify, WooCommerce, and custom systems
* **Evidence-native** enough to withstand audit, dispute, and filing review

---

## Goals

### Primary Goals

1. Deliver correct tax determination for sales, purchases, and cross-border transactions.
2. Turn every tax outcome into an **explainable decision** with underlying rule, source data, and evidence.
3. Provide **localized compliance packs** that include e-invoicing, withholding, filing prep, and audit artifacts.
4. Reduce manual finance workload for AP, AR, tax, and controllership teams.
5. Enable agentic workflows without allowing unsupervised high-risk actions.
6. Make ERP integration fast enough for operational use and robust enough for enterprise governance.

### Secondary Goals

1. Support policy simulation before rule changes go live.
2. Detect tax-data quality issues upstream before they hit filings.
3. Create a jurisdiction-expansion model that scales by adding compliance packs.
4. Offer a control-plane layer that can sit over multiple systems of record.

---

## Non-Goals

1. Replacing the customer's ERP or general ledger
2. Acting as legal or tax counsel
3. Fully autonomous filing/submission without configurable human approval
4. Supporting every country on day one
5. Solving payroll tax as part of the initial launch scope
6. Building a monolithic "all finance" suite

---

## Product Differentiation

PulseTax will beat the reference product on five axes:

### 1. Compliance operations, not just tax calculation

The system must own the full workflow from transaction intake to filing-ready evidence.

### 2. Explainability by default

Every determination must answer:

* what tax was applied
* why it was applied
* which rule/version was used
* what source data drove the result
* what uncertainty or override exists

### 3. PH/ASEAN-first localization

Instead of treating APAC as an afterthought, the product will launch with jurisdiction packs that encode local document rules, reporting expectations, and exception handling.

### 4. Evidence-native architecture

The core product artifact is not only the tax amount; it is the **decision + evidence bundle**.

### 5. Safe agentic execution

Agents may classify, reconcile, draft, triage, and prepare — but high-risk actions remain policy-gated and reviewable.

---

## Target Users

### Primary Users

* Tax Managers
* Controllers
* AP Managers
* AR / Billing Operations Leads
* ERP / Finance Systems Owners
* Internal Audit / Compliance Leads

### Secondary Users

* CFOs
* External accountants
* Implementation partners
* Marketplace / channel integrators

---

## User Personas

### Persona 1 — Tax Manager

Needs reliable tax determination, filing readiness, evidence, and change control across jurisdictions.

### Persona 2 — AP Operations Lead

Needs vendor invoice validation, use-tax support, discrepancy thresholds, and exception queues.

### Persona 3 — Controller

Needs reconciled outputs, approval history, audit trails, and confidence in what hits books and returns.

### Persona 4 — ERP Admin / Integrator

Needs stable connectors, clear contracts, replayability, observability, and low-friction rollout.

### Persona 5 — CFO

Needs risk reduction, faster closes, fewer penalties, and dashboard-level visibility.

---

## User Stories

### User Story 1 — Explainable tax determination

As a **Tax Manager**, I want every tax result to include an explanation and evidence trail so that I can defend it during review, audit, or dispute.

#### Acceptance Criteria

1. **WHEN** a transaction is evaluated, **THE SYSTEM SHALL** produce a tax result with jurisdiction, rule source, rate, taxable basis, exemptions, and confidence/explanation metadata.
2. **WHEN** a user opens a tax decision, **THE SYSTEM SHALL** show the source fields used and any missing or inferred values.
3. **WHEN** a rule changes, **THE SYSTEM SHALL** preserve the prior rule version for historical decisions.

---

### User Story 2 — AP discrepancy control

As an **AP Manager**, I want vendor invoices checked for tax undercharge, overcharge, and use-tax exposure so that my team can resolve issues before posting.

#### Acceptance Criteria

1. **WHEN** an AP invoice is ingested, **THE SYSTEM SHALL** compare supplier-charged tax to expected tax.
2. **WHEN** variance thresholds are exceeded, **THE SYSTEM SHALL** route the transaction into an exception queue.
3. **WHEN** the customer configures tolerance policies, **THE SYSTEM SHALL** apply them consistently across vendors and entities.

---

### User Story 3 — Local compliance pack execution

As a **Controller in the Philippines**, I want localized invoice and compliance workflows so that the product fits actual filing and audit operations.

#### Acceptance Criteria

1. **WHEN** a PH entity is enabled, **THE SYSTEM SHALL** enforce the PH compliance pack rules configured for that entity.
2. **WHEN** a transaction lacks required local metadata or document structure, **THE SYSTEM SHALL** block completion or require exception approval.
3. **WHEN** a reporting period closes, **THE SYSTEM SHALL** assemble a filing-ready evidence package for review.

---

### User Story 4 — Human-governed agent workflow

As a **Finance Ops Lead**, I want AI agents to triage work and prepare outputs, without silently making high-risk irreversible decisions.

#### Acceptance Criteria

1. **WHEN** an agent identifies a routine low-risk task, **THE SYSTEM SHALL** execute it within configured policy bounds.
2. **WHEN** an agent encounters a threshold breach, ambiguity, or filing action, **THE SYSTEM SHALL** require human review.
3. **WHEN** an agent proposes an override, **THE SYSTEM SHALL** show rationale, impacted records, and rollback path.

---

### User Story 5 — ERP-native connectivity

As an **ERP Admin**, I want the product to connect to existing finance systems without forcing a system replacement.

#### Acceptance Criteria

1. **WHEN** an integration is enabled, **THE SYSTEM SHALL** ingest the minimum required transaction payload and validate contract completeness.
2. **WHEN** source data is incomplete, **THE SYSTEM SHALL** return actionable validation errors.
3. **WHEN** the ERP retries or replays a transaction, **THE SYSTEM SHALL** behave idempotently.

---

## Functional Requirements

### Core Determination

**FR-001** The system shall calculate tax for sales, purchases, AP use-tax, VAT/GST-style scenarios, and configurable jurisdiction packs.

**FR-002** The system shall support both real-time evaluation and batch processing.

**FR-003** The system shall allow product/service/category-based tax treatment.

**FR-004** The system shall support address and jurisdiction resolution with explicit provenance and fallback handling.

---

### Explainability and Evidence

**FR-005** The system shall store an immutable tax decision record for every evaluated transaction.

**FR-006** The system shall attach explanation metadata to each decision, including rule source, version, inputs, inferred fields, overrides, and reviewer actions.

**FR-007** The system shall generate an evidence bundle containing transaction context, document artifacts, decision rationale, and approval history.

**FR-008** The system shall allow side-by-side comparison between original source tax, expected tax, and approved override.

---

### Localization

**FR-009** The system shall support jurisdiction-specific compliance packs as first-class product units.

**FR-010** The system shall support a Philippines pack in launch scope.

**FR-011** The Philippines pack shall include structured invoice validation, withholding-aware controls, filing-workpaper generation, and e-invoicing/evidence readiness aligned to configured entity obligations.

**FR-012** The system shall allow different legal entities to run different compliance packs and effective dates.

---

### Agentic Operations

**FR-013** The system shall provide agent workflows for transaction triage, document classification, anomaly detection, reconciliation preparation, and filing draft generation.

**FR-014** The system shall classify actions into low-, medium-, and high-risk categories.

**FR-015** The system shall require configurable human approval for high-risk actions, including overrides, submissions, and rule publication.

**FR-016** The system shall log every agent action with prompt/context lineage sufficient for internal review.

---

### AP / AR / Filing Workflow

**FR-017** The system shall support AP discrepancy handling for undercharged and overcharged tax.

**FR-018** The system shall support AR transaction validation before posting or invoice issuance.

**FR-019** The system shall assemble period-close workpapers and exception summaries by entity and jurisdiction.

**FR-020** The system shall support reconciliation between transaction-level decisions and filing-period totals.

---

### Integrations

**FR-021** The system shall expose a stable integration contract for ERP, commerce, billing, and procurement systems.

**FR-022** The system shall support prebuilt connectors for Odoo, Microsoft Dynamics, SAP, NetSuite, Shopify, and WooCommerce in the target roadmap.

**FR-023** The system shall support file-based and API-based ingestion modes.

**FR-024** The system shall support outbound posting of tax decisions, exceptions, and evidence references back into source systems where supported.

---

### Governance and Change Control

**FR-025** The system shall support draft, test, approve, publish, and rollback states for tax rules and compliance-pack changes.

**FR-026** The system shall allow customers to simulate the impact of a rule change against historical transactions before publishing it.

**FR-027** The system shall preserve full audit history for rule changes, overrides, and approvals.

---

### Observability

**FR-028** The system shall provide dashboards for transaction throughput, exception rate, unresolved variance, filing readiness, and agent action outcomes.

**FR-029** The system shall surface data-quality issues separately from tax-rule issues.

**FR-030** The system shall support traceability from filing total to transaction to source document.

---

## Key Workflows

### Workflow A — Sales transaction determination

1. Source system sends transaction
2. System validates payload completeness
3. System determines tax
4. System emits decision + explanation + evidence reference
5. Exceptions route for review if confidence/policy thresholds fail

### Workflow B — AP invoice discrepancy handling

1. Invoice arrives from ERP/AP automation
2. System extracts source tax and expected tax
3. Variance and use-tax logic runs
4. Exception queue created if needed
5. Reviewer approves, corrects, or escalates
6. Posting artifact returned to source system

### Workflow C — Period-close compliance pack

1. System aggregates period transactions
2. Reconciliation checks run
3. Missing evidence / unresolved exceptions flagged
4. Filing-ready workpapers and review pack generated
5. Authorized user approves submission artifacts

### Workflow D — Agent-assisted regulatory update

1. Product team ingests new rule/change
2. Agent prepares candidate updates and impacted transaction set
3. Reviewer validates simulation output
4. Rule pack published with versioning
5. Monitoring watches for post-release anomalies

---

## Edge Cases

1. Transactions with incomplete or conflicting address data
2. Mixed taxable and exempt line items on one document
3. Supplier invoices with nonstandard or malformed tax fields
4. Multi-entity shared-service processing with entity-specific rules
5. Cross-border transactions where source system classification is wrong
6. Retroactive rule changes affecting already-posted periods
7. Document data present but not valid for local compliance evidence
8. High-volume retries from ERP connectors
9. Agent-proposed overrides that conflict with locked close periods
10. Jurisdiction pack version drift across subsidiaries

---

## Success Metrics

### Product Outcomes

* 80%+ of routine determinations completed without manual intervention
* 50%+ reduction in tax exception handling time
* 60%+ reduction in filing-pack preparation time
* <2% unresolved exception rate at period close for mature deployments
* 90%+ of tax decisions opened in review include sufficient explanation without escalation

### Business Outcomes

* Faster land-and-expand motion through jurisdiction packs
* Stronger win rate in PH/ASEAN midmarket and upper-midmarket deals
* Better retention through control-plane stickiness, not just API usage
* Higher ACV from compliance-pack subscriptions and managed updates

### Trust Outcomes

* 100% audit trail coverage for overrides and approvals
* 100% version traceability for published rules
* Zero silent autonomous high-risk actions

---

## Launch Scope

### Phase 1

* Core determination engine
* Explainability layer
* Evidence bundle
* AP discrepancy management
* PH compliance pack v1
* Odoo + API ingestion
* Human approval framework
* Filing workpaper generation

### Phase 2

* Dynamics + SAP connectors
* Additional ASEAN packs
* Rule simulation sandbox
* Period-close dashboards
* Agent-assisted reconciliation

### Phase 3

* Broader APAC and global packs
* Cross-border and customs extensions
* Marketplace/channel distribution
* Managed compliance update service

---

## Constraints

1. The product must never present itself as tax/legal advice.
2. The product must not allow fully autonomous high-risk submission flows by default.
3. Localization must be pack-based, versioned, and entity-aware.
4. Explanation and evidence are mandatory system outputs, not optional add-ons.
5. Source-system data quality cannot be assumed.

---

## Risks

1. Localization depth may expand scope quickly.
2. Customers may expect "global coverage" before operational maturity exists in local packs.
3. Agentic features can erode trust if explanation quality is weak.
4. Filing workflows can become brittle if source-document normalization is poor.
5. Jurisdiction updates require disciplined content operations.

---

## Open Questions

1. Should PH launch scope include only indirect tax + withholding controls, or broader filing orchestration?
2. Is the first commercial wedge Odoo-first, Microsoft-first, or API-first?
3. Should jurisdiction packs be sold per country, per entity, or by volume tier?
4. How much of filing submission should be native versus partner-assisted in v1?
5. Which next market after PH creates the best expansion path: SG, MY, TH, or AU?

---

## One-Sentence Positioning

**PulseTax is the agentic, explainable, evidence-native tax control plane for ERP-connected businesses that need local compliance operations, not just tax calculation.**

---

## References

* [AvaTax: Agentic Tax and Compliance — Microsoft Marketplace](https://marketplace.microsoft.com/marketplace/apps/avalara.avatax-agentic-tax-and-compliance?tab=Overview)
* [BIR Electronic Invoice System](https://eis.bir.gov.ph/)
* [Spec Kit — GitHub](https://github.com/github/spec-kit)

---

## Existing IPAI Modules (Foundation)

| Module | Role in PulseTax |
|--------|-----------------|
| `ipai_tax_intelligence` | Core determination engine kernel (55 tests, proven) |
| `ipai_bir_tax_compliance` | PH compliance pack prototype |
| `ipai_bir_notifications` | PH filing notification framework |
| `ipai_copilot_actions` | Agent action queue + human approval framework |
| `ipai_document_intelligence` | Document extraction for AP invoice intake |
| `ipai_expense_ops` | AP discrepancy control pattern |
| `ipai_branch_profile` | Multi-entity / branch-aware tax operations |
