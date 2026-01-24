# Current Focus (ChatGPT)

## Active Priorities

1. **Marketplace Integrations** - GitHub/Drive/S3 artifact sync
2. **Memory Architecture** - LLM packs separate from ops memory
3. **Finance PPM** - BIR compliance automation

## Quick Commands

```bash
# Check marketplace syncs
SELECT status, COUNT(*) FROM marketplace.artifact_syncs GROUP BY status;

# Check recent workflow runs
gh run list -R Insightpulseai-net/odoo-ce --limit 5

# Deploy IPAI modules
./scripts/deploy-odoo-modules.sh
```

## Known Blockers

- GitHub iterations API missing (UI-only for now)
- Vault beta - use env vars as fallback

## Don't Forget

- Run `./scripts/repo_health.sh` before commits
- Evidence pack required for all deploys
- No secrets in repo - use Actions secrets
