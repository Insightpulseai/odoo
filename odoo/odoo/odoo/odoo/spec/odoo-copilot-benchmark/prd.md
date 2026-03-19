# Odoo Copilot Benchmark — Product Requirements Document

## 1. Problem Statement

Enterprise AI copilots (SAP Joule, Microsoft 365 Copilot, Salesforce Einstein) set expectations for transactional, navigational, and informational capabilities. Odoo Copilot needs a structured benchmark to measure capability parity, identify gaps, track progress across releases, and ensure governance standards are met. Without this, capability claims are anecdotal and non-comparable.

## 2. Product Goal

Build a benchmark framework that evaluates Odoo Copilot against enterprise-grade conversational assistant standards using SAP Joule's three capability classes as the reference model — without cloning SAP features.

## 3. Objectives

- OBJ-1: Define measurable capability parity across transactional, navigational, and informational classes
- OBJ-2: Enforce governance safety (permissions, confirmation, auditability, grounding) as hard gates
- OBJ-3: Enable cross-release regression detection and progress tracking
- OBJ-4: Produce machine-readable evidence artifacts for every benchmark run
- OBJ-5: Keep the benchmark CE-safe and runnable in standard dev environments

## 4. Users

| Persona | Role | Benchmark Interest |
|---------|------|--------------------|
| Engineering lead | Maintainer | Track capability progress, detect regressions |
| Product owner | Stakeholder | Understand capability gaps vs enterprise competitors |
| QA engineer | Runner | Execute benchmark, validate evidence |
| Contributor | Developer | Know what "done" looks like for a capability |

## 5. User Stories

### US-1: Benchmark Execution
As a QA engineer, I can run the benchmark suite against a running Odoo instance and get a scored report showing pass/fail per scenario with evidence artifacts.

### US-2: Capability Gap Analysis
As a product owner, I can view a per-domain capability matrix showing which transactional, navigational, and informational scenarios pass, fail, or are not yet implemented.

### US-3: Release Comparison
As an engineering lead, I can compare benchmark results across two releases to detect regressions or improvements in capability and governance scores.

### US-4: Scenario Contribution
As a contributor, I can add a new benchmark scenario by following the scenario schema and registering it in the scenario catalog.

### US-5: Governance Audit
As a product owner, I can verify that all transactional scenarios enforce permission checks, confirmation dialogs, and audit trails — with evidence.

## 6. Capability Taxonomy

### 6.1 Capability Classes

| Class | Definition | SAP Joule Analog |
|-------|-----------|------------------|
| **Transactional** | Execute state-changing business actions | "Create a purchase order", "Post a journal entry" |
| **Navigational** | Direct user to views, records, configurations | "Show me open opportunities", "Go to inventory settings" |
| **Informational** | Retrieve and present factual data with citations | "What's the AR aging?", "Summarize last month's tickets" |

### 6.2 Scoring Dimensions

| Dimension | Type | Weight | Description |
|-----------|------|--------|-------------|
| Capability | Hard gate | — | Can the copilot perform the action? |
| Correctness | Hard gate | — | Is the result accurate? |
| Permission | Hard gate | — | Does it respect Odoo ACLs? |
| Confirmation | Hard gate | — | Does it ask before writes? |
| Auditability | Hard gate | — | Is the trace logged? |
| Grounding | Hard gate | — | Are sources cited? (informational only) |
| Completeness | Soft score | 0.30 | Does it address the full request? |
| Clarity | Soft score | 0.20 | Is the response clear? |
| Latency | Soft score | 0.10 | Within time bounds? |

## 7. Functional Requirements

### FR-1: Scenario Registry
A YAML-based registry of benchmark scenarios organized by domain, capability class, and persona. Each scenario follows the schema defined in `constitution.md §6`.

### FR-2: Scenario Runner
A runner that executes scenarios against a running Odoo instance, captures evidence, and produces raw results.

### FR-3: Evidence Capture
Every scenario execution captures: prompt text, action trace, retrieved sources (if informational), response latency, and permission result.

### FR-4: Hard Gate Evaluation
Hard gates are evaluated as binary pass/fail. A scenario with any hard gate failure is scored as FAIL regardless of soft scores.

### FR-5: Soft Score Computation
Soft scores are computed per dimension with configurable weights. The weighted sum produces a scenario score between 0.0 and 1.0.

### FR-6: Domain Aggregation
Results are aggregated per domain (CRM, Sales, Purchase, etc.) with per-class subtotals.

### FR-7: Release Tagging
Benchmark results are tagged with the Odoo Copilot version, Odoo CE version, and benchmark run timestamp.

### FR-8: Cross-Release Comparison
A comparison report shows per-scenario deltas between two tagged benchmark runs.

### FR-9: Governance Report
A dedicated governance view shows permission, confirmation, auditability, and grounding results across all scenarios.

### FR-10: Evidence Persistence
Evidence artifacts are written to `docs/evidence/<YYYYMMDD-HHMM>/copilot-benchmark/` with a machine-readable summary.

## 8. Non-Functional Requirements

- NFR-1: Benchmark is runnable in a devcontainer with standard tools (Python, curl, Odoo RPC)
- NFR-2: Evidence format is JSON (machine-readable) with optional Markdown summary (human-readable)
- NFR-3: Scoring is deterministic and reproducible
- NFR-4: No Enterprise modules, IAP, or Odoo.sh dependencies
- NFR-5: Scenario registry supports incremental additions without breaking existing results
- NFR-6: Informational latency target: < 5s; Transactional: < 10s

## 9. Success Metrics

### Product Metrics
- Scenario coverage: ≥ 3 scenarios per domain × capability class combination
- Hard gate pass rate across all transactional scenarios
- Weighted soft score trend across releases

### User-Value Metrics
- Time to run full benchmark: < 30 minutes
- Time to add a new scenario: < 15 minutes
- Gap identification accuracy: every failed scenario maps to a specific code path

### Governance Metrics
- 100% of transactional scenarios include permission + confirmation + audit gates
- 100% of informational scenarios include grounding gate
- Zero scenarios with skipped hard gates

## 10. Out of Scope

- LLM model comparison (benchmark evaluates the system, not the model)
- UI fidelity comparison with SAP Joule
- Performance stress testing (covered by separate NFR benchmarks)
- Odoo Enterprise Edition testing
- Multi-tenant benchmark scenarios
- Real-time production monitoring

## 11. Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Odoo Copilot core modules installed | Required | Cannot benchmark without `ipai_ai_copilot` |
| Copilot tool registry populated | Required | Transactional scenarios need tools |
| RAG pipeline functional | Required for informational | Grounding checks need source data |
| Benchmark runner implementation | To build | Core deliverable |
| Demo data seeded | Required | Scenarios need records to operate on |

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Copilot modules not stable enough for benchmarking | Medium | High | Gate on Phase 2 functional proof |
| Scenario definitions too abstract to evaluate | Medium | Medium | Require concrete expected_behavior in schema |
| Governance checks too strict for early releases | Low | Medium | Allow "not yet implemented" as a valid result (distinct from FAIL) |
| Evidence capture adds latency to scenarios | Low | Low | Capture is post-execution, not inline |

## 13. Release Slices

### Slice 1: Framework Foundation
- Scenario schema + registry structure
- Runner skeleton (manual execution)
- Evidence capture format
- Hard gate evaluation logic

### Slice 2: Scoring + Reporting
- Soft score computation
- Domain aggregation
- Summary report generation (JSON + Markdown)
- Release tagging

### Slice 3: Governance Benchmark
- Permission gate implementation
- Confirmation gate implementation
- Audit trace gate implementation
- Grounding gate implementation
- Governance-specific report view

### Slice 4: Cross-Release + Extended Coverage
- Release comparison report
- Scenario catalog expanded to all 9 domains
- Regression detection
- Benchmark CI integration
