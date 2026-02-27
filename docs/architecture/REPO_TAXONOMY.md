# Insightpulseai Organization Repository Taxonomy

## 1. Enterprise vs. Org Responsibility Split

- **`Dataverse` (Enterprise account) — Governance Layer**:
  - Enforces org-wide controls: SSO/SCIM, 2FA requirements.
  - Policies: Repo creation rules, Actions policy, secret scanning, code scanning.
  - Central billing & license management, audit log, and security center.
  - _Rule_: Enterprise owns policy. It is not for day-to-day code execution.
- **`Insightpulseai` (Org) — Engineering Execution Layer**:
  - Houses all repos, teams, CODEOWNERS, branch protection, shared templates in `.github/`.
  - Holds spec/ governance, linting, and platform SSOT.

## 2. Repo Taxonomy

### Tier A — Hard SSOT Repos (Foundational)

1. **`platform`**: Supabase SSOT / control plane (migrations, functions, RLS/RPC).
2. **`odoo`**: ERP runtime SSOT (addons, config, docker/compose, OCA manifest).
3. **`design`**: Design tokens SSOT (tokens.json, figma pull scripts).
4. **`infra`**: IaC + drift enforcement SSOT (DNS, Vercel config, Actions org policies).
5. **`.github`**: Org governance SSOT (default workflows, PR templates, Spec Kit enforcement, CODEOWNERS).

### Tier B — Product Surfaces (Apps)

6. **`web`**: All Vercel-deployed frontends (`apps/*` + `packages/*` UI libs).
7. **`agents`**: Agent registry, skills, MCP runbooks.

### Tier C — Satellite Repos

Only exist if separation significantly reduces blast radius. Otherwise, fold into `platform` or `agents`.

## 3. Recommended Canonical Structure Examples

- **`odoo`**: `addons/{odoo,oca,ipai}`, `config/{dev,staging,prod}`, `docker/`, `spec/`
- **`platform`**: `supabase/{migrations,functions,seed.sql,config.toml}`, `packages/`, `spec/`
- **`web`**: `apps/`, `packages/{ui,config,sdk}`, `spec/`
- **`design`**: `tokens/`, `figma/`, `assets/`, `mapping/`

## 4. Pinned Repositories (Max 6)

Pin the following repos to the org profile for clarity:

- `platform`
- `odoo`
- `web`
- `design`
- `infra`
- `agents`

## 5. Team Ownership Model (CODEOWNERS)

Team boundaries dictate code ownership to prevent repo sprawl from becoming ownership sprawl:

- `@Insightpulseai/erp-odoo` → owns `odoo/**`
- `@Insightpulseai/platform-supabase` → owns `platform/supabase/**`
- `@Insightpulseai/web-product` → owns `web/apps/**`, `web/packages/ui/**`
- `@Insightpulseai/design-systems` → owns `design/**`
- `@Insightpulseai/infra-devops` → owns `infra/**`, `.github/workflows/**`
- `@Insightpulseai/agents-ai` → owns `agents/**`, `skills/**`
