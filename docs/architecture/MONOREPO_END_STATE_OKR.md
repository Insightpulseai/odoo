# Monorepo End-State OKR — InsightPulse AI

> **Vision**: A single git repository is the authoritative source of truth for all infrastructure,
> code, configuration, and documentation that runs InsightPulse AI's products and services.
>
> **Mission**: Eliminate shadow configuration, reduce deployment friction, and enforce
> domain/service boundaries through code — not convention.

---

## O1: Single-Repo SSOT

**Objective**: Zero authoritative sources of truth outside this repository.

| Key Result | Target | Measure |
|-----------|--------|---------|
| KR1.1 | 0 Cloudflare DNS records not covered by `infra/dns/subdomain-registry.yaml` | CI drift gate passes |
| KR1.2 | 0 n8n workflows not exported to `automations/n8n/workflows/` | Sweep script reports 0 stray |
| KR1.3 | 0 Supabase schema changes outside migration files | `supabase db diff` clean on main |
| KR1.4 | 0 Vercel project settings not reflected in `vercel.json` | Manual audit monthly |

---

## O2: Odoo 19 CE + OCA Feature Parity

**Objective**: ≥80% Enterprise Edition feature parity via CE + OCA + ipai_* modules.

| Key Result | Target | Measure |
|-----------|--------|---------|
| KR2.1 | ≥80% of EE features mapped in `ssot/parity/ee_to_oca_matrix.yaml` | Matrix row count ≥ threshold |
| KR2.2 | 0 `odoo.enterprise` imports in `addons/ipai/` | CI lint gate (`ee-parity-gate.yml`) |
| KR2.3 | All EE gaps addressed by OCA module OR documented bridge | Matrix `gap_type` column complete |
| KR2.4 | Bridge contracts exist for all active IPAI bridges | `ssot/bridges/catalog.yaml` + `docs/contracts/` |

---

## O3: Domain Lock — *.insightpulseai.com Only

**Objective**: All external-facing services resolve under `*.insightpulseai.com`. No `.net`, no `.vercel.app` in canonical references.

| Key Result | Target | Measure |
|-----------|--------|---------|
| KR3.1 | 0 references to `insightpulseai.net` in non-archived files | `domain-lint.yml` CI gate |
| KR3.2 | 0 `.vercel.app` URLs in `docs/`, `spec/`, `CLAUDE.md` | `domain-lint.yml` CI gate |
| KR3.3 | All subdomains listed in `ssot/domains/insightpulseai.com.yaml` | SSOT compliance check |
| KR3.4 | Cloudflare Terraform plan shows no drift on merge to main | `cloudflare-dns-drift.yml` |

---

## O4: Zero-Touch Staging → Production Promotion

**Objective**: Any change merged to `main` can be promoted to production via CI — no manual console steps.

| Key Result | Target | Measure |
|-----------|--------|---------|
| KR4.1 | Odoo container update deployable via single `gh workflow run` | `deploy-odoo.yml` workflow exists |
| KR4.2 | Supabase migrations auto-applied on merge via CI | `supabase-migrate.yml` passes on main |
| KR4.3 | n8n workflow deployments idempotent and scriptable | `deploy_n8n_all.py --apply` works |
| KR4.4 | Go-live checklist automated to ≥70% | `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` |

---

## Canonical Repo Tree (Boundary Rules)

```
/
├── addons/
│   ├── odoo/          # Core Odoo CE addons (read-only, git submodule)
│   ├── oca/           # OCA modules (read-only submodules — never edited directly)
│   └── ipai/          # Custom IPAI modules (ipai_<domain>_<feature>/)
├── apps/              # Standalone applications (Next.js, etc.)
├── automations/       # n8n workflows (JSON exports = SSOT)
├── docs/              # All documentation (architecture, runbooks, evidence)
├── infra/             # Infrastructure as Code (Terraform, DNS, Docker)
├── packages/          # Shared packages (monorepo)
├── platform/          # Platform-level shared code (AI providers, utils)
├── scripts/           # Automation and CI scripts
├── spec/              # Spec Kit bundles (one per feature)
├── ssot/              # SSOT registries (domains, secrets, parity, bridges)
└── supabase/          # Supabase functions and migrations
```

**Boundary rules**:
- `addons/oca/` — read-only; create `ipai_*` override modules instead
- `docs/evidence/` — derived proof, not SSOT; canonical at `web/docs/evidence/`
- `ssot/` — identifier registries only; never contains secret values
- `infra/cloudflare/` — generated from `infra/dns/subdomain-registry.yaml`; do not hand-edit

---

## Domain Map

All external services MUST resolve under `*.insightpulseai.com`:

| Subdomain | Service | Stack |
|-----------|---------|-------|
| `erp` | Odoo CE 19 | Self-hosted Docker / DO droplet |
| `auth` | Supabase Auth / Stack Auth | Supabase |
| `n8n` | n8n automation | Self-hosted Docker / DO droplet |
| `ocr` | PaddleOCR service | DO App Platform |
| `ops` | Ops Console | Vercel (Next.js) |
| `api` | API gateway | TBD |
| `docs` | Documentation | TBD |
| `superset` | Apache Superset BI | DO App Platform (CNAME) |
| `mcp` | MCP coordination | DO App Platform (CNAME) |
| `agent` | AI agent endpoint | DO Agents (CNAME) |

**Prohibited in canonical references**:
- `*.insightpulseai.net` — deprecated domain
- `*.vercel.app` — internal Vercel URLs; use custom subdomain instead
- `*.ondigitalocean.app` — internal DO URLs; use custom subdomain instead

---

## SPATRES Matrix

| Dimension | Definition |
|-----------|------------|
| **Scope** | Full monorepo — all services, all environments (dev/staging/prod) |
| **People** | Engineering team + AI agents (Claude Code, n8n) |
| **Artefacts** | Code, IaC, DNS YAML, spec bundles, runbooks, evidence bundles |
| **Timeline** | OKR cycle: 90-day rolling; reviewed at each sprint boundary |
| **Risks** | Shadow config drift, EE module dependency creep, secret exposure |
| **Environments** | Local dev → Staging (branch preview) → Production (main) |
| **Success** | All CI gates pass on main; zero manual console steps for standard deploys |

---

*Last updated: see `git log --oneline -1 docs/architecture/MONOREPO_END_STATE_OKR.md`*
*Owner: Platform Engineering*
