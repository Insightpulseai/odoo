# AGCC Constitution

> Non-negotiable rules and constraints for the Agentic Global Compliance Cloud.
> This document is normative. All AGCC modules, agents, integrations, CI gates,
> and operational workflows must comply with every rule stated here.
> Violations require an audit record and remediation task. No exceptions.

---

## 1. Architectural Principles

Ordered by priority. When two principles conflict, the lower-numbered principle wins.

| # | Principle | Rationale |
|---|-----------|-----------|
| P1 | **Deterministic rules first, AI second, human authority always.** Tax determination and validation use codified rules from versioned policy data. AI assists with anomaly explanation and advisory. Humans retain final authority on all regulated decisions. | Prevents hallucinated legal conclusions. LLMs cannot be the source of truth for tax rates or legal positions. |
| P2 | **Policy graph is the single source of truth for jurisdiction rules.** Every tax rate, ATC code, threshold, filing deadline, and document schema is declared in versioned, schema-validated policy data. No compliance rule exists only in code. | Enables audit, versioning, effective-date management, and machine verification of rule provenance. |
| P3 | **ERP-native execution.** Compliance actions execute through Odoo accounting primitives: `account.move`, `account.move.line`, `account.tax`, `account.tax.group`, `account.fiscal.position`, `account.fiscal.position.rule`, `res.partner`. The compliance layer operates ON these models, never replaces them. | Preserves ERP as system of record. Prevents shadow ledgers. Keeps remediation in the workflow where users already work. |
| P4 | **Evidence is a first-class artifact.** Every compliance decision, tax computation, approval, override, filing action, and exception resolution produces a traceable evidence record. Evidence packs are generated, not reconstructed. | Audit-grade traceability. BIR, SEC, and international regulators require reconstructable decision trails. |
| P5 | **Filing submission always requires human approval.** No agent, cron, or automated workflow may submit a tax return, remittance, or regulatory filing without explicit human sign-off from an authorized signatory. | Filing errors carry legal penalties. Automated submission without human gate violates R6 (over-automation) control. |
| P6 | **Agent actions must be explainable and auditable.** Every agent-driven compliance action records: (a) what rule set was used, (b) what data inputs were evaluated, (c) what decision path was taken, (d) what human approvals were required or obtained. | Regulators and auditors must be able to reconstruct any compliance decision from its evidence trail. |
| P7 | **External content engines for content, internal control for governance.** External providers (Avalara AvaTax) supply multi-jurisdiction tax content (rates, rules, nexus). AGCC retains all control logic: approval gates, evidence generation, audit logging, exception routing, and filing orchestration. | Separates "content truth" from "execution truth" per PRD section 7.7. Prevents vendor lock-in on governance. |
| P8 | **Segregation of duties preserved.** The user who prepares a compliance artifact (return, 2307, remittance) must not be the user who approves it. Agent-prepared work follows the same SoD rules as human-prepared work. | Prevents fraud and self-validation. Required by BIR CAS permit conditions and standard internal control frameworks. |
| P9 | **Fail closed on missing policy.** If a transaction references a jurisdiction, tax type, ATC code, or document schema not present in the policy graph, the transaction is blocked -- not defaulted, not approximated, not skipped. Missing policy is an error, not a fallback condition. | Safe default. A wrong tax determination is worse than a blocked transaction. |
| P10 | **Jurisdiction packs are composable and isolated.** Each jurisdiction's rules, rates, forms, and filing calendars are encapsulated in a self-contained pack. Adding a jurisdiction must not modify existing packs. Removing a jurisdiction must not break others. | Enables incremental geographic expansion without regression. Prevents cross-jurisdiction coupling. |
| P11 | **Immutable audit log.** Compliance event logs are append-only. Corrections create new records referencing the original. No log entry is ever modified or deleted. | Audit trail integrity. Required for CAS permit and defensible compliance posture. |
| P12 | **Odoo CE only.** No Enterprise modules. No odoo.com IAP. No features gated behind Enterprise licensing. All compliance capabilities must run on Community Edition. | Platform constraint from operating contract. Prevents license dependency for regulated functions. |

---

## 2. Canonical Terminology

Every first-class object in AGCC. Terms used inconsistently across the platform must resolve to these definitions.

| Term | Definition | Canonical Location |
|------|------------|--------------------|
| **Compliance Graph** | The structured, versioned knowledge base linking entities, jurisdictions, tax registrations, obligation types, filing calendars, policy rules, and evidence artifacts. The graph is the queryable representation of all compliance state. | `ssot/agcc/compliance_graph.yaml` (schema), runtime in PostgreSQL |
| **Jurisdiction Pack** | A self-contained bundle of policy rules, tax rates, document schemas, filing calendars, and form templates for a single jurisdiction. Identified by ISO 3166-1 country code + optional subdivision. | `addons/ipai/ipai_agcc_jurisdiction_<cc>/` |
| **Policy Rule** | A single, versioned, schema-validated compliance rule with: jurisdiction scope, obligation type, effective date range, rule logic (deterministic), and evidence requirements. Policy rules are data, not code. | Jurisdiction pack `data/rules/*.json` |
| **Evidence Pack** | A collection of artifacts proving a compliance action was correctly performed: source transaction references, applied policy rules (with versions), computation inputs/outputs, approval records, timestamps, and actor identities. | `ir.attachment` (Odoo) + Azure Blob (immutable archive) |
| **Filing Calendar** | Per-entity, per-jurisdiction schedule of filing obligations with form type, frequency, due date computation, and notification lead time. | `agcc.filing.calendar` model |
| **Delegation Tier** | The level of autonomous authority granted to an agent or automated process for a specific compliance action class. Four tiers, strictly ordered. | Policy rule `delegation_tier` field |
| **-- Advisory** | Agent produces analysis and recommendations. Human decides and acts. No write to ERP records. | Delegation tier 1 |
| **-- Draft** | Agent creates draft artifacts (returns, forms, evidence packs). Human reviews, modifies, and promotes to final. | Delegation tier 2 |
| **-- Execute-with-Approval** | Agent executes the action (posts entries, generates forms) but requires explicit human approval before the action takes external effect (filing, remittance, submission). | Delegation tier 3 |
| **-- Execute-with-Post-Review** | Agent executes the action autonomously. Human reviews after the fact within a defined SLA. Restricted to low-risk, high-volume, deterministic actions only. | Delegation tier 4 |
| **Compliance Agent** | A named, scoped AI agent operating within AGCC. Bound by delegation tiers, policy rules, and audit requirements. Not a general-purpose assistant. Operates through MCP tool bindings. | `agents/foundry/agents/agcc-*.manifest.yaml` |
| **Tax Engine Adapter** | An integration connector to an external tax content provider (Avalara AvaTax, future providers). Supplies rates and rules. Never controls approval, evidence, or filing logic. | `addons/ipai/ipai_agcc_tax_engine_<provider>/` |
| **Document Validator** | A component that verifies document completeness and schema conformance: required fields present, TIN format valid, amounts reconcile, ATC codes assigned. Deterministic, no AI. | `ipai_agcc_core` validation layer |
| **Exception** | A compliance condition that cannot be resolved automatically: missing data, policy conflict, threshold crossing, classification ambiguity. Exceptions are typed, prioritized, and routed. | `agcc.exception` model |
| **Remediation Task** | An ERP-native task (`mail.activity`) assigned to a specific user to resolve an exception. Created in Odoo, not in a separate console. Tracks resolution, evidence, and elapsed time. | `mail.activity` on source `account.move` or `res.partner` |
| **Approval Gate** | A mandatory human review point enforced by `base_tier_validation` (OCA). Gates are binary: approved or rejected. Bypass creates an audit record and requires elevated authorization. | `tier.review` records |

---

## 3. Automation Boundaries

Every compliance action falls into exactly one of four automation tiers. Assignment is by action class, not by individual transaction. Tier assignment is declared in policy rules and enforced at runtime.

### 3.1 Fully Automated (Delegation Tier 4: Execute-with-Post-Review)

No human gate required before execution. Post-review within SLA.

| Action | Justification | Control |
|--------|---------------|---------|
| VAT computation (12% on VATable lines) | Deterministic math on codified rates | Unit-tested; rates from `ph_rates_2025.json` |
| EWT computation (1/2/5/10% by ATC code) | Deterministic lookup from canonical rate file | ATC-to-rate mapping is schema-validated |
| TIN format validation (regex) | Pattern match: `^\d{3}-\d{3}-\d{3}-\d{3}$` | Constraint on `res.partner.vat` |
| Fiscal position auto-apply | Country/partner-type rules in `account.fiscal.position.rule` | Deterministic rule evaluation |
| Document completeness check | Required field validation on `account.move` | `_check_*` constraints |
| Filing deadline reminder generation | Calendar math from BIR schedule | `ir.cron` + `mail.activity` |
| SLSP data aggregation | Read-only SQL aggregation of posted entries | No write; report over `account.move.line` |
| Audit trail event logging | Append-only event capture | `ir.logging` + `mail.tracking.value` |
| Invoice schema validation (field presence, format) | Deterministic field checks | Validation layer on `account.move` |

### 3.2 Human-in-the-Loop (Delegation Tier 3: Execute-with-Approval)

Agent prepares; authorized human approves before external effect.

| Action | Why Human Required | Workflow |
|--------|-------------------|----------|
| BIR form filing submission (2550M/Q, 1601-EQ) | Legal filing carries penalties for errors | Agent generates form draft; accountant reviews; authorized signatory approves |
| Tax remittance amount confirmation | Remitted amounts must match BIR records exactly | Agent computes; accountant verifies before remittance |
| BIR 2307 certificate issuance | Certificate is a legal document | Agent auto-generates; accountant reviews before release to vendor |
| Credit note with WHT reversal | Affects previously issued 2307 | Agent prepares replacement 2307; accountant confirms |
| Vendor/customer tax classification change | Affects all future transactions for that partner | Agent recommends; accounting manager approves via `base_tier_validation` |
| Fiscal position override | Exception to standard rules | Agent flags deviation; supervisor approves |
| VAT threshold crossing response | Requires BIR registration change | Agent detects threshold; compliance officer initiates registration |
| Monthly VAT return preparation | Aggregated amounts must reconcile to GL | Agent computes all boxes; accountant validates before submission |
| E-invoice transmission to BIR (when CAS/EIS live) | Regulatory submission | Agent formats; authorized user triggers transmission |

### 3.3 Advisory Only (Delegation Tier 1: Advisory)

Agent produces analysis. Human decides and acts independently.

| Action | Why Advisory Only | Agent Output |
|--------|------------------|--------------|
| Transfer pricing assessment | Requires specialist judgment, not rule application | Risk flag + recommendation to engage TP consultant |
| Tax treaty rate selection | Beneficial ownership determination is legal judgment | Suggested rate + treaty reference for tax counsel review |
| Legal interpretation of new BIR issuances | Legal analysis cannot be automated | Summary of issuance + potential impact areas for compliance officer |
| Cross-border structuring advice | Tax planning is legal counsel territory | Jurisdictional summary for advisor |
| SEC filing preparation guidance | Financial statement audit required | Deadline reminder + document checklist |
| OECD BEPS Pillar Two impact assessment | Evolving regulation, specialist domain | Exposure estimate + recommendation for specialist engagement |
| CAS permit application guidance | BIR administrative process | Checklist of requirements + status tracker |

### 3.4 Blocked Without Explicit Approval (Requires Elevated Authorization)

These actions are blocked by default. Execution requires approval from a specifically authorized role, with mandatory audit trail.

| Action | Required Approver | Enforcement Mechanism |
|--------|-------------------|----------------------|
| Override a computed tax amount | CFO or Tax Manager | `base_tier_validation` with mandatory comment + evidence attachment |
| Modify or reverse a posted journal entry | Controller | Odoo fiscal lock date + `res.groups` restriction |
| Submit filing to BIR (when e-filing implemented) | Authorized tax signatory | Digital signature + 2FA gate |
| Change canonical tax rates in `ph_rates_2025.json` | Compliance officer | Git PR review + CI schema validation + hash verification on module load |
| Change a partner's tax registration status | Compliance officer | `base_tier_validation` on `res.partner` write to tax fields |
| Grant or revoke compliance-role access | System administrator | Entra ID group assignment (not Odoo `res.groups` alone) |
| Override delegation tier for an action class | Platform owner | Policy change via PR; runtime override creates immutable audit record |
| Disable or modify a policy rule | Compliance officer | Versioned rule update; old version preserved; effective date gating |

---

## 4. Data Contracts

### 4.1 Canonical Data Sources

| Data | SSOT Location | Format | Owner |
|------|---------------|--------|-------|
| Philippine tax rates (VAT, EWT, Final WHT, percentage tax, income tax brackets) | `ipai_bir_tax_compliance/data/rates/ph_rates_2025.json` | JSON, schema-validated | Compliance officer (human) |
| ATC code registry | `ph_rates_2025.json` (embedded) | JSON array with code, rate, description, effective dates | Compliance officer (human) |
| Tax configuration in ERP | `account.tax` records | Odoo model | Module install/update from `ph_rates_2025.json` |
| Partner TIN | `res.partner.vat` | String, regex-validated `^\d{3}-\d{3}-\d{3}-\d{3}$` for PH | Data entry + validation constraint |
| Fiscal positions | `account.fiscal.position` + `account.fiscal.position.rule` | Odoo models | `l10n_ph` + `ipai_bir_tax_compliance` data files |
| Filing calendar (PH) | `ipai_bir_tax_compliance/data/filing_calendar_ph.json` | JSON, per-form-type schedule | Compliance officer (human) |
| Non-PH multi-jurisdiction tax content | Avalara AvaTax REST API (Phase 2) | API response | Avalara (external) |
| Document extraction (scanned invoices) | Azure Document Intelligence | API response | Azure (external) |
| Anomaly detection signals | Databricks DLT pipeline | Structured events | Analytics pipeline |

### 4.2 Data Quality Invariants

These invariants are enforced at all times. Failure is a blocking condition, not a warning.

| Invariant | Enforcement | Failure Mode |
|-----------|-------------|--------------|
| Every `account.tax` record for PH must match a rate in `ph_rates_2025.json` | CI validation + Odoo startup server action | Module install fails; discrepancy logged as critical exception |
| Every partner with PH transactions must have a valid TIN in `res.partner.vat` | `_check_vat` constraint on `res.partner` | Invoice posting blocked for partner without valid TIN |
| Every vendor bill with qualifying purchases must have EWT applied | Daily cron exception detection | Exception created; remediation task assigned |
| SLSP monthly totals must reconcile to GL tax account balances | Monthly automated reconciliation | Discrepancy logged as exception; filing preparation blocked |
| BIR 2307 record must exist for every vendor bill with WHT tax lines | Cron: flag bills with WHT lines but no 2307 record | Exception created with aging |
| `ph_rates_2025.json` must pass JSON schema validation | CI gate on every PR that touches the file | PR blocked |
| `ph_rates_2025.json` hash must match on module load | Module `post_init_hook` verifies SHA-256 | Module load fails on mismatch; logged as tampering alert |

### 4.3 Data Flow Constraints

| Rule | Detail |
|------|--------|
| Tax rates flow one direction: `ph_rates_2025.json` -> `account.tax`. Never reverse. | ERP tax records are derived from the canonical rate file, not the other way around. |
| External tax engine responses are cached but never treated as SSOT. | Avalara responses are evidence inputs. Canonical rates remain in jurisdiction packs. |
| Document Intelligence extraction outputs require human confirmation before ERP write. | OCR results populate draft `account.move`; human confirms before posting. |
| Databricks anomaly signals are advisory inputs, never automated write triggers. | Anomaly detection creates exceptions for human review, not automated corrections. |

---

## 5. Security and Audit Invariants

### 5.1 Audit Log Rules

| Rule | Enforcement |
|------|-------------|
| All compliance-relevant events are logged to `ir.logging` with structured context. | Custom logging decorator on compliance model write methods. |
| All field changes on compliance models are tracked via `mail.tracking.value`. | `track_visibility` on all tax, fiscal position, and partner tax fields. |
| Audit log entries are append-only. No update. No delete. No truncate. | Database-level trigger preventing UPDATE/DELETE on audit tables. PostgreSQL `pg_audit` extension recommended. |
| Every override of a computed value records: original value, new value, actor, timestamp, justification. | `base_tier_validation` review record + mandatory comment field. |
| Evidence packs archived to Azure Blob use immutable retention policy (10-year minimum for BIR). | Azure Blob immutability policy; deletion blocked until retention expiry. |
| Log retention: operational logs 90 days in PostgreSQL, permanent in Azure Blob archive. | Archival cron moves logs older than 90 days to cold storage. |

### 5.2 Segregation of Duties

| Action | Preparer Role | Approver Role | Same User Allowed |
|--------|---------------|---------------|-------------------|
| BIR return preparation | Compliance analyst | Tax manager or CFO | No |
| BIR 2307 generation | Accounts payable | Accounting manager | No |
| Tax remittance | Accounts payable | Controller or CFO | No |
| Tax rate update (`ph_rates_2025.json`) | Compliance analyst | Compliance officer (PR review) | No |
| Fiscal position override | Accountant | Supervisor | No |
| Exception resolution (high-risk) | Assigned resolver | Compliance officer | No |
| System role assignment | System administrator | Platform owner | No |

Enforcement: OCA `base_tier_validation` for Odoo workflow gates. Entra ID group membership for system-level access. `base_user_role` (OCA) for Odoo role mapping.

### 5.3 Agent Security

| Rule | Detail |
|------|--------|
| Compliance agents authenticate via service identity, not user credentials. | Azure Managed Identity -> MCP tool binding. No shared secrets. |
| Agent write scope is explicitly declared in manifest. No implicit write access. | Agent contract `write_scope` field lists permitted models. |
| Agents cannot grant themselves elevated permissions. | Permission changes require human actor in Entra ID. |
| Agent actions carry the agent's identity in audit records, not a generic system user. | `ir.logging` records include `agent_id` field. |
| Agents cannot access secrets directly. Tool bindings resolve secrets via Azure Key Vault at runtime. | Agents see opaque tool interfaces; Key Vault resolves credentials. |
| Agent rate limits are enforced. | Maximum task executions per agent per hour, declared in policy. |

---

## 6. Integration Constraints

### 6.1 Platform Constraints

| Constraint | Detail |
|------------|--------|
| **Odoo CE only.** | No Enterprise modules. No odoo.com IAP. No Enterprise-gated features. |
| **Azure-native runtime.** | Azure Container Apps for Odoo. Azure AI Foundry for agent runtime. Azure Blob for evidence archive. Azure Key Vault for secrets. PostgreSQL 16 (Azure-managed or local). |
| **MCP for agent tools.** | All reusable agent tool interfaces exposed via Model Context Protocol. No direct function calls between agents and Odoo. |
| **OCA first for workflow.** | `base_tier_validation` for approval gates. `base_user_role` for role mapping. `account_fiscal_position_autodetect` for jurisdiction detection. Custom `ipai_*` only when no OCA module exists. |
| **No Supabase.** | Deprecated. All persistence in PostgreSQL (Odoo) or Azure-native services. |
| **No Vercel.** | Deprecated. Azure Container Apps only. |

### 6.2 External Integration Rules

| Integration | Purpose | Boundary |
|-------------|---------|----------|
| **Avalara AvaTax** (Phase 2) | Multi-jurisdiction tax content (rates, rules, nexus) for non-PH jurisdictions | Content only. AGCC retains all governance, approval, evidence, and filing logic. Avalara responses are inputs, not decisions. |
| **Azure Document Intelligence** | OCR extraction from scanned vendor invoices | Extraction only. Results populate draft records. Human confirms before posting. |
| **Databricks** | Anomaly detection, WHT leakage analysis, threshold monitoring | Analytics only. Signals create advisory exceptions. No automated write-back to ERP. |
| **Azure Blob Storage** | Immutable archive for evidence packs, BIR forms, SLSP exports | Storage only. 10-year immutable retention for BIR. |
| **BIR eFPS / eREG** (future) | Electronic filing and registration | Submission only with human approval gate. Agent formats; authorized signatory triggers. |
| **Peppol / e-invoicing networks** (future) | E-invoice transmission | Transmission only with pre-submission validation and human approval for initial activation. |

### 6.3 Module Naming

All AGCC modules follow the `ipai_agcc_*` naming convention:

| Module | Purpose | Status |
|--------|---------|--------|
| `ipai_agcc_core` | Compliance graph, exception model, evidence pack, filing calendar, delegation tier enforcement | Planned |
| `ipai_agcc_jurisdiction_ph` | Philippine jurisdiction pack (rates, ATC codes, BIR forms, SLSP, filing calendar) | Planned (absorbs `ipai_bir_tax_compliance` scope) |
| `ipai_agcc_tax_engine_avalara` | Avalara AvaTax adapter for non-PH jurisdictions | Phase 2 |
| `ipai_agcc_einvoice` | E-invoicing adapter architecture (Peppol, BIR CAS/EIS) | Phase 2 |
| `ipai_agcc_analytics` | Databricks integration for anomaly detection and compliance analytics | Phase 2 |
| `ipai_agcc_doc_intel` | Azure Document Intelligence adapter for invoice OCR | Phase 2 |

---

## 7. Invariant Enforcement

### 7.1 CI Gates

The following CI checks run on every PR that touches `addons/ipai/ipai_agcc_*` or `spec/agentic-global-compliance-cloud/`:

| Check | Gate Type | Fails On |
|-------|-----------|----------|
| `agcc-rate-schema-validate` | Hard | `ph_rates_2025.json` fails JSON schema validation |
| `agcc-rate-hash-verify` | Hard | Rate file hash does not match declared hash in module manifest |
| `agcc-delegation-tier-audit` | Hard | Any compliance action missing explicit delegation tier assignment |
| `agcc-policy-rule-schema` | Hard | Policy rule JSON fails schema validation or missing required fields |
| `agcc-sod-check` | Hard | Approval workflow missing preparer/approver role separation |
| `agcc-module-naming` | Hard | Module not matching `ipai_agcc_*` convention |
| `agcc-evidence-completeness` | Soft | Evidence pack missing required artifact references |
| `agcc-filing-calendar-validate` | Soft | Filing calendar entries missing due date computation or notification lead time |

### 7.2 Runtime Invariants

| Invariant | Enforcement Point | Failure Behavior |
|-----------|-------------------|------------------|
| Missing policy rule for jurisdiction + obligation type | Transaction validation | Block transaction; create exception |
| Delegation tier exceeded by agent | MCP tool binding layer | Reject action; log violation |
| Approval gate bypassed | `base_tier_validation` | Block progression; escalate to compliance officer |
| Rate file version stale (past `effective_to` date) | Module startup + daily cron | Warning on startup; exception created; filing preparation blocked after grace period |
| SoD violation (same user as preparer and approver) | `base_tier_validation` review | Reject approval; require different user |
| Audit log write failure | Compliance event decorator | Block the triggering action; fail closed |

---

## Compatibility

### Relationship to Existing Artifacts

| Existing Artifact | Relationship to This Constitution |
|-------------------|-----------------------------------|
| `spec/agentic-global-compliance-cloud/prd.md` | This constitution enforces the PRD's design principles and non-functional requirements. The PRD defines what; this constitution defines the invariant rules for how. |
| `spec/agent-factory/constitution.md` | Agent Factory constitution governs agent lifecycle (passports, promotions, evaluation). This constitution governs compliance-domain behavior. AGCC agents must comply with both. |
| `docs/knowledge-base/skill-packs/tax-compliance-ph/SKILL.md` | PH tax skill pack provides implementation reference. This constitution provides the governance rules the implementation must satisfy. |
| `docs/knowledge-base/research/ai-compliance-agent-design.md` | Research report provides architectural rationale and risk analysis. This constitution codifies the decisions into enforceable rules. |
| `ipai_bir_tax_compliance` module | Existing module provides `ph_rates_2025.json` and basic tax rate data. AGCC jurisdiction pack (`ipai_agcc_jurisdiction_ph`) will absorb and extend this scope. |
| `l10n_ph` (Odoo core) | Philippine localization baseline. AGCC builds on top; never modifies core. |

---

*Schema version: 1.0*
*Effective date: 2026-04-07*
*Owner: @Insightpulseai-net/platform*
*Review cadence: Quarterly or on any structural change to AGCC, jurisdiction pack additions, or delegation tier modifications*
