# Assessment Evidence Harvester

## Purpose

Gather, normalize, and classify evidence for the internal Azure assessment harness.

This skill is responsible for finding the strongest available evidence for each assessment domain before any answer or score is produced.

It does not score.
It does not write optimistic conclusions.
It builds the evidence pack that later skills and judges must rely on.

## When to use

Use this skill when:
- preparing answers for WAF core questions
- preparing answers for workload overlays
- preparing answers for transformation-readiness overlays
- validating whether a claim is backed by current evidence
- determining whether a control is present, governed, and/or proven

## Inputs

Primary inputs may include:
- `docs/architecture/IPAI_PLATFORM_ANALYSIS.md`
- `docs/odoo-on-azure/**`
- `platform/docs/**`
- `infra/docs/**`
- `odoo/docs/**`
- `agents/docs/**`
- `data-intelligence/docs/**`
- `ssot/**`
- architecture review templates
- runtime inventory exports
- reconciliation and drift artifacts
- evidence packs under `docs/evidence/**`

## Output contract

For each domain or question, return:

- `claim`
- `evidence_sources`
- `evidence_summary`
- `classification`
  - `present`
  - `governed`
  - `proven`
- `confidence`
  - `low`
  - `medium`
  - `high`
- `missing_evidence`
- `risk_flags`

## Core rules

### 1. Prefer current-state evidence

Prefer evidence that reflects the current live or recently reconciled platform state over aspirational design text.

### 2. Distinguish design from proof

A Bicep module, SSOT file, or architecture page may show intended state.
It is not proof that the control is live, owned, tested, or effective.

### 3. Distinguish present vs governed vs proven

Always classify each finding into:
- **Present** -- the control or resource exists
- **Governed** -- the control is source-controlled, owned, and policy-backed
- **Proven** -- the control has been validated, tested, or demonstrated in operations

### 4. Treat drift as evidence degradation

If a claim depends on unmanaged runtime state or untracked resources, lower confidence and flag drift risk.

### 5. Be conservative with stale docs

If a document is old, broad, or clearly aspirational, classify it as weak evidence unless corroborated elsewhere.

## Evidence collection procedure

### Step 1 -- Identify the question or domain

Map the request into one of:
- WAF core pillar
- workload overlay
- transformation-readiness phase
- adjacent Microsoft assessment family

### Step 2 -- Gather direct evidence

Collect the most direct, source-of-truth-adjacent artifacts.

### Step 3 -- Gather corroborating evidence

Look for:
- ownership signals
- operational evidence
- runtime confirmation
- test/restore/drill proof
- backlog or risk references

### Step 4 -- Classify the evidence

For each claim:
- is it present?
- is it governed?
- is it proven?

### Step 5 -- Return missing-proof list

Explicitly list what would be needed to raise confidence or score.

## Transformation-readiness handling

For transformation overlay work, classify evidence under:
1. Discover
2. Analyze
3. Design
4. Implement
5. Operate

Pay special attention to:
- single source of truth
- dependency mapping
- target-state clarity
- enablement/change-management evidence
- post-go-live KPI and governance evidence

## Refusal / escalation conditions

Escalate instead of overclaiming when:
- no current-state inventory exists
- only runtime screenshots or memory support the claim
- only intended-state docs exist
- no owner is identified
- the claim depends on untracked resources
