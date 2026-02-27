# Platform Repository Tree — InsightPulse AI

> **Surface-Area-Explicit Principle**: Every directory entry below carries an SSOT label.
> If a path is not listed here, it is either ephemeral (not committed) or must be added
> with an explicit SSOT assignment before any agent may write to it.
>
> Last updated: 2026-02-27

---

## Root Layout

```
Insightpulseai/odoo/                     ← repo root (Git SSOT for everything below)
│
├── addons/                              ← Odoo module code (Git SSOT)
│   ├── ipai/                            ← Custom IPAI modules (43 modules)
│   │   └── ipai_<domain>_<feature>/     ← OCA-style module naming
│   └── oca/                             ← OCA submodule pinned references
│
├── automations/                         ← n8n workflow exports (Git SSOT for structure)
│   └── n8n/
│       ├── workflows/                   ← Exported JSON — canonical n8n SSOT
│       │   └── archive/                 ← Stale workflows (>90d no execution)
│       └── credentials/                 ← YAML manifests (names only, no values)
│
├── config/                              ← Service configuration files (Git SSOT)
│   └── odoo/
│       └── mail_settings.yaml           ← Mail SSOT (see SSOT_BOUNDARIES §2)
│
├── deploy/                              ← Production compose files (Git SSOT)
│   └── odoo-prod.compose.yml            ← DO droplet stack definition
│
├── docs/                                ← Documentation (Git SSOT)
│   ├── ai/                              ← Agent reference docs (sync'd from SSOT.md)
│   ├── architecture/                    ← Architecture decision records
│   │   ├── SSOT_BOUNDARIES.md           ← THIS repo's SSOT map (SSOT for SSOT)
│   │   ├── PLATFORM_REPO_TREE.md        ← This file
│   │   └── runtime_identifiers.json     ← Generated — DO NOT EDIT DIRECTLY
│   ├── contracts/                       ← Cross-domain contract definitions
│   │   ├── DNS_EMAIL_CONTRACT.md
│   │   └── PLATFORM_CONTRACTS_INDEX.md  ← Master index of all contracts
│   └── evidence/                        ← Ephemeral execution evidence (Git SSOT for structure)
│       └── YYYYMMDD-HHMM+0800/<topic>/logs/  ← Timestamped evidence bundles
│
├── infra/                               ← Infrastructure as Code (Git SSOT)
│   ├── cloudflare/                      ← Terraform for Cloudflare
│   │   └── envs/prod/
│   │       └── subdomains.auto.tfvars   ← Generated — DO NOT EDIT DIRECTLY
│   ├── dns/                             ← DNS records (Git SSOT)
│   │   ├── subdomain-registry.yaml      ← Cloudflare DNS SSOT
│   │   ├── zoho_mail_dns.yaml           ← Zoho mail DNS records
│   │   └── dns-validation-spec.json     ← Generated — DO NOT EDIT DIRECTLY
│   ├── supabase/
│   │   └── vault_secrets.tf             ← Vault secret NAMES only (no values)
│   └── terraform/                       ← DO droplet + firewall (Git SSOT)
│
├── packages/                            ← Shared packages (Git SSOT)
│   ├── assets/                          ← Brand assets exported from Figma
│   │   └── icons/                       ← SVG icons (committed after Figma export)
│   └── design-tokens/
│       └── tokens.json                  ← Design tokens (generated from Figma, Git SSOT)
│
├── scripts/                             ← Automation scripts (Git SSOT)
│   ├── agents/                          ← Agent instruction sync
│   ├── automations/                     ← n8n deploy/sweep scripts
│   ├── design/                          ← Token export scripts
│   ├── dns/                             ← DNS artifact generator
│   └── odoo/                            ← Odoo management wrappers
│
├── spec/                                ← Spec bundles (Git SSOT, spec-kit format)
│   └── <feature-slug>/
│       ├── constitution.md
│       ├── prd.md
│       ├── plan.md
│       └── tasks.md
│
├── supabase/                            ← Supabase project config (Git SSOT)
│   ├── config.toml                      ← Project + Edge Function config
│   ├── functions/                       ← Edge Function source code
│   │   └── <name>/index.ts
│   └── migrations/                      ← Sequential SQL migrations
│       └── YYYYMMDDHHMMSS_<name>.sql
│
└── .github/
    └── workflows/                       ← CI/CD pipeline (Git SSOT)
        └── *.yml                        ← 153+ workflows — names are canonical IDs
```

---

## SSOT Assignment Table

| Path pattern                                        | SSOT owner            | Derived from                        | Regenerate command                      |
| --------------------------------------------------- | --------------------- | ----------------------------------- | --------------------------------------- |
| `addons/ipai/**`                                    | Git                   | (original)                          | —                                       |
| `addons/oca/**`                                     | OCA upstream          | submodule pin                       | `git submodule update`                  |
| `automations/n8n/workflows/*.json`                  | Git (export from n8n) | Live n8n instance                   | `scripts/automations/export_n8n.py`     |
| `config/odoo/mail_settings.yaml`                    | Git                   | (original)                          | —                                       |
| `deploy/*.compose.yml`                              | Git                   | (original)                          | —                                       |
| `docs/architecture/runtime_identifiers.json`        | **Generated**         | `infra/dns/subdomain-registry.yaml` | `scripts/dns/generate-dns-artifacts.sh` |
| `infra/cloudflare/envs/prod/subdomains.auto.tfvars` | **Generated**         | `infra/dns/subdomain-registry.yaml` | `scripts/dns/generate-dns-artifacts.sh` |
| `infra/dns/dns-validation-spec.json`                | **Generated**         | `infra/dns/subdomain-registry.yaml` | `scripts/dns/generate-dns-artifacts.sh` |
| `infra/dns/subdomain-registry.yaml`                 | Git                   | (original)                          | —                                       |
| `packages/design-tokens/tokens.json`                | **Generated**         | Figma file                          | `scripts/design/export_tokens.sh`       |
| `ssot/odoo/settings_catalog.yaml`                   | **Generated**         | Live Odoo 19 CE instance            | `scripts/odoo/extract_settings_catalog.py` |
| `supabase/config.toml`                              | Git                   | (original)                          | —                                       |
| `supabase/migrations/*.sql`                         | Git                   | (original)                          | —                                       |
| `supabase/functions/**`                             | Git                   | (original)                          | —                                       |
| `.github/workflows/*.yml`                           | Git                   | (original)                          | —                                       |

---

## Surface Area Rules

### Rule A — Generated files must not be hand-edited

Files marked **Generated** above carry a `# DO NOT EDIT DIRECTLY` header.
A CI check (`repo-structure-guard.yml`) detects edits that bypass the generator.

### Rule B — New paths require SSOT assignment before first commit

Before adding a new top-level directory or significant sub-tree:

1. Add a row to the SSOT Assignment Table above.
2. Add a path guard to `.github/workflows/ssot-surface-guard.yml`.
3. Reference the governing contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.

### Rule C — Ephemeral paths must not be committed

| Ephemeral path         | Reason                                                 |
| ---------------------- | ------------------------------------------------------ |
| `sandbox/**`           | Development scratch space — `sandbox/` in `.gitignore` |
| `web/docs/evidence/**` | CI evidence — committed only in timestamped bundles    |
| `*.log`, `*.tmp`       | Build artifacts                                        |
| `.env`, `.env.*`       | Secrets — absolute block                               |

### Rule D — Addons must follow OCA naming

`addons/ipai/ipai_<domain>_<feature>/` — no exceptions.
Violations detected by `ipai-custom-modules-guard.yml`.

### Rule E — n8n JSON exports must be secret-free

`automations/n8n/workflows/*.json` must not contain literal credential values.
Enforced by `ssot-surface-guard.yml` secret scan step.
