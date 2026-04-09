# Cloud Adoption Strategy — Odoo on Azure (Future Target State)

> CAF-aligned strategy with OKR operating model.
> Repo naming: control-plane, agent-platform, data-intelligence.

---

## Mission Statement

Build and operate a secure, governed, repeatable Azure-native business platform where:
- **odoo** = ERP and transactional system of record
- **control-plane** = enterprise orchestration and registry layer
- **agent-platform** = AI and copilot execution layer
- **data-intelligence** = governed analytics and intelligence layer

All delivered through standardized Azure landing zones and a product-oriented operating model.

## What Must Be True When Migration Is Done

1. **Azure landing zones are the permanent foundation** — identity, connectivity, governance, security, observability inherited, not rebuilt per workload
2. **Odoo is the production ERP core on Azure** — not partial, not transitional
3. **Shared management operating model** — platform teams own foundation, workload teams operate within guardrails
4. **Responsibilities assigned to named owners** — governance, security, management, workload operation documented
5. **Product model, not project model** — durable ownership, not fragmented handoffs

## Target Repo Model (L2)

| Repo | Role | CAF Mapping |
|------|------|-------------|
| `.github` | Org governance, reusable CI | Shared governance |
| **`control-plane`** | Registry, orchestration, catalog, tenants | Platform services |
| **`infra`** | Landing zones, networking, identity, policy | Platform foundation |
| **`odoo`** | ERP transactional core | Application workload |
| **`agent-platform`** | Foundry agents, tools, policies, evals | Application workload |
| **`data-intelligence`** | Databricks, Lakeflow, Apps, Unity Catalog | Application workload |
| **`web`** | Product surfaces, portals, docs | Application workload |
| **`automations`** | Jobs, workflows, scheduled execution | Application workload |
| `design-system` | Design tokens, components | Support |
| `templates` | Bootstrap scaffolds | Support |

## Annual OKR

**Objective**: Build a cloud-ready organization that operates Azure safely, repeatedly, and at scale.

| KR | Measure |
|----|---------|
| KR1 | Cloud operating model selected, documented, approved |
| KR2 | Governance/security/management owners named and documented |
| KR3 | Cloud skill gaps assessed, role-based enablement in execution |
| KR4 | Quarterly reviews with visible progress, blockers, corrections |

## Quarterly Team OKRs

### Platform Team
- Shared platform operating model approved
- Governance/security/management owners named
- Landing-zone prerequisites defined
- Environment provisioning path documented

### Workload Teams
- Workload owner identified per product
- Required cloud skills mapped per team
- Team onboarding checklist completed
- Platform↔workload handoff points agreed

### Leadership
- Cloud priorities published and leadership-approved
- Success measures agreed (resilience, speed, control)
- Monthly review active for decisions and blockers
- Cross-functional steering group operating

## Operating Model: Shared Management

### Platform team owns
- Governance baseline
- Identity baseline
- Connectivity baseline
- Management and observability baseline
- Landing-zone products
- Environment provisioning path

### Workload teams own
- Workload architecture
- Deployment readiness
- Service operation inside guardrails
- Application-level reliability and business outcomes

## Success Measures

| Dimension | Measure |
|-----------|---------|
| Resilience | RTO/RPO met, backup/restore rehearsed |
| Governance | Policy compliance %, named owners, audit evidence |
| Delivery speed | Time from commit to prod, deploy frequency |
| Business value | New AI/data capabilities enabled, ERP uptime |
| Operating model | Quarterly review cadence, team OKR completion |

## Repo Rename Plan

| Current Name | Target Name | Why |
|-------------|-------------|-----|
| `ops-platform` | **`control-plane`** | Clearer — this repo IS the control plane (registry, orchestration, catalog) |
| `agents` | **`agent-platform`** | Broader than "agents" — contains runtime, tools, policies, evals, middleware |
| `lakehouse` | **`data-intelligence`** | Broader than storage — includes Databricks Apps, domain products, streaming, AI/BI |

### Repos That Keep Their Names

`.github`, `infra`, `odoo`, `web`, `automations`, `design-system`, `templates`

### Repos to Delete (After Salvage)

`template-factory`, `plugin-marketplace`, `plugin-agents`, `learn`, `mcp-core`

---

## Language Policy

| Repo | Python | .NET | TypeScript | Why |
|------|--------|------|-----------|-----|
| **`agent-platform`** | ✓ Primary | **✓ Mandatory** | — | Aligned to microsoft/agent-framework dual-language design |
| **`control-plane`** | ✓ Primary | Optional | Optional | Default Python; .NET for Azure-native services if needed |
| **`automations`** | ✓ Primary | Optional | Optional | Default Python; .NET for durable workers if needed |
| `odoo` | ✓ Only | — | — | Odoo is Python-only |
| `data-intelligence` | ✓ Primary | — | — | Databricks is Python/SQL/Scala |
| `web` | — | — | ✓ Primary | Next.js/React is TypeScript |
| `infra` | ✓ Scripts | — | — | Bicep/Terraform + Python scripts |

### .NET Required Files (Where Mandatory/Optional)

```
global.json
NuGet.config
Directory.Build.props
Directory.Packages.props
<RepoName>.slnx
```

---

## agent-platform Target Structure (Aligned to microsoft/agent-framework)

```
agent-platform/
├── docs/
│   ├── architecture/
│   ├── runbooks/
│   └── agents/
├── spec/
│   └── agent-platform/
├── schemas/
│   ├── tool.schema.json
│   ├── agent.schema.json
│   └── workflow.schema.json
├── python/
│   ├── agents/
│   ├── workflows/
│   ├── tools/
│   ├── middleware/
│   ├── evals/
│   └── tests/
├── dotnet/
│   ├── src/
│   │   ├── AgentPlatform.Agents/
│   │   ├── AgentPlatform.Workflows/
│   │   ├── AgentPlatform.Tools/
│   │   ├── AgentPlatform.Middleware/
│   │   └── AgentPlatform.Runtime/
│   ├── tests/
│   └── samples/
├── agent-samples/
├── workflow-samples/
├── runtimes/
│   ├── foundry/
│   └── local/
├── policies/
│   ├── action-guards/
│   └── data-access/
├── adapters/
│   ├── mcp/
│   └── http/
├── apps/
│   └── copilot/
├── AgentPlatform.slnx
├── global.json
├── NuGet.config
├── Directory.Build.props
├── Directory.Packages.props
├── pyproject.toml
└── .github/
    └── workflows/
        ├── ci.yml
        ├── dotnet-ci.yml
        └── python-ci.yml
```

### Design Rationale

- `python/` and `dotnet/` at top level mirrors microsoft/agent-framework layout
- `schemas/` shared across both languages (contracts are language-agnostic)
- `agent-samples/` and `workflow-samples/` at top level for discoverability
- `runtimes/` separates Foundry-hosted from local execution
- `policies/` and `adapters/` are runtime-independent

---

## Canonical Source Mapping (Per Repo)

| Repo | Primary Benchmarks |
|------|-------------------|
| `.github` | `actions/starter-workflows`, GH org workflow templates, reusable workflows, secure use reference |
| `templates` | `github/spec-kit`, `microsoft/App-Templates`, `Azure-Samples/azd-template-artifacts`, `azd-ai-starter-basic` |
| `infra` | CAF tools/templates, Azure Landing Zone deploy guidance, Azure Architecture Center |
| `control-plane` | CAF planning/operating model, `azd-deployment-environments`, GH reusable workflows |
| `odoo` | Odoo 18 official docs, OCA development standards, OdooSH behavioral contract |
| `agent-platform` | `microsoft/agent-framework`, `azd-ai-starter-basic`, `Deploy-Your-AI-Application-In-Production`, `Microsoft-AI-Decision-Framework` |
| `data-intelligence` | Databricks docs, Lakeflow, Unity Catalog, Databricks Financial Services solution sheet |
| `web` | Fluent 2 design system, `microsoft/fluentui` (consumption patterns), azd full-stack templates |
| `automations` | n8n self-hosted patterns, Azure Functions, Logic Apps connectors |
| `design-system` | `microsoft/fluentui` (primary benchmark — tokens/themes/components/specs/starter-templates), Fluent 2 |

### Explicit Exclusions

- `foundry-rs/*` — Ethereum/Solidity toolchain, NOT Microsoft Foundry (naming collision)
- Viva Goals — retired December 31, 2025; keep OKR layer tool-agnostic
- Generic "awesome" repos — use for discovery only, not as canonical standards

---

## Short Version

> InsightPulseAI will complete its migration by operating Odoo as the Azure-hosted ERP core on standardized Azure landing zones, with clear separation between platform and workload services, automated and governed infrastructure, and a product-oriented operating model with measurable business outcomes.
