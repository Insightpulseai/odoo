# Platform Contracts Index

> Index of all cross-domain contracts in the InsightPulse AI platform.
> A contract is a binding agreement between two or more SSOT domains.
> Each contract must have: a repo file (SSOT), an evidence export (derived), and a CI gate (enforcing).
>
> Last updated: 2026-02-21
> See also: `docs/architecture/SSOT_BOUNDARIES.md` §Cross-Domain Contract Objects

---

## Contract Registry

| # | Contract | SSOT Domain(s) | SSOT Repo File | Evidence Export | Enforcing CI Gate |
|---|----------|---------------|----------------|-----------------|-------------------|
| 1 | **DNS & Email** | G (Cloudflare) + A (Odoo mail) | `infra/dns/subdomain-registry.yaml` + `infra/dns/zoho_mail_dns.yaml` | `reports/cloudflare_dns_diff_*.json` | `dns-ssot-apply.yml`, `compose-ssot-gate.yml` |
| 2 | **Identity** | B (Supabase Auth) → A (Odoo `res.users`) | `supabase/functions/provision-odoo-user` + `supabase/migrations/*auth*` | Dashboard Auth state | `verify-ops-ssot.yml` |
| 3 | **n8n Workflows** | C (n8n) ↔ B + A | `automations/n8n/workflows/*.json` | `reports/n8n_inventory_*.json` | `ssot-surface-guard.yml` |
| 4 | **OCA Module Allowlist** | A (Odoo addons) | `config/oca/module_allowlist.yml` | `reports/odoo_module_state_*.json` | `install-set-drift-guard.yml` |
| 5 | **Canonical URLs** | D (Vercel) + F (DO) + G (Cloudflare) | `infra/dns/subdomain-registry.yaml` + `docs/architecture/CANONICAL_URLS.md` | `reports/cloudflare_dns_diff_*.json` | `dns-ssot-apply.yml`, `vercel-env-leak-guard.yml` |
| 6 | **Repo Root Allowlist** | H (GitHub) | `docs/architecture/ROOT_ALLOWLIST.md` | Root dir snapshot | `root-allowlist-guard.yml` |
| 7 | **Secrets** | All domains | Supabase Vault + container env vars | Never exported | Pre-commit secret scan (CI) |
| 8 | **PR Scope** | H (GitHub) | `.github/pull_request_template.md` | PR diff | `pr-scope-guard.yml` |
| 9 | **Compose / DevContainer** | A (Odoo) + all local services | `.devcontainer/docker-compose.devcontainer.yml` | `reports/compose_health_*.json` | `compose-ssot-gate.yml` |

---

## Contract Details

### Contract 1 — DNS & Email

| Field | Value |
|-------|-------|
| **Owner** | G (Cloudflare DNS) + A (Odoo mail settings) |
| **SSOT files** | `infra/dns/subdomain-registry.yaml` (all subdomains), `infra/dns/zoho_mail_dns.yaml` (Zoho MX/SPF/DKIM/DMARC) |
| **Derived** | `infra/cloudflare/envs/prod/subdomains.auto.tfvars` (Terraform), `docs/architecture/runtime_identifiers.json` |
| **Applier script** | `scripts/odoo/apply_mail_settings.py` (Odoo DB), `scripts/generate-dns-artifacts.sh` (Terraform vars) |
| **CI gates** | `dns-ssot-apply.yml`, `compose-ssot-gate.yml` |
| **Canonical doc** | `docs/contracts/DNS_EMAIL_CONTRACT.md` |
| **Drift rule** | Edit `subdomain-registry.yaml` → run generator → commit → Terraform applies |

### Contract 2 — Identity (Supabase → Odoo)

| Field | Value |
|-------|-------|
| **Owner** | B (Supabase Auth) is SSOT; A (Odoo) is relying party |
| **SSOT files** | `supabase/functions/provision-odoo-user`, `supabase/migrations/*auth*` |
| **Bridge fields** | `auth.users.id` → `res.users.x_supabase_user_id`, email, org/company |
| **Forbidden from mirroring** | Passwords, MFA factors, sessions, raw JWT |
| **CI gate** | `verify-ops-ssot.yml` |
| **Status** | Partial — `x_supabase_user_id` field and auth hook pending |

### Contract 3 — n8n Workflows

| Field | Value |
|-------|-------|
| **Owner** | C (n8n live instance) = runtime SSOT; `automations/n8n/workflows/` = repo SSOT |
| **SSOT files** | `automations/n8n/workflows/*.json` (secret-free JSON exports) |
| **Credential contracts** | `automations/n8n/CREDENTIALS.md` (references only, no secrets) |
| **Drift rule** | Any workflow edited in n8n UI must be re-exported → committed before next sprint |
| **Secret guard** | No `"password"`, `"token"`, `"secret"`, `"apiKey"` in workflow JSON |
| **CI gate** | `ssot-surface-guard.yml` (new) |
| **Deployer** | `scripts/automations/deploy_n8n_all.py` (idempotent, diff-based) |

### Contract 4 — OCA Module Allowlist

| Field | Value |
|-------|-------|
| **Owner** | A (Odoo addons layer) |
| **SSOT files** | `config/oca/module_allowlist.yml` |
| **Evidence** | `reports/odoo_module_state_<env>.json` |
| **Path rule** | `addons/oca/<repo-name>/<module>/` — slash, never hyphen |
| **CI gate** | `install-set-drift-guard.yml` |

### Contract 5 — Canonical URLs

| Field | Value |
|-------|-------|
| **Owner** | G (Cloudflare DNS) + D (Vercel) + F (DigitalOcean) |
| **SSOT files** | `infra/dns/subdomain-registry.yaml`, `docs/architecture/CANONICAL_URLS.md` |
| **Domain** | `insightpulseai.com` (never `.net`, deprecated 2026-02) |
| **CI gates** | `dns-ssot-apply.yml`, `vercel-env-leak-guard.yml` |

### Contract 6 — Repo Root Allowlist

| Field | Value |
|-------|-------|
| **Owner** | H (GitHub) |
| **SSOT files** | `docs/architecture/ROOT_ALLOWLIST.md` |
| **CI gate** | `root-allowlist-guard.yml` |
| **Rule** | No new root-level directories without updating allowlist and getting CI green |

### Contract 7 — Secrets

| Field | Value |
|-------|-------|
| **Storage** | Supabase Vault (remote/CI), container env vars (runtime), macOS Keychain (local dev) |
| **Never in** | Git, logs, CI output, `config/` YAML |
| **Log hygiene** | Print only host/port/user/PASS-FAIL; never print token/password/key partially |
| **Gate** | Pre-commit secret scan: `git log -p \| grep -E "password\|secret\|token" \| grep -v placeholder` |

### Contract 8 — PR Scope

| Field | Value |
|-------|-------|
| **Owner** | H (GitHub) |
| **SSOT file** | `.github/pull_request_template.md` |
| **CI gate** | `pr-scope-guard.yml` |
| **5 policy gates** | Spec Bundle, Secret Pattern, Odoo 19 View Convention, Migration RLS, Deprecated Reference |

### Contract 9 — Compose / DevContainer

| Field | Value |
|-------|-------|
| **Owner** | A (Odoo) + all local services |
| **SSOT files** | `.devcontainer/docker-compose.devcontainer.yml`, `devcontainer.json` |
| **Canonical dev root** | `/workspaces/odoo` (repo root bind-mounted) |
| **CI gate** | `compose-ssot-gate.yml` |

---

## Adding a New Contract

1. Identify the two or more SSOT domains involved
2. Create or update the SSOT repo file
3. Document the contract here (this index)
4. Add or update the CI gate in `.github/workflows/`
5. Reference from `SSOT_BOUNDARIES.md` §Cross-Domain Contract Objects
