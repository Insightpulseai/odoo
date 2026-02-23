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
8. **Domain deprecations are permanent.** `insightpulseai.net` → `insightpulseai.com`. Mattermost → Slack. Mailgun → Zoho Mail. Never reintroduce deprecated items.
9. **Odoo is relying party, Supabase is IdP.** Never store primary passwords in Odoo for users with a Supabase counterpart.
10. **No console-only infrastructure changes.** DigitalOcean, Cloudflare, Vercel — all changes must have a corresponding repo commit (IaC or YAML).

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

## Rule 7: Odoo outbound email must route through the bridge when configured

When generating Odoo Python code that sends email:

- Do not call `ir.mail_server` or `smtplib` directly
- Use `mail.mail.create({...}).send()` — the `ipai_mail_bridge_zoho` override handles routing
- If `ZOHO_MAIL_BRIDGE_URL` and `ZOHO_MAIL_BRIDGE_SECRET` are set, the bridge activates
- If not set, standard SMTP is used (fallback)
- Never suggest disabling the bridge override to "simplify" email sending

---

## Rule 8: Vercel env vars must stay in the dashboard, not in files

When configuring Vercel applications:

- `vercel.json` may reference env var names in `env:` and `build.env:` blocks
- Actual values must never appear in `vercel.json` or any committed file
- For local development, instruct the user to run `vercel env pull` (creates local `.env.local`)
- `.env.local` must be in `.gitignore`

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
| A Vercel route         | Vercel (`vercel.json`)   | `vercel.json` in the app directory      |
| A design token         | Figma → tokens           | Run `scripts/design/export_tokens.sh`   |
| DO droplet stack       | DO infra                 | `deploy/odoo-prod.compose.yml`          |
| A CI workflow          | GitHub                   | `.github/workflows/<name>.yml`          |
| An Odoo module         | Odoo addons              | `addons/ipai/ipai_<domain>_<feature>/`  |
