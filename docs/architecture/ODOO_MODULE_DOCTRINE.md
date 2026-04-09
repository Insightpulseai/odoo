# Odoo Module Doctrine

## Current Platform Summary

- **Transactional SoR:** Odoo 18 CE + curated OCA
- **Custom extension boundary:** narrow IPAI bridge/domain layer only
- **Canonical runtime:** Azure Container Apps behind Front Door / WAF
- **Canonical AI control plane:** Microsoft Foundry
- **Canonical AI runtime pattern:** Container Apps + AI Search + managed identity / keyless auth
- **Decision order:** Core first -> OCA second -> config/data third -> IPAI custom last

---

## Purpose

This document defines the canonical rules for when to use:

- Odoo core
- OCA addons
- IPAI custom modules
- external platform bridges

It exists to keep the Odoo 18 codebase modular, upgrade-safe, and governance-friendly while preventing unnecessary custom module sprawl.

---

## Core Principles

### 1. Module-first is true, but custom-module-first is false
Odoo is extended through modules, but not every requirement justifies a new custom module.

Decision order:

1. Use **Odoo core** if the requirement is already covered.
2. Use **OCA** if the requirement is covered by a maintained community addon.
3. Use **configuration / metadata / templates / seed data** if code is not required.
4. Use a thin **IPAI custom module** only when the requirement is genuinely not solved by the above.
5. Use an **external bridge/service** when the capability is primarily platform, AI, OCR, or edge infrastructure behavior.

---

## Layering Doctrine

### Odoo Core
Odoo core owns the transactional baseline and first-party business capabilities.

Examples:
- CRM
- Sales
- Purchase
- Inventory
- Accounting
- Project
- Timesheets
- Website
- POS

### OCA
OCA owns open-source parity and workflow-depth extensions.

Use OCA for:
- accounting/reporting/reconcile depth
- workflow enhancements
- purchase/sales/project extensions
- spreadsheet/dashboard improvements
- sign/document enhancements
- quality/warehouse refinements
- subscription/contract extensions
- other mature 18.0 community addons

### IPAI
IPAI owns only these categories, and must stay narrow:

- Azure-specific runtime/security bridges, especially ACA + Front Door + Foundry-connected lanes
- AI/copilot/agent bridges
- PH-specific or InsightPulseAI-specific business logic
- intentionally productized UX shell layers
- bounded integration modules that do not belong in OCA or core

### External Platform Bridges
Use external services rather than Odoo modules when the value is primarily:

- OCR / document extraction
- hosted AI inference / retrieval
- edge ingress / WAF / container runtime behavior
- enterprise identity provider behavior
- infrastructure operations / observability

In these cases, Odoo should contain only the thinnest necessary integration layer.

---

## Runtime Doctrine

### Canonical current runtime
The canonical current Odoo runtime is:

- **Azure Container Apps**
- fronted by **Front Door / WAF**
- with Azure-native observability, identity, and supporting services

### Alternate runtime lane
VM / VMSS is an alternate self-managed hosting model only.
It is not the current default doctrine.

### Implication for custom modules
Runtime-specific modules are allowed only when they solve real Azure/runtime problems, such as:

- proxy/header normalization
- ingress trust/security enforcement
- cloud identity bridge behavior
- platform-aware AI/document service integration

---

## Microsoft Foundry / AI Doctrine

### AI Control Plane
The canonical current AI control plane is **Microsoft Foundry**.

Use Foundry for:
- model selection and deployment governance
- agent-oriented AI project structure
- evaluation and experiment-oriented AI workflows
- standardized access to Azure AI capabilities through the Foundry experience, SDK, or CLI

### Model Doctrine
Use the current approved Foundry model catalog as the source for supported AI model choices.
Model selection must remain environment-driven and replaceable.

Do not hardcode product doctrine around a single model family.
Instead:
- bind supported models through configuration
- keep prompts and orchestration portable
- isolate provider/model assumptions behind IPAI bridge modules

### AI Runtime Doctrine
The canonical runtime pattern for AI sidecars, copilots, and agent services is:

- **Azure Container Apps**
- **AI Search** for retrieval when needed
- **managed identity / keyless auth** where supported
- Foundry or Azure AI services for model execution

### AI Lane Separation Rule
AI is an **adjacent capability lane**, not the transactional system of record.

Therefore:
- AI failure must not block core ERP transactions
- core business records remain Odoo-owned
- retrieval indexes, prompt state, and agent state must not redefine ERP truth
- AI outputs must be treated as assistive until explicitly committed by approved business logic

---

## Authentication and Integration Doctrine

### Authentication
Use Odoo core authentication features and documented provider integrations first.

Default order:
1. Odoo core auth feature or documented provider setup
2. provider configuration and system parameters
3. OCA addon if a maintained extension exists
4. IPAI bridge only for Azure/Entra-specific or platform-specific behavior not cleanly covered by core

Custom auth modules must not replace generic authentication behavior already provided by Odoo.

### Integration
Treat integration as a native Odoo capability surface.

Prefer:
- core connectors and documented integrations
- external API usage
- OCA integration addons
- thin bridge modules

Avoid:
- broad custom "enterprise bridge" modules that bundle unrelated integrations
- duplicating documented core integrations with custom wrappers
- embedding provider-specific platform logic into generic business modules

### Cloud / Azure-specific exception
Azure-specific behaviors may still justify IPAI modules when they address:
- Entra/OIDC/MFA bridge behavior
- ACA / proxy / ingress behavior
- Front Door / trust boundary enforcement
- Azure AI / Foundry / Document Intelligence bridge behavior
- Azure storage or keyless auth patterns not cleanly covered by core

---

## IPAI AI Module Boundary Rules

The following are valid categories for AI-related IPAI modules:

- copilot orchestration
- agent/tool routing
- Azure AI / Foundry bridge logic
- retrieval bridge logic
- document intelligence bridge logic
- bounded UX shells for AI interaction

The following are **not** valid reasons by themselves to create a new IPAI AI module:

- exposing a model that can be configured without code
- duplicating a generic chat frontend pattern already handled outside Odoo
- storing environment credentials or endpoints in code
- mixing platform orchestration, business logic, and demo UX in a single module
- replacing a CE/OCA capability with AI where deterministic business logic is still required

### Required AI module properties
Every new AI-related IPAI module must show:
- bounded scope
- explicit failure isolation
- explicit model/config indirection
- scenario-level validation
- clear separation between assistive output and committed ERP state

---

## Template and Accelerator Reuse Doctrine

Microsoft templates and accelerators are reference architectures, not automatic product architecture.

Use them for:
- deployment contracts
- managed identity patterns
- AI Search / retrieval patterns
- Container Apps topology
- observability patterns
- CI/CD structure
- evaluation / monitoring patterns

Do not use them as justification to:
- move core ERP runtime into an AI template architecture by default
- introduce unnecessary platform services into the ERP baseline
- collapse business requirements into generic sample-app assumptions

---

## Keep / Replace / Exclude Rules

### Keep as IPAI custom module
Keep a custom module only if it is one of the following:

- PH/local compliance logic
- Azure-specific runtime/security bridge
- AI/copilot/agent orchestration bridge
- product shell / branding layer with clear user-facing value
- bounded workspace or integration bridge not replaceable by OCA/core

### Replace with CE/OCA/config
Do not keep a custom module if it is mainly:

- wrapping an existing core feature
- wrapping an OCA feature without adding durable product value
- storing configuration that should live in data records
- duplicating reporting/workflow already available in CE+OCA
- mixing multiple concerns that should be split

### Exclude from capability claims
Do not count these as product capability modules:

- seed/demo modules
- data loaders
- sample dashboards
- example projects/tasks/stages
- migration helper modules
- temporary compatibility wrappers

These may exist in-repo, but they must not be presented as parity surface.

---

## IPAI Module Taxonomy

Every IPAI module must declare one of these classifications:

- `keep_custom`
- `migrate_and_keep`
- `replace_with_ce_oca`
- `partial_replace_keep_shell`
- `seed_only_exclude`

---

## Custom Module Acceptance Criteria

A new IPAI module may be created only if all of the following are true:

1. The requirement is not adequately covered by Odoo core.
2. The requirement is not adequately covered by a maintained OCA 18.0 addon.
3. The requirement cannot be solved with configuration, data records, templates, automation rules, or view inheritance alone.
4. The module has one bounded purpose.
5. The module has named ownership.
6. The module has explicit tests or scenario validation.
7. The module has a clear upgrade path for Odoo 18.
8. The module does not silently duplicate another layer.

---

## Preferred Implementation Patterns

### Prefer configuration over code
Prefer settings, model records, templates, pricing tables, sale order templates, MIS definitions, dashboard records, scheduled actions, and server actions before writing Python code.

### Prefer view inheritance over view replacement
Use view inheritance to extend existing views instead of replacing them wholesale.

### Prefer wizard/report/shell modules over deep model forks
If a requirement is mostly guided UX, calculation wizard, dashboard, action menu, report, ranking/leaderboard, or branded presentation — prefer a thin wizard/report/shell module instead of changing core transactional models.

### Prefer bridge modules over embedded infrastructure logic
For AI, OCR, identity, and ingress behavior:
- keep infrastructure logic in Azure/platform services
- keep Odoo-side code thin and bounded
- preserve failure isolation so ERP transactions still work if the bridge fails

---

## Security Doctrine

Every custom module must define security deliberately.

Required:
- explicit `ir.model.access.csv` where applicable
- no accidental broad access
- no hidden privilege escalation through buttons/controllers
- no dependency on admin-only manual actions for normal business flow

For bridge modules:
- prefer platform identity and tokenless auth where possible
- avoid storing secrets in module code or repo data files

---

## Seed / Demo / Fixture Doctrine

Seed modules must remain separate from capability modules.

Rules:
- seed modules must not be required to prove business capability
- seed modules must not be counted as parity coverage
- seed modules must not hide missing product logic
- seed modules should be installable/removable without changing core capability

---

## Reporting / Proxy / ACA Note

Because the runtime is behind Azure ingress/proxy layers, report generation and linked asset resolution must be validated in the deployed environment.

For PDF/QWeb reports:
- validate `web.base.url`
- use `report.url` where needed
- verify wkhtmltopdf asset reachability
- treat proxy/header/report URL issues as runtime integration concerns, not generic app bugs

---

## Parity Doctrine

### What counts as parity
Parity means the target business outcome is supported and validated.

Parity does **not** require:
- pixel-perfect UI match
- identical naming
- identical internal implementation
- identical vendor packaging

### Allowed scoped parity labels
Use these labels instead of blanket "full parity" claims:

- `full_operational_parity`
- `full_agency_ops_parity`
- `full_partner_ops_parity`
- `workflow_parity_via_ipai`
- `partial`
- `mostly_yes`
- `strongest_yes`

### Evidence rule
No parity claim is valid without at least one of:
- install proof
- scenario/UAT proof
- module inventory proof
- runtime validation proof

---

## Decision Checklist Before Creating a New IPAI Module

Answer all of these:

1. What exact business or platform gap is not covered by core?
2. Which OCA repos/modules were checked?
3. Why is config/data/view inheritance insufficient?
4. Is this a bridge, shell, local-domain module, or true new business object?
5. Can the module fail without breaking core ERP transactions?
6. What tests or scenarios will prove it works?
7. Is this capability strategically worth owning long term?

If these questions cannot be answered clearly, do not create the module yet.

---

## Browser Automation and Debugging Doctrine

### Testing Stack Order

Browser-touching validation uses three tools in a strict priority order:

1. **Odoo-native tests** (TransactionCase, Form, HttpCase, tours) — correctness authority
2. **Playwright** (browser smoke/regression, cross-browser, traces) — browser regression authority
3. **Chrome DevTools MCP** (interactive debugging, network/perf inspection) — interactive debugging authority

### Supplementation Rule

Playwright and Chrome DevTools MCP **supplement** Odoo-native tests. They never replace them. Every browser regression must have an Odoo-native test that proves the server-side behavior is correct before a Playwright test is added to cover the browser surface.

### Responsibility Split

| Tool | Owns | Does Not Own |
|------|------|--------------|
| **Odoo-native** | Model correctness, form save/load, field defaults, onchange, access rules, tour-level UI flows | Cross-browser rendering, network waterfall, JS console errors |
| **Playwright** | Page load smoke, settings open/save, menu navigation, client action stability, screenshot/trace capture | Business logic correctness, ORM behavior, access rule enforcement |
| **Chrome DevTools MCP** | Interactive JS debugging, network/perf inspection, DOM state during failure, console error triage | Automated regression coverage, CI gating |

### Current Regression Mapping — Project Settings Defects

| Defect class | Odoo-native coverage | Playwright coverage | DevTools MCP role |
|--------------|---------------------|--------------------|--------------------|
| Settings form save failure | TransactionCase + Form mock | Playwright open/save smoke | Inspect XHR payload on failure |
| Action/menu client crash | HttpCase tour | Playwright navigation smoke | Console error capture |
| JS asset load failure | (not applicable) | Playwright network assertion | Network waterfall inspection |

---

## Summary

The default order of operations is:

**Core first -> OCA second -> config/data third -> IPAI custom last**

IPAI exists to stay thin, strategic, and durable.
It should not become a second ERP inside Odoo.

---

*Last updated: 2026-04-05*