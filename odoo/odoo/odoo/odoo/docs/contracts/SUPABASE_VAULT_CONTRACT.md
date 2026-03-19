# Supabase Vault Contract

> **Scope**: Defines which secrets go to Supabase Vault (Postgres-side encrypted storage)
> vs Edge Function Secrets (runtime config for Deno), and the naming/access conventions.
>
> Reference: [Supabase Vault docs](https://supabase.com/docs/guides/database/vault)
> Last updated: 2026-02-21

---

## What Vault is

Supabase Vault is a Postgres extension (`pgsodium`) that stores secrets in an
**authenticated-encrypted table** (`vault.secrets`). Decrypted values are accessible
only through a **security-definer view/function** inside Postgres — never in plaintext
in backups or replication. Encrypted at rest on disk.

---

## Vault vs Edge Function Secrets — Decision Table

| Secret type | Where to store | Why |
|-------------|---------------|-----|
| Secrets used by **pg_cron** / **pg_net** / SQL triggers | **Vault** | Must be readable inside Postgres |
| Secrets used by Edge Functions only | **Edge Function Secrets** (`supabase secrets set`) | Simpler; Deno reads via `Deno.env.get()` |
| Secrets used by **both** Postgres and Edge Functions | **Vault** + expose via `SECURITY DEFINER` RPC | Single source; Edge Function calls RPC |
| Secrets used by Odoo container | Container env vars | Not Vault — Odoo cannot reach Supabase Vault directly |
| Secrets used by n8n workflows | n8n credentials store | n8n manages its own credential vault |

**Current state for Zoho bridge:**
- `BRIDGE_SHARED_SECRET`, `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ACCOUNT_ID`
  → stored as **Edge Function Secrets** (set via `supabase secrets set --project-ref spdtwktxdalcfigzeqrz`)
  → read in `supabase/functions/zoho-mail-bridge/index.ts` via `Deno.env.get()`
  → **do not move to Vault** unless a Postgres-side consumer exists

---

## Naming Convention for Vault Keys

Use dot-notation: `<category>.<service>.<field>`

| Category | Examples |
|----------|---------|
| `integrations.zoho.*` | `integrations.zoho.client_id`, `integrations.zoho.refresh_token` |
| `integrations.github.*` | `integrations.github.webhook_secret` |
| `auth.jwt.*` | `auth.jwt.signing_key` |
| `ops.cron.*` | `ops.cron.webhook_url` |

Flat uppercase env var names (`ZOHO_CLIENT_ID`) are for **Edge Function Secrets**.
Dot-notation names are for **Vault**.

---

## Access Policy

| Actor | Access to Vault | How |
|-------|----------------|-----|
| `service_role` | Full read/write | Direct access via decrypted view |
| Edge Functions | Read via Vault RPC or (preferred) Edge Secrets | `select integrations.get_secret('...')` |
| `anon` role | No access | RLS blocks; SECURITY DEFINER wraps |
| Odoo container | No direct access | Odoo cannot call Supabase Vault |
| pg_cron jobs | Read via `SECURITY DEFINER` functions | Call `integrations.get_secret()` |

**Rule:** No function readable by `anon` may return a vault secret value.
Only `SECURITY DEFINER` functions callable by `service_role` may return decrypted secrets.

---

## Secret Registry

`integrations.secret_registry` — a **metadata table** (no values) that declares
which secrets are required. Used for:
- CI assertions: "are all required secrets present?"
- Rotation tracking: when was a secret last rotated?
- Ownership: which team/service owns this secret?

See migration: `supabase/migrations/20260221000001_vault_secret_registry.sql`

---

## How to add a secret to Vault (CLI)

```bash
# Store a secret in Vault (value never committed to git)
supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
  MY_SECRET=the_actual_value

# For Postgres-side Vault (when the secret needs to be readable in SQL):
# Use the Supabase dashboard Vault UI or a one-time SQL migration:
# SELECT vault.create_secret('value', 'integrations.zoho.refresh_token', 'Zoho OAuth2 refresh token');
```

---

## CI Verification (secret names, not values)

The `check_required_secrets()` RPC returns names of **missing** required secrets
(by cross-referencing `integrations.secret_registry` against `vault.secrets`).
It never returns secret values — only the names of what is absent.

```sql
-- Call from CI via Supabase REST (service_role)
SELECT * FROM integrations.check_required_secrets();
-- Returns: TABLE(secret_name text, status text)
-- status = 'present' | 'missing'
```

---

## Related Docs

- `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` — C-07 Supabase Vault Secrets
- `docs/contracts/MAIL_BRIDGE_CONTRACT.md` — Zoho bridge uses Edge Secrets (not Vault)
- `infra/supabase/vault_secrets.tf` — Vault secret **names** tracked in Terraform
- `supabase/migrations/20260221000001_vault_secret_registry.sql` — Registry table + RPC
