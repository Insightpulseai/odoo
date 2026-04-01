# Target Org Repo Map

> **SSOT**: `ssot/governance/org-repo-target-state.yaml`
> **Status**: Target state (not current live state)
> **Last updated**: 2026-03-30

## Deprecated Surfaces (Never Reintroduce)

| Surface | Replaced By | Date |
|---------|-------------|------|
| Cloudflare (DNS/WAF) | Azure DNS + Azure Front Door | 2026-03-26 |
| nginx (edge) | Azure Front Door | 2026-03-15 |
| Supabase (all) | Azure-native services | 2026-03-26 |
| n8n (automation) | Azure-native jobs | 2026-03-28 |
| DigitalOcean | Azure | 2026-03-15 |
| Vercel | Azure Container Apps | 2026-03-11 |
| Mailgun | Zoho SMTP | 2026-03-11 |

---

## Core Backbone (12 repos)

### `.github`

Org-wide GitHub governance, reusable automation, repo standards, and bootstrap templates.

```
.github/
├── .github/
│   ├── actions/{policy-check,setup-python,docs-sync}
│   ├── workflows/{org-governance,reusable-ci,reusable-release}.yml
│   ├── ISSUE_TEMPLATE/
│   ├── profile/README.md
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/{governance,standards,runbooks}
├── repo-templates/{service,docs-site,oss}
├── scripts/{bootstrap,checks,org}
├── spec/github-governance/
└── ssot/{policies,rulesets,workflows}
```

**Owns**: org policy, reusable workflows/actions, repo templates, community profile
**Does not own**: repo-specific CI, runtime code, product logic

---

### `odoo`

Transactional system of record built on Odoo CE + OCA with thin IPAI bridge modules only.

```
odoo/
├── .github/workflows/
├── addons/
│   ├── oca/{account_*,stock_*,hr_*}
│   ├── ipai/{ipai_meta,ipai_bridge_*,ipai_connector_*}
│   └── local/{sandbox_*,experimental_*}
├── config/{dev,staging,prod}/{odoo.conf,env.example}
├── docker/{compose,images,init}
├── docs/{architecture,runbooks,evidence}
├── evidence/{runtime,migrations,releases}
├── scripts/{ci,dev,odoo,azure}
├── spec/{odoo-runtime,copilot,finance}
├── ssot/odoo/{addons.manifest.yaml,oca-baseline.yaml,runtime-identifiers.json}
└── tests/{contract,integration,smoke}
```

**Owns**: ERP runtime, Odoo addons, OCA curation, IPAI bridge modules, config, migration scripts
**Does not own**: agent runtime, lakehouse, web frontend, infrastructure IaC

---

### `platform`

Shared control-plane applications, contracts, APIs, and operator surfaces.

```
platform/
├── .github/workflows/
├── apps/{control-plane,admin-console,ops-portal}/{app,tests}
├── packages/{contracts,sdk,shared-ui}
├── services/{api,workers,identity-bridge}
├── docs/{architecture,runbooks,adr}
├── scripts/{ci,release,ops}
├── spec/{control-plane,identity,governance}
├── ssot/{contracts,config,policies}
└── tests/{contract,integration,smoke}
```

**Owns**: control plane, admin console, ops portal, internal APIs, shared SDK, shared UI, cross-plane contracts, identity bridge, metadata/registry APIs
**Does not own**: deployable agent runtime (`agent-platform`), agent definitions/skills/judges (`agents`), Odoo runtime, lakehouse, public web

---

### `data-intelligence`

Databricks-centered governed lakehouse, semantic models, and analytics delivery plane.

```
data-intelligence/
├── .github/workflows/
├── bundles/{jobs,pipelines,workflows}
├── notebooks/{ingestion,curation,semantic}
├── models/{metrics,marts,serving}
├── schemas/{bronze,silver,gold}
├── docs/{architecture,runbooks,data-products}
├── scripts/{validation,release,bootstrap}
├── spec/{lakehouse,semantic-layer,governance}
├── ssot/{catalogs,contracts,jobs}
└── tests/{data-quality,contract,smoke}
```

**Owns**: lakehouse, governed data products, semantic layer, Databricks bundles, analytics SQL
**Does not own**: Odoo runtime, web frontend, agent runtime, infrastructure IaC

---

### `agent-platform`

Deployable runtime and orchestration plane for agent execution, tool routing, evaluation runtime hooks, and telemetry.

```
agent-platform/
├── .github/workflows/
├── runtimes/{orchestrator,executor,checkpointing,gateways}
├── services/{runtime-api,worker-manager,eval-runner,telemetry-bridge}
├── packages/{runtime-sdk,tracing,adapters}
├── configs/{dev,staging,prod}
├── docs/{architecture,runbooks,adr}
├── scripts/{ci,release,ops}
├── spec/{runtime,orchestration,observability}
├── ssot/{runtime,routing,policies}
└── tests/{contract,integration,smoke}
```

**Owns**: agent orchestration engine, execution workers, runtime gateways, scheduler/executor loops, state/checkpointing, eval execution hooks, runtime telemetry/tracing, Foundry integration
**Does not own**: canonical skill docs (`agents`), persona definitions (`agents`), judge definitions (`agents`), business/control-plane UI (`platform`), generic shared APIs (`platform`)

---

### `web`

Customer-facing and operator-facing web experiences, shared UI packages, and edge delivery surfaces.

```
web/
├── .github/workflows/
├── apps/{marketing,product,landing-redirect}/{app,tests}
├── packages/{ui,brand,content}
├── edge/{redirects,headers,middleware}
├── docs/{architecture,design,runbooks}
├── scripts/{ci,preview,release}
├── spec/{marketing,portals,content}
├── ssot/{routes,seo,content-model}
└── tests/{e2e,accessibility,smoke}
```

**Owns**: marketing site, product portals, shared UI packages, edge config, SEO
**Does not own**: Odoo runtime, agent runtime, infrastructure IaC

---

### `infra`

Azure-native infrastructure as code, DNS, identity, observability, and platform policy.

```
infra/
├── .github/workflows/
├── azure/{foundations,workload,identity,dns,front-door}
├── github/{oidc,runners,policies}
├── observability/{monitor,alerts,dashboards}
├── env/{dev,staging,prod}
├── docs/{architecture,runbooks,evidence}
├── scripts/{plan,apply,validate}
├── spec/{landing-zone,identity,observability}
└── ssot/{topology,inventory,policies}
```

**Owns**: Azure IaC, Azure DNS, Front Door config, Key Vault, OIDC federation, observability, runner pools
**Does not own**: application code, Odoo modules, agent logic, web frontend
**Deprecated**: Cloudflare (→ Azure DNS), nginx (→ Front Door), DigitalOcean (→ Azure)

---

### `automations`

Scheduled and event-driven automation jobs with explicit connectors, contracts, and runbooks.

```
automations/
├── .github/workflows/
├── jobs/{scheduled,event-driven,maintenance}
├── connectors/{github,azure,odoo}
├── runbooks/{ops,finance,marketing}
├── docs/{architecture,runbooks,evidence}
├── scripts/{bootstrap,validate,release}
├── spec/{scheduled-jobs,event-automation,retry-policy}
├── ssot/{schedules,connectors,contracts}
└── tests/{contract,integration,smoke}
```

**Owns**: scheduled jobs, event-driven triggers, connectors, ops runbooks
**Does not own**: Odoo runtime, agent runtime, infrastructure IaC
**Deprecated**: n8n (→ Azure-native jobs)

---

### `agents`

Canonical registry of agents, skills, judges, evals, schemas, and workflow samples.

```
agents/
├── .github/workflows/
├── .claude/{commands,skills,agents}     # operator overlay
├── .mcp.json                            # tool connectors
├── personas/{odoo_sh,platform,cross-functional}
├── skills/{odoo,azure,release,governance}
├── judges/{odoo,runtime,release}
├── evals/{suites,fixtures,reports}
├── schemas/{agent,skill,judge,workflow}
├── agent-samples/
├── workflow-samples/
├── registry/
├── docs/{architecture,concepts,runbooks}
├── spec/{registry,evals,governance}
└── ssot/{manifests,routing,policies}
```

**Owns**: personas, skill definitions, judge rubrics, eval suites, agent schemas, agent manifests, routing maps, workflow samples
**Does not own**: deployable runtime services (`agent-platform`), long-lived APIs (`platform`), operator UI (`platform`), infrastructure

---

### `design`

Brand tokens, component mappings, assets, and design-to-code contracts.

```
design/
├── .github/workflows/
├── tokens/{core,semantic,brand}
├── components/{web,marketing,odoo}
├── assets/{logos,icons,illustrations}
├── docs/{guidelines,patterns,handoff}
├── exports/{figma,codegen,previews}
├── spec/{brand-system,component-library,token-governance}
└── ssot/{tokens,mappings,policy}
```

**Owns**: design tokens, component mappings, brand assets, Figma exports, handoff specs
**Does not own**: runtime UI code (`web` repo), Odoo theme code (`odoo` repo)

---

### `docs`

Cross-repo architecture, governance, runbooks, evidence, and strategic operating model documentation.

```
docs/
├── .github/workflows/
├── architecture/{platform,repo,adr}
├── governance/{policy,standards,evidence}
├── runbooks/{ops,release,incident}
├── strategy/{okr,roadmap,portfolio}
├── templates/{adr,runbook,evidence-pack}
├── spec/{docs-governance,evidence-model,architecture-index}
└── ssot/{indexes,contracts,freshness}
```

**Owns**: cross-repo architecture, governance docs, ADRs, runbooks, evidence policy, strategy
**Does not own**: repo-specific docs (each repo owns its own `docs/`), runtime code

---

### `templates`

Reusable starter kits and scaffolds for repos, specs, docs, automations, and design artifacts.

```
templates/
├── .github/workflows/
├── repo/{service,library,docs-site}
├── spec/{prd,plan,tasks}
├── automation/{workflow,issue,adr}
├── design/{deck,proposal,one-pager}
├── docs/{usage,standards,migration}
├── tests/{template-contract,render}
└── ssot/{catalog,versions,policy}
```

**Owns**: repo scaffolds, spec templates, automation templates, design deck templates
**Does not own**: instantiated repos, live specs, runtime code

---

## Satellite Repos

| Repo | Purpose | Target |
|------|---------|--------|
| `landing.io` | Public redirect shell | Fold into `web/apps/landing-redirect` or keep standalone |
| `ugc-mediaops-kit` | Public OSS media ops toolkit | Keep standalone, not core backbone |

---

## Three-Way Boundary Doctrine

```
If it runs as a deployable service → agent-platform
If it defines how an agent should think, act, evaluate, or route → agents
If it is shared control-plane or operator-facing product surface → platform
```

### `platform` vs `agent-platform` vs `agents`

| Concern | `platform` | `agent-platform` | `agents` |
|---------|-----------|-------------------|----------|
| Control-plane apps | Yes | No | No |
| Admin/operator UI | Yes | No | No |
| Shared APIs / SDK | Yes | No | No |
| Identity bridge | Yes | No | No |
| Cross-plane contracts | Yes | No | No |
| Orchestration engine | No | Yes | No |
| Execution workers | No | Yes | No |
| Runtime gateways | No | Yes | No |
| State/checkpointing | No | Yes | No |
| Eval execution hooks | No | Yes | No |
| Telemetry/tracing | No | Yes | No |
| Foundry integration | No | Yes | No |
| Personas | No | No | Yes |
| Skill definitions | No | No | Yes |
| Judge rubrics | No | No | Yes |
| Eval suites (content) | No | No | Yes |
| Agent schemas | No | No | Yes |
| Agent manifests | No | No | Yes |
| Routing maps | No | No | Yes |
| Samples/examples | No | No | Yes |
| `.claude/` overlay | Optional | Optional | Yes |

**Summary**: `platform` = product surface. `agent-platform` = engine. `agents` = catalog.

---

## Repo Completeness Gate

A repo is "done" when it has:

- `README.md` — answers: what it owns, what it doesn't, authoritative files, validation, evidence
- `.github/workflows/` — CI/CD
- `docs/` — repo-specific documentation
- `spec/` — spec bundles
- `ssot/` — machine-readable truth
- `scripts/` — executable truth
- `tests/` — contract enforcement
- `<repo-native domain directories>` — actual product/runtime code

---

## File Extension Policy

See `ssot/governance/org-repo-target-state.yaml` for the full org-wide policy.

| Category | Extensions | Role |
|----------|-----------|------|
| Authoritative docs | `.md` | README, docs, ADRs, runbooks, specs |
| Authoritative contracts | `.yaml`, `.json` | SSOT, manifests, machine-readable truth |
| Authoritative diagrams | `.drawio` | Editable diagrams (exported as `.png`) |
| Executable truth | `.py`, `.sh`, `.ts`, `.sql`, `.tf`, `.bicep` | Runtime, scripts, IaC |
| Never committed | `.env`, `.pem`, `.key` | Secrets — Key Vault only |
