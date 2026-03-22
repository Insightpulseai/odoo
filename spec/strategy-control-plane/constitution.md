# Constitution — Strategy Control Plane

## Status
Draft

## Purpose
Strategy Control Plane is a successor to legacy OKR tools (including the retired Microsoft Viva Goals). It connects strategic intent to execution evidence across the platform.

## Governing Principles

### 1. Evidence over self-report
Progress must be derived from connected systems first, manual entry second.

### 2. Open system boundaries
The product integrates with source systems but does not replace them.

### 3. Strategy-to-runtime traceability
Every strategic item must be traceable to plans, work items, specs, code, deployments, runtime evidence, and business metrics.

### 4. Human approval over autonomous truth mutation
Agents may draft, summarize, and propose. Agents may not silently change executive-visible status or governance policy.

### 5. Hybrid outcome model
Support OKRs, KPIs, initiatives, and milestones in one model. Do not force everything into a single semantic type.

### 6. Review-first UX
The primary experience is review preparation and decision support, not dashboard clutter.

### 7. Machine-readable by default
All strategic objects, relationships, and evidence links must be API-accessible and exportable.

### 8. No vendor lock-in
The product must remain portable and open. Strategic data must not be trapped in a single productivity suite.

## In Scope
- Strategic hierarchy (themes, objectives, KRs, KPIs, initiatives, milestones)
- Execution graph linking goals to work items, specs, repos, deployments, metrics
- Evidence engine computing progress confidence from connected systems
- Review engine generating operating review packets
- Agent layer for narrative drafting, risk summarization, corrective proposals
- Governance: RBAC, audit trails, locked snapshots, approval workflows

## Out of Scope
- Replacing source systems (Git, boards, ERP, analytics, observability)
- Generic BI or project management
- HR engagement or employee experience positioning
- Full autonomous strategy execution without human review
