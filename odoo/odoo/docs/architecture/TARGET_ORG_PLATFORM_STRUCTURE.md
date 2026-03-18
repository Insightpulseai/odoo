# Target Org/Platform Structure

> SSOT: `ssot/repo/org_topology.yaml`

## 12 Repos, 8 Planes

```
.github/            governance        org-wide workflows, templates, rulesets
odoo/               transactional     ERP/runtime (Odoo CE + OCA + ipai bridges)
platform/           control           ops platform, Supabase backend, service catalog
data-intelligence/  intelligence      Databricks, governed data products, semantic/BI
agent-platform/     agent             Foundry runtime, tools, workflows, evals
web/                experience        websites, portals, browser extensions, UIs
infra/              substrate         Azure/Cloudflare IaC, landing zones, identity
automations/        automation        n8n, schedulers, jobs, workflow contracts
agents/             doctrine          personas, skills, judges, knowledge, evals
design/             visual            tokens, Figma exports, brand assets
docs/               documentation     cross-repo architecture, strategy, evidence
templates/          bootstrap         starter kits, repo templates
```

## Renames (current → target)

| Current | Target | Reason |
|---|---|---|
| `lakehouse` | `data-intelligence` | Scope is broader than lakehouse |
| `ops-platform` | `platform` | Expanded to full control plane |
| `design-system` | `design` | Shorter; design-system is internal folder |

## Hard ownership boundaries

- **odoo/** owns ERP transactions. Not OLAP, not agent runtime, not control plane.
- **platform/** owns control-plane state, Supabase, service registry. Not Odoo modules, not Databricks.
- **data-intelligence/** owns CDC, bronze/silver/gold, semantic BI, agent context datasets. Not ERP transactions.
- **agent-platform/** owns Foundry runtime, agent workflows, tools, evals. Not ERP SoR, not governed OLAP.
- **agents/** owns doctrine: personas, skills, judges, knowledge. Not runtime logic.
- **web/** owns all frontends including browser copilot extension. Not infra, not Odoo modules.

## Browser copilot placement

```
web/
  apps/browser-copilot-extension/
  apps/native-screen-bridge/
  packages/browser-agent-contract/
```

## Per-repo scaffold

Every repo follows this structure:

```
<repo>/
  CLAUDE.md                 # repo root index (NOT .claude/CLAUDE.md)
  .claude/rules/            # scoped enforcement rules
  .github/workflows/
  .mcp.json
  spec/
  docs/
  ssot/
  tests/
  scripts/
  apps/                     # if applicable
  packages/                 # if applicable
  .devcontainer/            # only repos that need one
```

## Naming conventions

| Level | Pattern | Example |
|---|---|---|
| Org repos | kebab-case | `agent-platform`, `data-intelligence` |
| Repo apps | kebab-case | `browser-copilot-extension`, `ops-console` |
| Shared packages | kebab-case, @ipai/ if published | `browser-agent-contract` |
| Odoo modules | snake_case with ipai_ | `ipai_finance_ppm` |
| Specs | kebab-case slug | `spec/oltp-olap-separation/` |
| Workflows | kebab-case.yml | `deploy-production.yml` |
| Claude rules | kebab-case.md | `.claude/rules/repo-topology.md` |

## Devcontainer policy

Only repos with a runtime need a devcontainer:

| Repo | Devcontainer | Runtime |
|---|---|---|
| odoo | Yes (exists) | Python 3.12 + PostgreSQL 16 + Redis 7 |
| web | Yes (create) | Node 22 + pnpm |
| platform | Yes (create) | Python 3.12 + Supabase CLI |
| agent-platform | Yes (create) | Python 3.12 + Foundry SDK |
| All others | No | Config/docs only — edit locally |
