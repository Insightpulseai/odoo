# Constitution — Supabase Auth SSOT

> Non-negotiable governance rules for identity and access across the InsightPulse AI platform.

## Core Rules

1. **Supabase Auth is the IdP.** It is the single source of truth for user identities, sessions, MFA state, and social/OAuth provider links. No other system may become a primary identity authority.

2. **Odoo is a relying party only.** Odoo does not store primary credentials, social identity metadata, or session tokens. Its `res.users` rows are projections derived from Supabase Auth records.

3. **Mirror only what ERP needs.** The projection from Supabase → Odoo contains: UUID linkage key, email, company mapping, derived role label. Nothing else crosses the boundary.

4. **Provisioning is on-demand, not bulk.** Internal Odoo users are created by an Edge Function triggered by Supabase Auth hooks — not by batch jobs, not by UI, not by CSV import.

5. **RBAC and RLS are Supabase primitives.** Row-level access control lives in Postgres policies managed by Supabase. Odoo access groups are a secondary enforcement layer only.

6. **No passwords in git.** Auth configuration (client IDs, secrets, JWKS, SAML metadata) lives in Supabase Vault or CI secrets. Never in committed files.

7. **Auth hooks are audited.** Every hook invocation (signup, login, MFA enroll, role change) produces a row in `ops.platform_events`.

8. **Third-party JWT trust is declared, not assumed.** Any system trusting Supabase JWTs must explicitly configure the JWKS endpoint. Ad-hoc JWT parsing without validation is forbidden.

9. **SSO requires spec approval.** SAML integrations must be documented in a spec bundle before configuration. No SAML connections created via UI alone.

10. **Feature adoption follows the P0→P3 backlog.** Only adopt Supabase Auth features listed in `tasks.md`. New features require a spec amendment.
