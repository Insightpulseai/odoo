# Epic 02 — Pulser for Odoo: Architecture, Development, and Platform Hardening

> Engineering-track backlog: architecture, tooling, Odoo equivalent of AOT-style elements, code/test discipline, reporting, data integration, security/performance.

**Success criteria:** architecture baseline approved; developer workflow standardized; Odoo extension model codified + reusable; reporting/data/security/performance foundations implemented; CI + release gates enforce quality.

---

## Feature 1 — Plan Architecture and Solution Design

Tags: `pulser-odoo`, `architecture`, `engineering`

### Story 1.1 — Define canonical target architecture
Transaction, data intelligence, agent, delivery, partner-ops boundaries defined (per `spec/pulser-odoo/prd.md` §0). Odoo, Databricks/Fabric, Foundry, GitHub/Azure roles explicit. Runtime/integration/governance responsibilities assigned. Anti-patterns documented.

### Story 1.2 — Define Odoo extension doctrine in architecture
Decision order embedded (CE → property fields → OCA same-domain → adjacent → compose → thin `ipai_*`). Thin-bridge rule, `MODULE_INTROSPECTION.md` + `TECHNICAL_GUIDE.md` requirement, review criteria.

### Story 1.3 — Define environment and deployment topology
Dev/staging/prod topology. Odoo runtime dependencies. Data/agent/reporting dependencies. Network, secrets, observability, rollback boundaries.

### Story 1.4 — Define Well-Architected review model
Azure WAF criteria. GitHub WAF criteria. AI + SaaS workload overlays. Architecture changes require trade-off + risk notes.

---

## Feature 2 — Apply Developer Tools

Tags: `pulser-odoo`, `tooling`, `ci`

### Story 2.1 — Standardize developer workstation and repo tooling
Canonical Python/Odoo tooling. Devcontainer/editor/runtime boundaries. Linting, formatting, test, packaging standards. Secrets + env handling.

### Story 2.2 — Standardize engineering automation and CI gates
CI covers lint + unit + integration + doctrine checks. SSOT drift checks. Odoo extension-policy checks where feasible. Actionable failure reporting.

### Story 2.3 — Standardize AI-assisted development workflow
Spec Kit / doctrine workflow. Branch/PR/review expectations. Agent roles + allowed actions. Implementation-to-review evidence expectations.

---

## Feature 3 — Design and Develop AOT-Equivalent Elements

Tags: `pulser-odoo`, `odoo-extension`

### Story 3.1 — Define Odoo equivalents for AOT-style building blocks
Mapping for models, fields, views, actions, menus, security, reports, scheduled jobs, integrations. Preferred extension points. Non-preferred invasive overrides. Example patterns.

### Story 3.2 — Create reusable Odoo module scaffold and thin-bridge template
Template exists at `addons/ipai/_template/` (already landed). Required docs scaffolded. Test structure scaffolded. Security/data/view/model folders scaffolded.

### Story 3.3 — Define model/view/security composition patterns
`_inherit` patterns. View inheritance (XPath) patterns. Security/access-rule patterns. Property-field usage rules.

---

## Feature 4 — Develop and Test Code

Tags: `pulser-odoo`, `testing`

### Story 4.1 — Define code-quality and testing standards
Unit/integration/regression expectations. Test naming + placement. Coverage for critical paths. Failure-mode testing.

### Story 4.2 — Implement automated test pyramid for Odoo and Pulser
Unit tests for pure logic. Odoo integration tests for model/view/security. E2E smoke for critical journeys. Pulser prompt/action guardrail tests.

### Story 4.3 — Define defect triage and regression policy
Severity model. Regression tagging. Release-blocking defect rules. Re-test + closure criteria.

---

## Feature 5 — Implement Reporting

Tags: `pulser-odoo`, `reporting`

### Story 5.1 — Define reporting architecture across Odoo, Databricks, and Fabric
Odoo-native operational reporting scope. Databricks-curated data product layer. Fabric/Power BI consumption. Ownership by report class.

### Story 5.2 — Define finance and project-operations reporting baseline
Finance operational reports. Project profitability/utilization/budget. Executive summaries + KPI dashboards. Pulser-assisted report narration.

### Story 5.3 — Define report governance and semantic layer ownership
Metric ownership. Semantic layer responsibilities. Source-of-truth rules. KPI change-control process.

---

## Feature 6 — Integrate and Manage Data Solutions

Tags: `pulser-odoo`, `integration`, `data`

### Story 6.1 — Define integration architecture for Odoo and external systems
Sync vs async. API / event / file / staged-load patterns. Retry/idempotency/error-handling. Ownership + observability.

### Story 6.2 — Define data pipeline and lakehouse contract
Extract patterns from Odoo. Bronze/silver/gold layering. Curated finance/project datasets. Access + governance rules.

### Story 6.3 — Define data migration and reference-data management model
Reference/master/transactional data classes. Entity ownership. Validation + reconciliation. Refresh/movement across environments.

---

## Feature 7 — Implement Security and Optimize Performance

Tags: `pulser-odoo`, `security`, `performance`

### Story 7.1 — Define identity, access, and approval-control model
Human roles + access scopes. Pulser capability levels: read/recommend/draft/act. Approvals for sensitive actions. Auditability.

### Story 7.2 — Implement runtime observability and performance baselines
Health, latency, throughput, failure metrics. Odoo app + worker baselines. Agent/service baselines. Dashboard + alert ownership.

### Story 7.3 — Define performance optimization strategy for Odoo and data stack
Odoo optimization levers. Query/report/pipeline optimization ownership. Caching + background-job strategies. Load test + benchmark plan.

### Story 7.4 — Define security hardening and incident response model
Secrets, rotation, storage. Network + environment hardening. Incident severity + response ownership. Agent disablement + safe-mode procedures.

---

## Feature 8 — Benchmark and Readiness

Tags: `pulser-odoo`, `benchmark`, `readiness`

### Story 8.1 — Benchmark D365 development concepts to Odoo/Azure equivalents
Architecture, tooling, AOT-equivalent, reporting, data, security mapped. Odoo/Azure substitutes explicit. "Do not clone D365 internals" guidance. Attached to SSOT/spec.

### Story 8.2 — Define engineering readiness checklist for new domain work
Checklist: architecture, extension choice, testing, reporting, data, security. Required approvals + evidence. Reuse/adaptation-first checks. Reusable across Finance, Services, Pulser agent work.

---

## Priority sequencing

**P0:** 1.1, 2.1, 3.1, 4.1, 5.1, 7.1
**P1:** 1.3, 2.2, 3.2, 4.2, 6.1, 7.2
**P2:** 1.4, 2.3, 5.3, 7.3, 7.4, 8.1
