# Tasks: Pulser for Odoo

> **Canonical Slug**: `pulser-odoo`
> **Human-facing title**: `Pulser for Odoo`
> **SC-PH traceability**: Each task group maps to one or more SC-PH-* success criteria from `prd.md` Section 15.

---

## Phase 1: Consolidation & Renaming
- [x] Merge PRD, Constitution, and Plan from legacy folders.
- [ ] Merge Task lists (Wave/Phase mapping).
- [ ] Rename legacy spec folders after verification.
- [ ] Update SSOT keys in `release_contract.yaml`.

## Phase 2: Bridge Implementation — SC-PH-01, SC-PH-02, SC-PH-03
- [ ] P2-1: Implement finance Q&A context packager (account, partner, bank). **SC-PH-01**
- [ ] P2-2: Build reconciliation assistance flow with native Odoo API. **SC-PH-02**
- [ ] P2-3: Build collections assistance drafting in Odoo Mail. **SC-PH-02**
- [ ] P2-4: Implement approval-gated action mediation in `tool_executor.py`. **SC-PH-13**
- [ ] P2-5: Achieve 100% audit coverage for all bridge interactions. **SC-PH-13**

## Phase 3: Documentation & Foundry Patch
- [ ] D-1: Update `docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md` -> `MVP_SHIP_CHECKLIST.md`.
- [ ] D-2: Patch Foundry agent descriptions with Odoo CE 18.0 assistant wording.
- [ ] D-3: Update examples in `FOUNDRY_TOOL_POLICY.md` and `MCP_POLICY.md`.

## Phase 4: Runtime Unblocking (Dockerfile)
- [ ] R-1: Patch `Dockerfile.odoo-copilot` with missing OCA project/timesheet modules.
- [ ] R-2: Patch `Dockerfile.odoo-copilot` with IPAI Copilot and Knowledge Bridge modules.
- [ ] R-3: Remove `ipai_finance_ppm` from production build.
- [ ] R-4: Verify `addons_path` consistency for the consolidated build.

## Phase 5: REST/FastAPI Replacement
- [ ] F-1: Inventory current REST/FastAPI endpoints touching finance, tax, approvals, expenses, or document state.
- [ ] F-2: Classify endpoints into thin-edge vs duplicated-business-logic.
- [ ] F-3: Create Odoo-native service/action contracts for endpoints in scope.
- [ ] F-4: Migrate tax/accounting/approval logic into Odoo addons where duplicated.
- [ ] F-5: Replace Azure wrapper calls with official Azure SDK/REST/Foundry SDK usage.
- [ ] F-6: Add parity tests for each migrated endpoint.
- [ ] F-7: Remove or deprecate superseded FastAPI business endpoints.
- [ ] F-8: Update `ssot/agent-platform/odoo_edge_inventory.yaml` with final state.

## Phase 6: Workflow Implementation — SC-PH-02, SC-PH-03, SC-PH-06, SC-PH-07, SC-PH-12

- [ ] W-1: Implement `pulser-doc-intake-v1` workflow in Foundry. **SC-PH-03, SC-PH-06**
  - [ ] W-1a: Wire classify step to Content Understanding + DI API.
  - [ ] W-1b: Wire extract step to Document Intelligence prebuilt models.
  - [ ] W-1c: Wire validate step to Odoo master data lookup.
  - [ ] W-1d: Wire safe_action to Odoo ORM draft creation with idempotency key.
  - [ ] W-1e: Wire evidence persistence to Blob Storage.
- [ ] W-2: Implement `pulser-form-validator-v1` workflow in Foundry. **SC-PH-01, SC-PH-07**
  - [ ] W-2a: Wire intent normalization to active form context packager.
  - [ ] W-2b: Wire validation checks per model specialization (hr.expense, account.move, sale.order, project.project).
  - [ ] W-2c: Wire structured output to Pulser UI card renderer.
- [ ] W-3: Implement `pulser-payment-reconcile-v1` workflow in Foundry. **SC-PH-02**
  - [ ] W-3a: Wire payment classification to uploaded proof / bank statement line.
  - [ ] W-3b: Wire open item lookup to Odoo `account.move.line` search.
  - [ ] W-3c: Wire reconciliation candidate validation.
- [ ] W-4: Implement `pulser-close-orchestrator-v1` workflow in Foundry. **SC-PH-12**
  - [ ] W-4a: Wire template instantiation to SSOT task catalog.
  - [ ] W-4b: Wire dependency-based task release.
  - [ ] W-4c: Wire compliance scenario execution.
  - [ ] W-4d: Wire human-in-the-loop review gate.
  - [ ] W-4e: Wire evidence pack generation.

## Phase 7: Prompt & Grounding Contract — SC-PH-01, SC-PH-04, SC-PH-05, SC-PH-19

- [ ] G-1: Define model input schemas for each active Odoo screen. **SC-PH-01**
- [ ] G-2: Define supporting context fields per workflow. **SC-PH-05**
- [ ] G-3: Define output schemas per workflow (done: 4 schemas in `agents/schemas/workflow/pulser/`). **SC-PH-04**
- [ ] G-4: Configure fallback states (`not_found`, `not_yet_computable`, `needs_review`, `blocked`). **SC-PH-04**
- [ ] G-5: Configure low-variance inference settings for finance-critical tasks. **SC-PH-04**
- [ ] G-6: Create Foundry IQ / AI Search index for finance policy grounding. **SC-PH-18, SC-PH-19**

## Phase 8: Document Pipeline — SC-PH-03, SC-PH-06

- [ ] DP-1: Provision Azure Blob Storage container for raw document intake.
- [ ] DP-2: Define extraction result storage schema (Blob JSON or PG table).
- [ ] DP-3: Build invoice/bill/receipt/payment-proof classifiers using DI prebuilt models.
- [ ] DP-4: Create classification eval dataset (min 50 samples per class). **SC-PH-06**
- [ ] DP-5: Wire Content Understanding Read/Layout as first-pass OCR before DI.
- [ ] DP-6: Build PH-specific extraction schema (BIR fields, TIN, ATC, withholding). **SC-PH-10**

## Phase 9: Governance & Hardening — SC-PH-13 through SC-PH-17, SC-PH-22

- [ ] GH-1: Configure >= 4 custom Pulser compliance policies in Foundry. **SC-PH-14**
- [ ] GH-2: Run release-gate evals for all 5 core agents. **SC-PH-15**
- [ ] GH-3: Complete >= 1 red-team run against Pulser core agent surfaces. **SC-PH-17**
- [ ] GH-4: Curate >= 25 stored completions covering success + failure finance paths. **SC-PH-16**
- [ ] GH-5: Set up actionable monitoring alerts for all core agents. **SC-PH-22**
- [ ] GH-6: Implement runtime duplicate detection in transaction agent. **SC-PH-13**
- [ ] GH-7: Implement company-context validation gate. **SC-PH-05**

## Phase 10: Integration — SC-PH-21

- [ ] INT-1: Connect PostgreSQL MCP read-only for grounding. **SC-PH-21**
- [ ] INT-2: Implement document upload handoff (Azure Function -> Blob -> DI -> Foundry).
- [ ] INT-3: Implement structured result callback (Foundry -> Odoo draft creation).
- [ ] INT-4: Decide APIM vs direct REST integration pattern.

## Phase 11: PH Compliance & BIR — SC-PH-08 through SC-PH-11, SC-PH-23, SC-PH-24

- [ ] BIR-1: Implement VAT output/input consistency scenario. **SC-PH-10**
- [ ] BIR-2: Implement withholding integrity scenario. **SC-PH-10**
- [ ] BIR-3: Implement ATC/TIN completeness scenario. **SC-PH-10**
- [ ] BIR-4: Implement BIR filing readiness view (2307, SLSP, 2550Q, SAWT/QAP). **SC-PH-11**
- [ ] BIR-5: Implement cash advance monitoring and owner assignment. **SC-PH-08**
- [ ] BIR-6: Implement cash advance liquidation tracking and escalation. **SC-PH-09**
- [ ] BIR-7: Implement explicit BIR status enum (`ready_for_filing`, `submitted_externally_pending_confirmation`, `officially_confirmed`). **SC-PH-24**
- [ ] BIR-8: Verify no Pulser flow labels anything as "officially filed" without external confirmation. **SC-PH-23**

## Phase 12: Exit Gate — Production Readiness

- [ ] EXIT-1: Verify SC-PH-13 (zero silent-post incidents).
- [ ] EXIT-2: Verify SC-PH-14 (>= 4 custom policies active).
- [ ] EXIT-3: Verify SC-PH-15 (all core agents have passing eval runs).
- [ ] EXIT-4: Verify SC-PH-17 (>= 1 red-team run completed).
- [ ] EXIT-5: Verify SC-PH-18 (>= 1 knowledge index active).
- [ ] EXIT-6: Verify SC-PH-21 (PostgreSQL MCP connected read-only).
- [ ] EXIT-7: Verify SC-PH-06, SC-PH-07, SC-PH-10, SC-PH-12 (AP, expense, tax, close baselines).
- [ ] EXIT-8: Verify SC-PH-23 (no false BIR completion claims).

## Phase 13: Finance PPM OKR Dashboard (CE + OCA + Delta)

- [x] OKR-1: Create `ppm.okr.objective` model with computed score/status/RAG.
- [x] OKR-2: Create `ppm.okr.key_result` model with 0.0-1.0 scoring.
- [x] OKR-3: Create native kanban/list/form/graph views for objectives.
- [x] OKR-4: Create native list/form/graph views for key results.
- [x] OKR-5: Add ACLs for OKR models (user=read, manager=CRUD).
- [x] OKR-6: Add OKR menu items to Finance PPM menu.
- [x] OKR-7: Write decomposition architecture doc.
- [ ] OKR-8: Create canonical Finance PPM project for Pulser for PH.
- [ ] OKR-9: Define O1-O6 objectives and seed KR data.
- [ ] OKR-10: Define milestone structure (Foundation / Core / Cash Advance / PH Tax / Close / Governance).
- [ ] OKR-11: Define recurring task templates for month-end and tax-period cycles.
- [ ] OKR-12: Define dependency graph for close-critical tasks.
- [ ] OKR-13: Add scheduled review/approval activity templates.
- [ ] OKR-14: Verify `mis_builder` OCA module available in addons-path for KPI reports.
- [ ] OKR-15: Verify `project_timeline` OCA module available for Gantt view.
- [ ] OKR-16: Add evidence completeness KR widget (% of tasks with required Documents files).
- [ ] OKR-17: Remove deprecated `okr_dashboard.html` and `okr_dashboard_action.xml`.

## Phase 14: Finance PPM Document Copies in Odoo Documents

- [ ] DOC-1: Create canonical Finance PPM directory tree in Odoo Documents.
- [ ] DOC-2: Define file-tag schema for OKR, KR, period, company, branch, lane, owner, reviewer, approver.
- [ ] DOC-3: Implement automatic copy/save rules for source finance artifacts.
- [ ] DOC-4: Implement automatic save rules for extracted JSON and review packs.
- [ ] DOC-5: Implement automatic save rules for approval/signoff artifacts.
- [ ] DOC-6: Implement automatic save rules for BIR readiness and external confirmation artifacts.
- [ ] DOC-7: Link Finance PPM tasks, milestones, and dashboard widgets to retained Documents files.
- [ ] DOC-8: Add archive and retention rules for prior periods.
- [ ] DOC-9: Add verification checks so finance-critical workflows fail closed when evidence copies are missing.

## Phase 15: Pulser Grounding from Odoo Documents

- [ ] GRD-1: Define Odoo Documents retrieval contract for Pulser.
- [ ] GRD-2: Define metadata fields required for finance/compliance retrieval.
- [ ] GRD-3: Implement indexing of retained source and derivative artifacts.
- [ ] GRD-4: Link files to tasks, milestones, OKRs, accounting records, and BIR status objects.
- [ ] GRD-5: Implement evidence-aware question answering from linked Documents files.
- [ ] GRD-6: Implement file-reference output format for Pulser responses.
- [ ] GRD-7: Implement missing-evidence detection and response behavior.
- [ ] GRD-8: Add eval scenarios for document-grounded finance/compliance answers.
- [ ] GRD-9: Add guardrails so Pulser distinguishes evidence, inference, and missing support.
- [ ] GRD-10: Add Document Grounding Coverage KR (% of finance-critical answers backed by Documents).

## Phase 16: Professional Office Skills — Studio Definitions (Workstream A)

- [ ] OFS-1: Define PowerPoint Studio skill contract (prompts, schema, grounding sources, publish target).
- [ ] OFS-2: Define Word Studio skill contract (prompts, schema, grounding sources, publish target).
- [ ] OFS-3: Define Excel Studio skill contract (prompts, schema, grounding sources, publish target).
- [ ] OFS-4: Register all three studios in `ssot/agent-platform/skills_manifest.yaml`.
- [ ] OFS-5: Register `office-skills` solution in `ssot/agents/solution_registry.yaml`.

## Phase 17: Professional Office Skills — Native Artifact Generation (Workstream B)

- [ ] OFS-6: Add `python-docx` to Pulser runtime dependencies for DOCX generation.
- [ ] OFS-7: Add `python-pptx` to Pulser runtime dependencies for PPTX generation.
- [ ] OFS-8: Add `openpyxl` to Pulser runtime dependencies for XLSX generation.
- [ ] OFS-9: Implement Odoo-aware data contract for PowerPoint Studio (PPM OKRs, metrics, retained visuals).
- [ ] OFS-10: Implement Odoo-aware data contract for Word Studio (Documents, policies, approvals).
- [ ] OFS-11: Implement Odoo-aware data contract for Excel Studio (record metrics, OKRs, derived formulas).
- [ ] OFS-12: Implement native PPTX generator (structured slides, brand-safe styling, no HTML export).
- [ ] OFS-13: Implement native DOCX generator (formal structure, citations, consistent formatting).
- [ ] OFS-14: Implement native XLSX generator (formula-safe workbooks, KPI models, conditional formatting).

## Phase 18: Professional Office Skills — Render QA & Review Gates (Workstream C)

- [ ] OFS-15: Implement render QA checks for PPTX (no overflow, story flow, visual consistency).
- [ ] OFS-16: Implement render QA checks for DOCX (page hierarchy, citation integrity, signoff fields).
- [ ] OFS-17: Implement render QA checks for XLSX (formula integrity, recalc validation, cell overflow).
- [ ] OFS-18: Implement review workflow: draft → reviewer notes → revision → approved → publish.

## Phase 19: Professional Office Skills — Documents Retention & Grounding (Workstream D)

- [ ] OFS-19: Store source and derivative publishable artifacts in Odoo Documents with trace links.
- [ ] OFS-20: Tag retained office artifacts with OKR/KR/milestone/period metadata.
- [ ] OFS-21: Implement Pulser retrieval from retained office artifacts in Documents.
- [ ] OFS-22: Implement evidence-aware answering from published decks, docs, and workbooks.

## Phase 20: Professional Office Skills — Finance PPM Linkage (Workstream E)

- [ ] OFS-23: Add publishable-quality KR to Finance PPM dashboard (% artifacts passing QA).
- [ ] OFS-24: Add document grounding coverage metric for office artifacts.
- [ ] OFS-25: Add evidence completeness widget for retained publishable artifacts.
- [ ] OFS-26: Link OFS business-case OKRs (O1–O5) to SC-PH success criteria.

## Phase 21: Professional Office Skills — Release Gate (R3 Hardening)

- [ ] OFS-27: Define custom policies for office artifact generation (content safety, brand compliance).
- [ ] OFS-28: Add eval scenarios for each studio (PowerPoint, Word, Excel).
- [ ] OFS-29: Complete at least one red-team run on office artifact generation.
- [ ] OFS-30: Verify all publish-gate criteria met (content grounded, renders cleanly, reviewer approved, copies retained).

## Phase 22: Office Publishing Accelerator — Agent Choreography

- [ ] OFS-31: Create `pulser-office-publishing` capability family with 9 sub-skills.
- [ ] OFS-32: Implement Office Triage Agent (request interpretation, artifact classification, studio routing).
- [ ] OFS-33: Implement Office Planning Agent (narrative structure, section plan, data bindings).
- [ ] OFS-34: Implement Office Research / Grounding Agent (enterprise data retrieval, evidence classification).
- [ ] OFS-35: Implement Publishability QA Agent (format, structure, grounding, lane-specific checks).
- [ ] OFS-36: Implement Evidence / Documents Agent (retention, trace links, metadata tagging).
- [ ] OFS-37: Wire multi-agent orchestration: triage → planning → grounding → studio → QA → evidence.
- [ ] OFS-38: Implement publishability scoring (≥ 90% publish, 70–89% revise, < 70% rework).
- [ ] OFS-39: Implement QA-fail loop: failed artifacts re-route to studio agent with fix instructions.
- [ ] OFS-40: Add branded template pack (deck master, document styles, workbook themes).
- [ ] OFS-41: Add eval scenarios for full orchestration pipeline (end-to-end triage-to-publish).
- [ ] OFS-42: Add production boundary enforcement (POC → Pilot → Production stage gates).

---

## Phase 23: Identity and Access Model

- [ ] ID-1: Validate Odoo Entra login path for internal users. **SC-PH-04, SC-PH-B04**
- [ ] ID-2: Define and document separation between internal / portal / service / read-only / write-capable identities.
- [ ] ID-3: Define read-only grounding access model for MCP-backed data tools.
- [ ] ID-4: Define write-capable business action access model (approval-gated).
- [ ] ID-5: Create service/runtime identity inventory (Managed Identity per service).
- [ ] ID-6: Retain identity configuration evidence in `Finance PPM / 10 Identity` Documents folder.
- [ ] ID-7: Register identity model in `ssot/agent-platform/identity_model.yaml`.

## Phase 24: Foundry-Native Runtime Adoption

- [ ] FNR-1: Adopt `Get started with AI agents` template baseline for Pulser app shell.
- [ ] FNR-2: Adopt `Multi-modal Content Processing` patterns for invoice / receipt / document extraction flows.
- [ ] FNR-3: Adopt `Document Generation and Summarization` patterns for report and evidence-pack generation.
- [ ] FNR-4: Adopt `Deploy Your AI Application in Production` landing-zone patterns for production deployment.
- [ ] FNR-5: Enable Azure AI Search for finance knowledge indexing and agentic retrieval. **SC-PH-18, SC-PH-19**
- [ ] FNR-6: Enable File Search tool for Documents-grounded evidence retrieval. **SC-PH-B11**
- [ ] FNR-7: Enable Code Interpreter for formula validation and scenario computation.
- [ ] FNR-8: Enable Browser Automation for BIR portal and external confirmation workflows. **SC-PH-23, SC-PH-24**
- [ ] FNR-9: Configure Foundry MCP Server as canonical tool exposure surface. **SC-PH-21**
- [ ] FNR-10: Configure Azure DevOps MCP where board/progress sync is required.
- [ ] FNR-11: Configure Work IQ Word and Microsoft MCP Server for Enterprise for Office publishing lane.

## Phase 25: Capability-Family Alignment

- [ ] CF-1: Tag all existing epics, issues, and tasks with one or more canonical capability family slugs (families 1–10 from `constitution.md §9.3`).
- [ ] CF-2: Verify every capability family maps to at least one OKR objective (O1–O6+O7 for publishing).
- [ ] CF-3: Verify every capability family has at least one eval scenario defined.
- [ ] CF-4: Verify every capability family is covered by a release gate (A–D from `plan.md §20`).
- [ ] CF-5: Retire conflicting or duplicate naming from prior patches (e.g. legacy `ipai_odoo_copilot` vs `pulser-copilot-experience`).
- [ ] CF-6: Align solution kit components (§16) to capability family slugs.
- [ ] CF-7: Register capability family manifest in `ssot/agents/capability_families.yaml`.

## Phase 26: SMART Success Criteria Dashboard Binding

- [ ] SC-1: Bind SC-PH-B01 (upload-to-draft median) to Finance PPM dashboard KR widget with live data source.
- [ ] SC-2: Bind SC-PH-B02 (finance-review turnaround reduction) to Finance PPM dashboard KR widget.
- [ ] SC-3: Bind SC-PH-B03 (incorrect safe-action rate) to Governance / Control dashboard widget.
- [ ] SC-4: Bind SC-PH-B04 (wrong-company-context incidents) to Governance / Control dashboard widget.
- [ ] SC-5: Bind SC-PH-B05 and SC-PH-B06 (cash advance discipline) to Cash Advance OKR widgets.
- [ ] SC-6: Bind SC-PH-B07 and SC-PH-B08 (PH readiness recall / false-ready rate) to PH Tax / BIR OKR widgets.
- [ ] SC-7: Bind SC-PH-B09 (close blocker surfacing) to Close OKR widget.
- [ ] SC-8: Bind SC-PH-B10 (evidence completeness) to Evidence Completeness dashboard widget (§21.1).
- [ ] SC-9: Bind SC-PH-B11 (document grounding coverage) to Document Grounding Coverage widget (§21.2).
- [ ] SC-10: Bind SC-PH-B12 and SC-PH-B13 (Office publishing quality) to Publishing OKR widgets.
- [ ] SC-11: Bind SC-PH-B14 (cost per workflow) to FinOps / AI runtime health dashboard section.
- [ ] SC-12: Define owner, source, cadence, and alert threshold for each SC-PH-B metric.
- [ ] SC-13: Add exit-gate verification task for each Gate A–D criterion in production checklist.

---

## Phase 27: Microsoft 365 Developer Sandbox

> Scope: dev/test only. See `prd.md §25` for product rule. No production data.

- [ ] M365-1: Confirm eligibility path for Microsoft 365 E5 developer subscription via Developer Program.
- [ ] M365-2: Provision Pulser Office/M365 sandbox tenant (one per org; 25 licenses).
- [ ] M365-3: Validate Word add-in prototyping path (review packs, close memos, signoff documents). **`pulser-office-publishing`**
- [ ] M365-4: Validate Excel add-in prototyping path (OKR scorecards, KPI workbooks, scenario models). **`pulser-office-publishing`**
- [ ] M365-5: Validate PowerPoint add-in prototyping path (close decks, CFO review decks, board packs). **`pulser-office-publishing`**
- [ ] M365-6: Validate Teams / SharePoint / Graph integration paths. **`pulser-copilot-experience`**
- [ ] M365-7: Use tenant as publishability QA surface for generated Office artifacts.
- [ ] M365-8: Verify Entra-authenticated M365 identity patterns align with `prd.md §18` identity model.
- [ ] M365-9: Keep all critical configurations backed up outside the developer tenant (90-day renewal risk).
- [ ] M365-10: Do not store finance-critical evidence or production business data in developer tenant.

---

*Last updated: 2026-04-11*
