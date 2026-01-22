## Summary

Adds unified CD pipeline for automated production deployment on merge to main.

### Changes
- **CD Pipeline** (`.github/workflows/cd-production.yml`): Build → Smoke Test → Deploy → Verify → Release
- **Deployment via DigitalOcean API** (doctl) - no SSH keys required
- **Web Session Parity**: Codespaces/sandbox now has same capabilities as local CLI
- **Credential Management**: `.env.local` auto-loading, one-time setup scripts
- **Supabase Verification**: Full verification script for migrations, functions, vault

### Files Added/Modified
- `.github/workflows/cd-production.yml`
- `scripts/deploy_production.sh`
- `scripts/diagnose_prod.sh`
- `scripts/verify_supabase_full.sh`
- `scripts/setup_credentials.sh`
- `scripts/lib/load_env.sh`
- `scripts/web_session_init.sh`
- `.claude/hooks/SessionStart.md`
- `.claude/settings.web.json`
- `.devcontainer/devcontainer.json`

### Required Secret

Add `DIGITALOCEAN_TOKEN` to GitHub secrets before merging:
https://github.com/jgtolentino/odoo-ce/settings/secrets/actions

## Test Plan

- [ ] Add `DIGITALOCEAN_TOKEN` secret to GitHub
- [ ] Merge to main
- [ ] Verify CD pipeline runs successfully
- [ ] Check https://erp.insightpulseai.net/web/health returns 200
