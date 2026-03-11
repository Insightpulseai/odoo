# Constitution: OdooOps Console Auth (Supabase)

## Non-negotiables
- Supabase Auth is the sole identity provider for ops.insightpulseai.com
- Odoo ERP login remains Odoo-native (no changes)
- All ops data is isolated by org via RLS
- No secrets in repo; use Supabase Vault + Vercel env vars (server-only)

## Boundaries
- OdooOps Console manages deployments and metadata; Odoo remains system of record
- Any future SSO into Odoo is a separate module and does not change Odoo's internal auth baseline
