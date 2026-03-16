# Org Repo SSOT Map — InsightPulseAI

> Canonical ownership map for all active repositories in the InsightPulseAI GitHub org.
> Each row defines what a repo owns, what it must not own, and where its boundaries are.
>
> Updated: 2026-03-08
> Source: Verified against actual repo contents post-restructuring (2026-03-07)

---

## Active Repos (9)

| Repo | Tier | Canonical Role | Owns | Must Not Own | Runtime/Deploy Plane | Key SSOT Paths |
|------|------|----------------|------|-------------|---------------------|----------------|
| `.github` | 0 | Org governance | Reusable workflows, PR/issue templates, org labels, org-wide agent configs, governance docs | Application code, runtime configs, secrets values, repo-specific workflows | N/A (governance only) | `.github/workflows/claude-code.yml`, `.github/workflows/claude-pr-review.yml`, `labels.json`, `docs/org/` |
| `odoo` | 1 | ERP runtime core | Odoo CE 19 + OCA + ipai_* modules, ERP Docker image, Odoo-specific CI, spec bundles, ERP config | Non-ERP web apps, Databricks assets, standalone agent runtimes, IaC for non-Odoo infra | Azure Container Apps → Azure PG Flexible (target); DO Droplet (current) | `addons/ipai/`, `addons/oca/`, `config/odoo/`, `docker/`, `spec/`, `CLAUDE.md` |
| `ops-platform` | 1 | Control-plane substrate | Supabase Edge Functions, migrations, ops.* tables, tenant registry, plan catalog, secrets metadata, boards/automation glue | ERP modules, Databricks pipelines, web UIs, raw IaC | Supabase (Edge Functions, Vault, Auth, Realtime) | `supabase/functions/`, `supabase/migrations/`, `policy/` |
| `lakehouse` | 1 | Data + AI platform | Databricks bundles, notebooks, jobs, pipelines, SQL, dashboards, ML models, serving endpoints, agents, Unity Catalog governance | ERP logic, web apps, infrastructure IaC, Odoo modules | Databricks on Azure (workspaces, compute, serving) | `databricks/bundles/`, `databricks/notebooks/`, `databricks/jobs/` |
| `infra` | 1 | Infrastructure as Code | Azure Bicep/Terraform, Cloudflare DNS, DO legacy configs, networking, observability foundations, Key Vault definitions, identity/policy | Application code, business logic, ERP modules, agent skills | Azure (all IaC targets), Cloudflare, DigitalOcean | `azure/modules/`, `azure/envs/`, `cloudflare/dns/`, `terraform/` |
| `agents` | 1 | Agent framework + MCP | Agent definitions, MCP server implementations, tool schemas, skill packs, prompt templates, agent orchestration, eval framework | ERP modules, web UIs, raw infrastructure, Databricks pipelines | Azure AI Foundry (target), GitHub Actions (CI) | `agents/`, `mcp-server/`, `tools/`, `skills/`, `prompts/` |
| `web` | 2/3 | Non-Odoo browser surfaces | Ops console, marketing site, docs site, customer portal, shared UI packages | ERP modules, Databricks assets, infrastructure IaC, agent definitions | Vercel (web apps, static sites) | `apps/console/`, `apps/marketing/`, `apps/docs/`, `packages/ui/` |
| `design-system` | 3 | Design tokens + components | Style Dictionary tokens, React/Tailwind components, icon pipeline, brand assets, Storybook | Application logic, infrastructure, ERP modules, agent code | npm registry (packages), Storybook (docs) | `tokens/`, `components/`, `icons/`, `brand/` |
| `templates` | 0 | Repo templates + scaffolds | OCA module scaffolds, Supabase starters, Next.js starters, Databricks templates, catalog | Runtime code, production configs, secrets, deployed services | N/A (template source only) | `oca/`, `supabase/`, `nextjs/`, `catalog.yaml` |

---

## Ownership Rules

### Environment ownership

Each repo may only define GitHub Environments for systems it deploys:

| Repo | Allowed Environments | Not Allowed |
|------|---------------------|-------------|
| `odoo` | `odoo-dev`, `odoo-staging`, `odoo-production` | `databricks-*`, `web-*`, `ops-console-*` |
| `lakehouse` | `databricks-dev`, `databricks-staging`, `databricks-production` | `odoo-*`, `web-*` |
| `web` | `web-preview`, `web-production`, `ops-console-preview`, `ops-console-production` | `odoo-*`, `databricks-*` |
| `infra` | `infra-dev`, `infra-production` (for Terraform apply) | `odoo-*`, `web-*` |
| `ops-platform` | `supabase-dev`, `supabase-production` | `odoo-*`, `databricks-*` |
| `.github` | None | All |
| `agents` | `agents-dev`, `agents-production` (if agent serving exists) | `odoo-*`, `databricks-*` |
| `design-system` | None (publish-only) | All |
| `templates` | None | All |

### Workflow ownership

A CI workflow belongs in the repo that:

1. Owns the code being built/tested/deployed
2. Has the secrets needed for that deployment
3. Defines the target environment

A workflow must **not** exist in a repo that does not own its deploy target.

### External system mapping

| External System | Primary Repo | Secondary |
|----------------|-------------|-----------|
| Odoo runtime | `odoo` | — |
| Supabase | `ops-platform` | — |
| Databricks | `lakehouse` | — |
| Azure IaC | `infra` | — |
| Cloudflare DNS | `infra` | — |
| Vercel | `web` | — |
| Azure AI Foundry | `agents` | — |
| GitHub org settings | `.github` | — |
| npm packages | `design-system` | `web` |

---

## Migration State

Most repos besides `odoo` and `agents` are scaffolds. Actual content has not yet migrated from the `odoo` monorepo.

| Repo | Content State | Content Currently In |
|------|--------------|---------------------|
| `ops-platform` | Scaffold (`supabase/config.toml` + `CLAUDE.md`) | `odoo/supabase/` |
| `lakehouse` | Scaffold (`CLAUDE.md` only) | `ssot/databricks/`, `odoo/work/databricks/`, `odoo/infra/databricks/` |
| `infra` | Scaffold (`CLAUDE.md` only) | `odoo/infra/azure/`, `odoo/infra/cloudflare/`, `odoo/infra/dns/` |
| `web` | Scaffold (`CLAUDE.md` only) | `odoo/web/`, `odoo/apps/ops-console/`, `odoo/platform/` |
| `design-system` | Scaffold (`CLAUDE.md` only) | `odoo/packages/design-tokens/`, `odoo/figma/` |
| `templates` | Scaffold (`CLAUDE.md` only) | `odoo/templates/`, `odoo/catalog/` |
| `agents` | Has real content | Own content (substantial — mcp-server, tools, skills, eval) |
| `.github` | Has real content | Own content (64 workflows, governance docs, agent configs) |

### Decomposition sequence

Content should migrate out of `odoo` in this order:

1. **`infra`** — DNS, Cloudflare, Azure IaC (cleanest boundary, fewest dependencies)
2. **`lakehouse`** — Databricks bundles, notebooks, warehouse SSOT
3. **`ops-platform`** — Supabase functions, migrations, vault definitions
4. **`web`** — ops-console, marketing site, docs site
5. **`design-system`** — tokens, brand assets, components
6. **`templates`** — scaffolds, catalog

Each migration step requires:
- Move content to target repo
- Update CI workflows (move relevant workflows, update paths)
- Delete moved content from `odoo`
- Update `PLATFORM_REPO_TREE.md` to reflect new locations

---

## Resolved Decisions

### `boards-automation` — Do not create

Azure Boards automation, control-plane glue, and cross-repo orchestration belong in `ops-platform`. No separate repo needed unless independent lifecycle, access, or deployment is required.

### `platform` vs `ops-platform` — Keep `ops-platform`

`ops-platform` is already real, more specific, and correctly signals "control plane / operations substrate." A rename to `platform` is aesthetic and would require updating all references across 9 repos. Not worth it unless a full org-wide rename pass is underway.

---

## Archived Repos (13)

All archived 2026-03-07. Content migrated or abandoned.

| Repo | Reason | Content Destination |
|------|--------|-------------------|
| `template-factory` | Empty (no default branch) | `templates` |
| `plugin-marketplace` | Scaffold-only | Abandoned |
| `plugin-agents` | Scaffold-only | `agents` |
| `dev-environment` | Archived | Content split to `web`, `design-system`, `infra` |
| `ops-console` | Empty (no default branch) | `web/apps/console/` |
| `app-crm` | Empty (no default branch) | Abandoned (Odoo CRM module covers this) |
| `learn` | Archived | Content to `odoo/docs/` or `lakehouse/docs/` |
| `mcp-core` | Migrated | `agents/mcp/` |
| `fin-ops` | Empty | `ops-platform` if needed |
| `app-landing` | Empty | `web/apps/marketing/` |
| `roadmap` | 1 commit | GitHub Projects |
| `demo-repository` | Demo/test | Abandoned |
| `fluent-owl` | Pre-restructuring | `design-system` if relevant |

---

## Azure Boards Mapping

| Azure Boards Project | Primary Repo | Secondary Repos |
|---------------------|-------------|----------------|
| `erp-saas` | `odoo` | — |
| `lakehouse` | `lakehouse` | — |
| `platform` | `ops-platform` | `agents`, `infra`, `web` |

---

## Stale SSOT Files

The following files reference pre-restructuring repo names and need updating:

| File | Issue |
|------|-------|
| `ssot/github/org_repos.yaml` | References archived repos (`template-factory`, `mcp-core`, `dev-environment`, etc.), missing current repos (`lakehouse`, `web`, `design-system`, `templates`) |
| `ssot/github/desired-end-state.yaml` | May reference old repo names |

These should be updated to match this map as the canonical source.
