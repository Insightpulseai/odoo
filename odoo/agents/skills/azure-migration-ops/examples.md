# Examples — azure-migration-ops

## Example 1: Mailgun to Zoho SMTP migration

**Input**: PR updates Odoo mail server configuration from Mailgun to Zoho SMTP

**Output**:
- Source: Mailgun SMTP (`smtp.mailgun.org:2525`, domain `mg.insightpulseai.com`)
- Target: Zoho SMTP (`smtp.zoho.com:587`, domain `insightpulseai.com`)
- Source status: deprecated (2026-03-11)
- Target status: healthy — test email sent successfully
- DNS cutover: MX records point to Zoho — PASS
- Secret migration: `zoho-smtp-user` and `zoho-smtp-password` in `kv-ipai-dev` — PASS
- Residual references: 2 files still reference `mailgun` (scripts/deploy-mail.sh, docs/old-setup.md)
- Rollback path: documented in docs/contracts/MAIL_MIGRATION.md — PASS
- Blockers: 2 residual references must be cleaned up
- Evidence: `curl -s smtp.zoho.com:587` connection test, MX record lookup

## Example 2: DigitalOcean to Azure Container Apps

**Input**: Container Apps `ipai-odoo-dev-web` replaces DigitalOcean droplet `178.128.112.214`

**Output**:
- Source: DigitalOcean droplet (`178.128.112.214`, Docker Compose stack)
- Target: Azure Container App (`ipai-odoo-dev-web` in `rg-ipai-dev`)
- Source status: deprecated (2026-03-15)
- Target status: healthy — HTTP 200 on `/web/login`
- DNS cutover: `erp.insightpulseai.com` CNAME to Front Door — PASS
- Secret migration: all Odoo secrets in `kv-ipai-dev` — PASS
- Residual references: 5 files reference `178.128.112.214` or DigitalOcean
- Rollback path: documented — PASS
- Blockers: [5 residual references to old IP/provider in codebase]

## Example 3: Incomplete migration — DNS not yet cut over

**Input**: Vercel to ACA migration for website, DNS still pointing to Vercel

**Output**:
- Source: Vercel deployment (`insightpulseai.vercel.app`)
- Target: Azure Container App (`ipai-website-dev` in `rg-ipai-dev`)
- Source status: deprecated (2026-03-11)
- Target status: healthy — HTTP 200
- DNS cutover: NOT COMPLETE — `www.insightpulseai.com` still CNAME to Vercel — BLOCKER
- Blockers: [DNS cutover incomplete — traffic still routing to deprecated Vercel]
- Recommendation: Update Cloudflare CNAME for `www` to Front Door endpoint before marking complete
