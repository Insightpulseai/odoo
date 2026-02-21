# Platform Repo Tree — InsightPulse AI

> SSOT-oriented directory map. Surface area is **explicit** — only curated entrypoints
> are canonical. Everything else is generated, derived, or transient.
>
> Last updated: 2026-02-21
> Mirrors: `docs/architecture/SSOT_BOUNDARIES.md` §SSOT Domains

---

## Canonical Tree

```
odoo/                               ← Repo root (SSOT for all platform domains)
│
├── addons/
│   ├── ipai/                       ← SSOT-A: Custom IPAI modules (ipai_* namespace)
│   │   ├── ipai_auth_oidc/         │  OCA-style, Supabase ↔ Odoo identity bridge
│   │   ├── ipai_zoho_mail/         │  Zoho SMTP/IMAP integration
│   │   ├── ipai_slack_connector/   │  Slack notifications (replaces Mattermost)
│   │   └── ...43 modules total     │
│   └── oca/                        ← SSOT-A: OCA community modules (pinned versions)
│       ├── bank-statement-import/
│       ├── mail/
│       ├── manufacture/
│       ├── server-tools/
│       ├── server-ux/
│       └── .../
│
├── supabase/                       ← SSOT-B: Supabase (Auth, DB schema, Edge Functions)
│   ├── migrations/                 │  Schema changes ONLY via migrations/
│   ├── functions/                  │  Edge Functions (provision-odoo-user, etc.)
│   ├── seed/                       │  Seed data (idempotent)
│   └── config.toml                 │  Project configuration
│
├── automations/
│   └── n8n/                        ← SSOT-C: n8n automation workflows
│       ├── workflows/              │  *.json exports (secret-free, committed after UI edit)
│       └── CREDENTIALS.md         │  Credential contracts (no secrets, references only)
│
├── web/                            ← SSOT-D: Vercel-deployed web apps
│   ├── ai-control-plane/           │  Next.js AI control plane (port 3100)
│   ├── apps/                       │  Additional web applications
│   ├── docs/                       │  Evidence bundles (canonical: YYYYMMDD-HHMM+0800/)
│   │   └── evidence/               │
│   │       └── 20*/                │  Timestamped evidence only (gitignore-excepted)
│   └── spec/                       │  Web app spec bundles
│
├── infra/
│   ├── cloudflare/                 ← SSOT-G: Cloudflare configuration (IaC)
│   │   └── envs/prod/              │
│   ├── digitalocean/               ← SSOT-F: DigitalOcean app specs
│   ├── dns/                        ← SSOT-G: DNS intent (YAML = truth)
│   │   ├── subdomain-registry.yaml │  All subdomains defined here first
│   │   └── zoho_mail_dns.yaml      │  Zoho Mail DNS records (MX, SPF, DKIM, DMARC)
│   ├── runbooks/                   ← SSOT-F: Operational runbooks
│   └── terraform/                  ← SSOT-F: Infrastructure as Code
│
├── design/                         ← SSOT-E: Figma design system exports
│   ├── assets/                     │  Static assets (exported from Figma)
│   ├── figma/                      │  FILE_KEYS.md — Figma file registry
│   ├── tokens/                     │  Design tokens (exported, not hand-edited)
│   └── schema.tokens.json          │  Canonical token schema
│
├── agents/                         ← Agent capabilities and MCP registry
│   ├── capabilities/               │  manifest.json (what agents CAN do)
│   ├── mcp/                        │  MCP server implementations
│   ├── registry/                   │  Agent registry
│   └── skills/                     │  Skill bundles
│
├── config/                         ← SSOT-A: Runtime configuration (never secrets)
│   ├── dev/odoo.conf
│   ├── staging/odoo.conf
│   ├── prod/odoo.conf
│   └── odoo/
│       └── mail_settings.yaml      │  Mail SSOT (applied by apply_mail_settings.py)
│
├── data/
│   └── seed/                       ← SSOT-A: Reference data (idempotent load scripts)
│
├── spec/                           ← SSOT for feature contracts
│   ├── <feature-slug>/             │  constitution.md, prd.md, plan.md, tasks.md
│   └── agent/
│       └── constitution.md         │  Agent execution constraints
│
├── docs/
│   ├── architecture/               ← Platform-level architectural decisions
│   │   ├── SSOT_BOUNDARIES.md      │  Canonical domain ownership (this doc's twin)
│   │   ├── PLATFORM_REPO_TREE.md   │  This file
│   │   ├── CANONICAL_URLS.md       │  URL registry
│   │   └── ROOT_ALLOWLIST.md       │  Allowed root-level paths
│   ├── contracts/                  ← Cross-domain contract docs
│   │   ├── DNS_EMAIL_CONTRACT.md
│   │   └── PLATFORM_CONTRACTS_INDEX.md
│   └── ai/                         ← AI agent reference docs
│
├── scripts/                        ← Automation scripts (550+ in 43 categories)
│   ├── odoo/                       │  Odoo install/update/health wrappers
│   ├── agents/                     │  Agent instruction sync, drift check
│   └── automations/                │  n8n sweep, deploy scripts
│
├── .github/
│   └── workflows/                  ← SSOT-H: CI gates (153 workflows)
│       ├── ssot-surface-guard.yml  │  Cross-domain SSOT enforcement (new)
│       ├── dns-ssot-apply.yml      │  DNS SSOT enforcement
│       ├── pr-scope-guard.yml      │  PR path scope enforcement
│       └── ...
│
└── .claude/
    ├── rules/                      ← Agent behavioral rules
    │   └── ssot-platform.md        │  Platform SSOT rules for Claude agents
    └── settings.json               │  Allowed tools
```

---

## Surface Area Rules

1. **Repo is SSOT.** Every intentional platform state must have a file in this tree.
2. **Evidence is derived.** `web/docs/evidence/20*/` contains proof, not truth.
3. **Generated files are not SSOT.** `*.auto.tfvars`, lock files, and build artifacts are derived.
4. **UI state is not SSOT.** n8n workflows edited via UI must be re-exported → committed. Same for Figma tokens, Cloudflare rules, Vercel env var names.
5. **Secrets are not in this tree.** Supabase Vault + container env vars only.

---

## Docker Mount Convention

| Mount path (container) | Host path (repo) | Domain |
|------------------------|------------------|--------|
| `/workspaces/odoo`     | `/` (repo root)  | All    |
| `/workspaces/odoo/addons/ipai` | `addons/ipai/` | A |
| `/workspaces/odoo/addons/oca/*` | `addons/oca/*/` | A |

> OCA modules mount as `addons/oca/` (slash). Never `addons-oca/` (hyphen).

---

## What Is NOT Here (and Why)

| Absent path | Reason |
|-------------|--------|
| `node_modules/`, `__pycache__/`, `dist/`, `build/` | Generated artifacts — gitignored |
| `.env`, `.env.*` | Secrets — never committed |
| `web/docs/evidence/20*/*/logs/*.log` | Evidence logs — gitignore-excepted via `!web/docs/evidence/20*/**/logs/` |
| `supabase/.branches/` | Supabase local dev state — transient |
| `sandbox/` | Transient dev workspace — not canonical |
