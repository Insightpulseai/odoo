# Platform Doctrine

> **Single canonical doctrine document for the InsightPulse AI platform.**
> Consolidates architectural decisions from Odoo docs, Azure docs, Microsoft Foundry docs,
> Playwright docs, and Chrome DevTools docs review.
>
> For module-level governance (acceptance criteria, taxonomy, keep/replace rules),
> see [ODOO_MODULE_DOCTRINE.md](ODOO_MODULE_DOCTRINE.md).
>
> Last updated: 2026-04-05

---

## 1. Extension Model

Odoo centers extension around **modules**. A module is a self-contained directory containing:

- `__manifest__.py` -- declares name, version, depends, data files, assets
- `models/` -- Python business logic and ORM definitions
- `views/` -- XML view definitions and view inheritance
- `data/` -- seed records, default configuration, scheduled actions
- `security/` -- `ir.model.access.csv` and record rules
- `reports/` -- QWeb report templates
- `wizards/` -- transient models for guided user flows
- `controllers/` -- HTTP endpoints
- `static/` -- JS, CSS/SCSS, images, and web assets

### Decision Priority

The decision order for meeting any requirement is strict:

1. **Odoo core configuration** -- use built-in features, settings, system parameters.
2. **OCA addon** -- use a maintained community addon from a vetted OCA repository.
3. **Configuration / data / templates** -- solve with data records, automation rules, view inheritance, or server actions when no code is required.
4. **IPAI custom module** -- write a thin `ipai_<domain>_<feature>` module only when the above three options are genuinely insufficient.

### Naming Convention

All custom modules follow the pattern:

```
ipai_<domain>_<feature>
```

Examples: `ipai_finance_ppm`, `ipai_ai_tools`, `ipai_auth_oidc`, `ipai_bir_compliance`.

---

## 2. Runtime Architecture

### Canonical Runtime

| Component | Target |
|-----------|--------|
| Compute | Azure Container Apps (ACA) |
| Ingress / WAF | Azure Front Door |
| Database | PostgreSQL 16 on Azure Flexible Server (`pg-ipai-odoo`) |
| Observability | Azure-native (Application Insights, Log Analytics) |
| Identity | Managed identity / keyless auth where supported |

ACA is the default compute surface. The platform is **not** VM-first. VM / VMSS is an alternate self-managed hosting model only and is not the current default.

### Why ACA

- AI sidecars, background jobs, and platform bridges fit ACA naturally as separate containers or apps within the same environment.
- Scale-to-zero and per-revision deployment support efficient staging and preview workflows.
- Front Door provides global ingress, TLS termination, WAF, and routing without self-managed nginx.

### Database Environments

| Database | Purpose | Notes |
|----------|---------|-------|
| `odoo_dev` | Local development only | Never deployed, never hardcoded in Dockerfiles |
| `odoo_staging` | Staging | Pre-production validation |
| `odoo` | Production | System of record |
| `test_<module>` | Disposable test databases | Created and destroyed per test run, never shared |

Database names are runtime arguments, not baked configuration. Never hardcode a database name in a Dockerfile or image.

Runtime doctrine is confirmed by active Azure inventory including ACA environments, Front Door, PostgreSQL Flexible Server, Key Vault with private endpoints, and Foundry resources.

---

## 3. AI Architecture

### Service-Plane Split

| Plane | Owner | Role |
|-------|-------|------|
| Operational SoR | Odoo | Transactional business data, workflows, ERP truth |
| AI / Agent plane | Microsoft Foundry | Model governance, agent orchestration, evaluation |
| Analytics | Databricks | Unity Catalog, DLT pipelines, BI data products |

AI is an **adjacent capability lane**, not the transactional system of record.

### Canonical AI Control Plane

Microsoft Foundry (`ipai-copilot` project) is the canonical AI control plane.

Use Foundry for:

- Model selection and deployment governance
- Agent-oriented AI project structure
- Evaluation and experiment-oriented AI workflows
- Standardized access to Azure AI capabilities through the Foundry SDK or CLI

### Canonical AI Runtime Pattern

- **Azure Container Apps** for AI sidecars, copilot services, and agent runtimes
- **Azure AI Search** for retrieval when needed
- **Managed identity / keyless auth** where supported
- Foundry or Azure AI services for model execution

### AI Lane Separation Rules

- AI failure must not block core ERP transactions.
- Core business records remain Odoo-owned.
- Retrieval indexes, prompt state, and agent state must not redefine ERP truth.
- AI outputs are assistive until explicitly committed by approved business logic.
- Model selection must remain environment-driven and replaceable. Do not hardcode around a single model family.

---

## 4. Auth and Integrations

### Decision Order

1. **Odoo core auth / documented provider setup** -- use what ships with Odoo CE.
2. **Provider configuration and system parameters** -- configure, do not code.
3. **OCA addon** -- use a maintained extension if one exists.
4. **IPAI bridge** -- only for Azure/Foundry/runtime-specific behavior not cleanly covered by the above.

### Odoo Native Auth Capabilities

Odoo CE natively supports the following authentication and integration surfaces. Do not wrap these in custom modules:

- Azure sign-in (OAuth provider)
- Google sign-in (OAuth provider)
- Facebook sign-in (OAuth provider)
- LDAP authentication
- Two-factor authentication (2FA / TOTP)
- Outlook / Azure OAuth for mail and calendar

### IPAI Bridges -- Justified

IPAI bridge modules are justified when the requirement is specific to the Azure/ACA/Foundry runtime and is not covered by Odoo core or OCA:

- **ACA / proxy / Front Door** -- header normalization, ingress trust, proxy-aware URLs
- **Entra / OIDC** -- enterprise OIDC flows, conditional access, MFA policy enforcement beyond basic OAuth
- **Document Intelligence** -- Azure Document Intelligence (OCR) integration for invoice/receipt extraction
- **Copilot / agent orchestration** -- Foundry-connected AI bridge logic
- **PH-specific domain logic** -- BIR compliance, localization rules not covered by `l10n_ph`

### IPAI Bridges -- Not Justified

Do not create IPAI modules to replace:

- Generic authentication already provided by Odoo core
- Generic integrations (mail, calendar, contacts) already provided by Odoo core
- CE/OCA-covered workflows (accounting, CRM, project, inventory, etc.)
- Seed data, demo data, or data-loader concerns (these are fixtures, not capability)

---

## 5. Testing Doctrine

The platform uses a three-layer quality stack. Each layer has a distinct authority and none replaces another.

### Layer 1: Odoo-Native Tests -- Correctness Authority

Odoo-native tests are the first and mandatory layer. Every business behavior must have an Odoo-native test before any browser-level test is added.

| Test class | Use for |
|------------|---------|
| `TransactionCase` | Model logic, computed fields, constraints, business rules |
| `TransactionCase` + `Form` | Form behavior, onchange triggers, field defaults, save/load cycles |
| `HttpCase` + tours | Browser/webclient flows, RPC calls, login flows, menu navigation |
| Hoot / `web` test helpers | JS-only behavior, widget rendering, client-side logic |
| `assertQueryCount` | Performance-sensitive ORM paths, N+1 detection |

### Layer 2: Playwright -- Browser Regression Authority

Playwright supplements Odoo-native tests with cross-browser regression coverage.

Owns:

- Cross-browser rendering validation (Chromium, Firefox, WebKit)
- Page load smoke tests
- Settings open/save flows
- Menu and client action stability
- Screenshot and trace capture for regression evidence
- CLI-driven and MCP/agent-friendly test workflows

Does not own:

- Business logic correctness (that is Layer 1)
- ORM behavior or access rule enforcement (that is Layer 1)

### Layer 3: Chrome DevTools MCP -- Interactive Browser Debugging Authority

Chrome DevTools MCP is used for interactive investigation, not automated regression.

Owns:

- Network waterfall inspection
- JS console error triage
- DOM state during failure
- Performance profiling
- Runtime debugging during development

Does not own:

- Automated regression coverage (that is Layers 1 and 2)
- CI gating (that is Layers 1 and 2)

### Supplementation Rule

Playwright and Chrome DevTools MCP **supplement** Odoo-native tests. They never replace them. Every browser regression must have an Odoo-native test that proves the server-side behavior is correct before a Playwright test is added to cover the browser surface.

---

## 6. IPAI Custom Boundary

### Keep Narrow

The following categories justify IPAI custom modules:

| Category | Example |
|----------|---------|
| ACA / proxy / Front Door bridges | Header normalization, `web.base.url` proxy awareness, ingress trust |
| Entra / OIDC bridge | Enterprise OIDC, conditional access enforcement |
| Document Intelligence bridge | Azure Document Intelligence for invoice/receipt OCR |
| Copilot / agent orchestration bridge | Foundry-connected AI tools, agent routing, retrieval bridge |
| PH-specific domain logic | BIR compliance, PH tax localization, PH payroll rules |

### Do Not Broaden

The following do not justify IPAI custom modules:

| Anti-pattern | Why |
|--------------|-----|
| Generic auth wrappers | Odoo core handles OAuth, LDAP, 2FA natively |
| Generic integration wrappers | Odoo core handles mail, calendar, contacts natively |
| CE/OCA-covered workflows | Accounting, CRM, project, inventory are CE/OCA territory |
| Seed / demo / data-loader modules | These are fixtures, not capability; they must not be counted as parity |
| Broad "enterprise bridge" bundles | Unrelated integrations must not be bundled into a single module |

### Required Properties for Any New IPAI Module

Every new IPAI module must demonstrate:

1. Bounded scope -- one clear purpose
2. Explicit failure isolation -- ERP transactions still work if the module fails
3. Configuration indirection -- no hardcoded endpoints, models, or credentials
4. Scenario-level validation -- tests or UAT proof
5. Clear separation between assistive output and committed ERP state

---

## 7. Current Runtime State Evidence

The current Azure runtime inventory confirms this platform is deployed as:

- **Azure Container Apps**: Two environments (`ipai-odoo-dev-env`, `ipai-odoo-ha-env`) each with web, worker, and cron apps
- **Azure Front Door** (`afd-ipai-dev`): Edge/ingress for all public traffic
- **Azure Database for PostgreSQL Flexible Server** (`pg-ipai-odoo`): Private-endpoint-attached, managed database
- **Azure Key Vault** (`kv-ipai-dev`): Secret storage with private endpoint and private DNS
- **Application Insights** (`ipai-appinsights`) + **Log Analytics** (`la-ipai-odoo-dev`): Telemetry and log aggregation
- **Alert rules**: `alert-aca-high-cpu`, `alert-aca-no-replicas`, `alert-aca-restarts`, `alert-http-5xx`
- **Microsoft Foundry** (`ipai-copilot-resource` / `ipai-copilot` project): Active AI control plane
- **ACA sidecars/bridges**: `ipai-copilot-gateway`, `ipai-ocr-dev`, `ipai-mcp-dev`, `ipai-odoo-connector`
- **Container App Job**: `ipai-build-agent` for CI/CD build operations

This doctrine is based on active runtime state, not only intended architecture.

---

## 8. Deprecated Stack

The following items are permanently deprecated. Never reintroduce them.

| Deprecated Item | Replacement | Date |
|-----------------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| Supabase (all instances) | Azure-native services | 2026-03-26 |
| Cloudflare DNS | Azure DNS (delegated from Squarespace) | 2026-03 |
| DigitalOcean (all) | Azure (ACA + VM + managed PG) | 2026-03-15 |
| Mailgun (`mg.insightpulseai.com`) | Zoho SMTP (`smtp.zoho.com:587`) | 2026-03-11 |
| Vercel deployment | Azure Container Apps | 2026-03-11 |
| Wix (all -- hosting, CMS, DNS, API) | Azure DNS + Azure Container Apps + Odoo CMS | 2026-04-02 |
| Mattermost (all) | Slack | 2026-01-28 |
| `ipai_ai_widget` (global patches) | Native Odoo 18 Ask AI + `ipai_ai_copilot` | 2026-03-09 |
| `ipai-odoo-dev-pg` (old PG instance) | `pg-ipai-odoo` (Azure Flexible Server) | 2026-03 |
| Superset (as primary BI) | Power BI (primary) + Superset (supplemental only) | 2026-04 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |
| Public nginx edge | Azure Front Door | 2026-03-15 |
| Self-hosted runners | GitHub-hosted / Azure DevOps pool | 2026-03-15 |
| Appfine (all) | Removed | 2026-02 |

---

*This document consolidates decisions from Odoo upstream documentation, Azure platform documentation, Microsoft Foundry documentation, Playwright documentation, and Chrome DevTools documentation review. It is the single canonical doctrine reference for platform-level architectural decisions.*
