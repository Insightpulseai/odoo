# SSOT Platform Rules — Agent Behavior

> These rules govern agent behavior with respect to the Platform SSOT Map.
> They extend (and never contradict) the top-level CLAUDE.md operating contract.
> Reference: `docs/architecture/SSOT_BOUNDARIES.md`, `docs/architecture/PLATFORM_REPO_TREE.md`

---

## Core Rules (Concise Reference)

1. **Repo is SSOT.** UI changes must be exported back: n8n → JSON, Figma → tokens, Cloudflare → DNS YAML.
2. **Surface area is allowlisted.** Only paths in `docs/architecture/PLATFORM_REPO_TREE.md` are canonical entrypoints.
3. **Secrets never committed.** Supabase Vault + container env vars only. Never `.env*` in git.
4. **Schema changes only via migrations.** No ad-hoc SQL, no Supabase dashboard schema edits.
5. **OCA path is `addons/oca/` (slash).** Never `addons-oca/` (hyphen). Docker mount: `/workspaces/odoo/addons/oca/*`.
6. **Evidence is not SSOT.** `web/docs/evidence/20*/` bundles are derived proof, not source of truth.
7. **Cross-domain changes need a contract doc.** DNS + email changes → `docs/contracts/DNS_EMAIL_CONTRACT.md`. New cross-domain contracts → register in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.
8. **Domain deprecations are permanent.** `insightpulseai.net` → `insightpulseai.com`. Mattermost → Slack. Never reintroduce deprecated items.
9. **Odoo is relying party, Supabase is IdP.** Never store primary passwords in Odoo for users with a Supabase counterpart.
10. **No console-only infrastructure changes.** Azure, Cloudflare — all changes must have a corresponding repo commit (IaC or YAML).

---

## Rule 1: Read before write — always consult the SSOT map

Before modifying any file, identify which SSOT domain owns it using
`docs/architecture/PLATFORM_REPO_TREE.md`. If the path is not listed,
do not create it until you have added a row to the SSOT Assignment Table.

**Banned action**: Creating a file in a path not covered by the SSOT tree
without first updating `PLATFORM_REPO_TREE.md`.

---

## Rule 2: Generated files must never be hand-edited

Files marked "Generated" in `PLATFORM_REPO_TREE.md` must only be changed
by running their declared regenerate command:

| File                                                | Regenerate command                      |
| --------------------------------------------------- | --------------------------------------- |
| `infra/cloudflare/envs/prod/subdomains.auto.tfvars` | `scripts/dns/generate-dns-artifacts.sh` |
| `docs/architecture/runtime_identifiers.json`        | `scripts/dns/generate-dns-artifacts.sh` |
| `infra/dns/dns-validation-spec.json`                | `scripts/dns/generate-dns-artifacts.sh` |
| `packages/design-tokens/tokens.json`                | `scripts/design/export_tokens.sh`       |
| `ssot/odoo/settings_catalog.yaml`                   | `scripts/odoo/extract_settings_catalog.py` |

If asked to edit a generated file directly, instead:

1. State which generator script produces it.
2. Edit the upstream SSOT source.
3. Run the generator.
4. Commit all changed files together.

---

## Rule 3: Secrets never cross boundaries in plaintext

Regardless of which SSOT domain is involved, secrets must never be:

- Written to any file tracked by Git (except `*.example` or `vault_secrets.tf` for names only)
- Echoed or printed in CI logs
- Included in n8n workflow JSON exports
- Passed as URL query parameters

When a secret is required and missing, state exactly which env var or Vault key
is needed and what the source SSOT is (see `SSOT_BOUNDARIES.md §3`).

---

## Rule 4: DNS changes require YAML-first workflow

Never suggest direct Cloudflare API calls or dashboard changes for DNS.
The workflow is always:

```
1. Edit infra/dns/subdomain-registry.yaml
2. Run scripts/dns/generate-dns-artifacts.sh
3. Commit all generated artifacts together
4. CI (dns-ssot-apply.yml) applies via Terraform on merge to main
```

---

## Rule 5: Supabase migrations are append-only for ops.\* schema

Never generate a migration that drops or truncates any table in the `ops` schema.
Tables `ops.platform_events` and `ops.task_queue` are append-only.
New columns may be added via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.

If a schema change is genuinely required, document the reason in the migration
file header and require a manual review step.

---

## Rule 6: n8n workflows must use credential references, not literal values

When generating or modifying n8n workflow JSON:

- Use `{{ $credentials.<name>.<field> }}` for credential values
- Use `{{ $env.<VAR_NAME> }}` for environment variable references
- Never include literal passwords, API keys, or tokens in the JSON

---

## Rule 7: Odoo outbound email uses Zoho SMTP (Mailgun is deprecated)

Odoo outbound mail routes through Zoho SMTP on port 587/TLS.
Mailgun (`mg.insightpulseai.com`) is deprecated — never reintroduce it.

SMTP transport (SSOT: `config/odoo/mail_settings.yaml`):
- Host: `smtp.zoho.com` (or `smtppro.zoho.com` for paid org mailboxes)
- Port: `587` (STARTTLS) or `465` (SSL) — never port 25 (blocked by Azure)
- Auth: required — credentials resolved at runtime via Azure Key Vault

Secret source of truth: **Azure Key Vault** (`kv-ipai-dev`).
- Secret names: `zoho-smtp-user`, `zoho-smtp-password`
- Runtime binding: managed identity → Key Vault → env vars `ZOHO_SMTP_USER` / `ZOHO_SMTP_PASSWORD`
- No plaintext credentials in tracked config files.

When generating Odoo Python code that sends email:

- Use `mail.mail.create({...}).send()` — Odoo's standard `ir.mail_server` handles delivery via Zoho SMTP
- Sender addresses must be authorized Zoho mailboxes on `insightpulseai.com`
- Never use Mailgun endpoints, `mg.insightpulseai.com`, or port 25
- Never introduce a bridge module for mail routing — standard `ir.mail_server` with Zoho SMTP credentials is the canonical path
- Never place SMTP credentials in `odoo.conf`, `.env` files tracked in git, or any committed config

---

## Rule 8: Vercel is deprecated — Azure-native deployment is canonical

Vercel is no longer an active deployment target for this repository.
Azure Container Apps (`ca-ipai-dev`) is the canonical deployment surface.

- Do not add new `vercel.json` files or Vercel project configurations
- Do not create workflows that depend on Vercel deployment status events
- Do not treat Vercel preview deployments as CI gates
- Any remaining Vercel integrations, preview checks, or deployment references are transitional residue and should be removed
- SSOT integration files (`ssot/integrations/vercel_*.yaml`) are marked `deprecated`

---

## Rule 9: New contracts require a doc + CI validator

When implementing a feature that crosses an SSOT boundary:

1. Check `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` for an existing contract.
2. If none exists, create `docs/contracts/<NAME>_CONTRACT.md`.
3. Add a row to the index.
4. Add validation to `.github/workflows/ssot-surface-guard.yml` or a dedicated workflow.

A cross-boundary feature may not be marked complete until the contract exists.

---

## Rule 10: OCA module isolation

When working on `addons/oca/` submodules:

- Never modify OCA module source code — create an `ipai_*` override module instead
- OCA submodule pins live in `.gitmodules` — update via `git submodule update --remote`
- Never copy OCA files into `addons/ipai/` — use proper `_inherit` overrides

---

## Quick Reference: Which domain owns what?

| I need to change...    | SSOT domain              | File to edit                            |
| ---------------------- | ------------------------ | --------------------------------------- |
| A DNS record           | Cloudflare DNS           | `infra/dns/subdomain-registry.yaml`     |
| Mail server config     | Mail (`config/odoo/`)    | `config/odoo/mail_settings.yaml`        |
| An Edge Function       | Supabase (`supabase/`)   | `supabase/functions/<name>/index.ts`    |
| A Supabase secret name | Supabase Vault           | `infra/supabase/vault_secrets.tf`       |
| An n8n workflow        | n8n (`automations/n8n/`) | `automations/n8n/workflows/<name>.json` |
| A Vercel route         | **DEPRECATED**           | Vercel is no longer active — use Azure Container Apps |
| A design token         | Figma → tokens           | Run `scripts/design/export_tokens.sh`   |
| Azure Container Apps   | Azure infra              | `infra/azure/`                          |
| A CI workflow          | GitHub                   | `.github/workflows/<name>.yml`          |
| An Odoo module         | Odoo addons              | `addons/ipai/ipai_<domain>_<feature>/`  |
