# Platform SSOT Rules

Rules for Claude agent behavior across all 8 InsightPulse AI platform domains.

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
