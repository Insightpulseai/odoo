# Epic 05 — Pulser for Odoo: Admin Tooling and UI Test Automation

> Narrow engineering-tools backlog. Adapts patterns from Microsoft model-driven app tooling + Easy Repro UI testing — **without** recreating Dataverse-specific tools inside Odoo.

**Reference docs:**
- Microsoft model-driven app **Developer tools** page (XrmToolBox, FetchXML Builder, Ribbon Workbench, View Designer, Dataverse REST Builder — community/admin/dev utilities, **not Microsoft-supported**)
- Microsoft model-driven app **Testing tools (client)** page (Easy Repro built on Selenium, recommended for larger client-side solutions)

**Doctrine anchors:**
- Microsoft's developer-tools page is a tooling catalog, **not a product architecture requirement**. Many listed tools are community-built and explicitly not Microsoft-supported. For Pulser/Odoo: adapt the pattern of targeted admin/dev utilities while keeping generic tooling outside core ERP modules.
- The transferable concept from the testing page is not Easy Repro itself, but the principle of **resilient browser-based UI automation** for larger client-side solutions, with framework abstractions that avoid brittle HTML parsing.

**Priority:** Secondary backlog. Below Finance Domain Parity, Integration/Business Events/Workflow Surfaces, and Administration/Servicing/Environment Lifecycle.

**Success criteria:** admin/dev utility doctrine defined; Odoo-equivalent utility shortlist identified; UI automation/testing baseline defined; Easy Repro/Selenium concepts mapped to Odoo web testing strategy; **no unnecessary custom `ipai_*` module created for generic admin tooling**.

---

## Feature 1 — Benchmark Model-Driven App Developer Tools

Tags: `pulser-odoo`, `tooling`, `admin-tools`

### Story 1.1 — Catalog Microsoft model-driven admin/developer tool patterns
Tool categories documented (admin/configuration/query/API-generation/testing). Dataverse-specific tools marked non-portable. Odoo/Pulser-equivalent opportunities identified.

### Story 1.2 — Define Odoo-equivalent utility doctrine
"Adapt before build" rule documented. Prefer Odoo shell + scripts + existing ecosystem tools first. Thin utility scripts allowed where gaps remain. Custom Odoo addon creation = last resort (per `feedback_odoo_module_selection_doctrine.md`).

### Story 1.3 — Identify reusable utility candidates
Shortlist: query helpers, metadata inspection, export/import helpers, config diff tools. Each classified as reuse / script / sidecar / reject. Owner + priority. Domain-module creation rejected unless justified.

---

## Feature 2 — Define UI Test Automation Baseline

Tags: `pulser-odoo`, `ui-testing`, `test-automation`

### Story 2.1 — Map Easy Repro testing concepts to Odoo
Selenium/browser automation concepts mapped. Odoo web flows identified for automation. Resilient selector / page-object strategy documented. Dataverse-specific assumptions marked OUT OF SCOPE.

### Story 2.2 — Define canonical UI automation framework for Odoo and Pulser
Preferred framework selected (Playwright preferred — already in IPAI stack per memory). Test layering between unit/integration/UI documented. Core finance / project / Pulser UI journeys identified. CI execution expectations.

### Story 2.3 — Define critical-path UI regression suite
Smoke suite scenarios. Environment + data prerequisites. Pass/fail + evidence rules. Release-blocking threshold. (Cross-references epic-01 Story 3.3 "Automate regression suite for critical scenarios".)

---

## Feature 3 — Create Admin Utility and Test Governance

Tags: `pulser-odoo`, `tooling`, `governance`

### Story 3.1 — Define supportability rules for community and third-party tools
Third-party / community-tool policy. Support + ownership expectations. Security review expectations. Exit / replacement criteria.

### Story 3.2 — Define when utility code may live outside Odoo modules
Script vs sidecar vs addon decision rule. Generic admin utilities default OUTSIDE `addons/ipai`. Only domain-coupled UI or action surfaces may enter Odoo addons. Review checklist documented.

### Story 3.3 — Define UI test ownership and maintenance policy
Ownership by app/domain. Flaky-test handling. Maintenance cadence. Selector / page-object update rules.

---

## Priority sequencing

**P0:** 1.2, 2.2, 3.2
**P1:** 1.1, 2.1, 2.3, 3.3
**P2:** 1.3, 3.1
