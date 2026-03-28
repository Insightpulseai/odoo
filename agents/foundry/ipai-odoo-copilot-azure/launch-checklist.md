# Launch Checklist -- Odoo Copilot on Azure

> Version: 1.0.0
> Last updated: 2026-03-27
> Target: Advisory Release (PROD-ADVISORY)
> Parent: publish-policy.md, runtime-contract.md (C-30)

## Pre-Launch (must all pass before enabling for users)

### Agent Configuration

- [ ] System prompt v2.0.0+ is live on Foundry agent `asst_45er4aG28tFTABadwxEhODIf`
- [ ] Temperature is 0.4 (not 1.0)
- [ ] Top P is 0.9 (not 1.0)
- [ ] Content Safety active (Hate, Sexual, Violence, SelfHarm)
- [ ] No tools wired (advisory mode only)
- [ ] Agent model is `gpt-4.1`

### Odoo Module

- [ ] `ipai_odoo_copilot` module installed on target database
- [ ] `ipai.copilot.enabled` = `True` in ir.config_parameter
- [ ] `ipai.copilot.mode` = `PROD-ADVISORY`
- [ ] `ipai.copilot.model` = `gpt-4.1`
- [ ] `AZURE_FOUNDRY_API_KEY` env var set on container app (sourced from Key Vault)
- [ ] `AZURE_OPENAI_ENDPOINT` env var set on container app
- [ ] Connection test passes (Settings > IPAI Copilot > Test Connection)

### Security

- [ ] API key is sourced from Azure Key Vault, not hardcoded
- [ ] Copilot endpoints require `auth='user'` (verified in controller)
- [ ] Rate limiting active (20 req/min/user)
- [ ] Audit logging active (ipai.copilot.audit model populated on test requests)
- [ ] Conversation access scoped to user + company

### Evaluation

- [ ] Eval dataset v2 loaded (minimum 30 cases for initial Advisory Release)
- [ ] eval-20260315-full-final.json: 30/30 pass
- [ ] 0 critical safety failures
- [ ] 0 PII leakage events
- [ ] 0 unauthorized action attempts

### Infrastructure

- [ ] Container app `ipai-odoo-dev-web` running with copilot module
- [ ] Dockerfile.odoo-copilot builds successfully
- [ ] `/web/health` returns 200
- [ ] `/ipai/copilot/chat` returns valid JSON-RPC response for test prompt

## Post-Launch Monitoring (first 72 hours)

- [ ] Review audit logs: `SELECT * FROM ipai_copilot_audit ORDER BY create_date DESC LIMIT 50`
- [ ] Confirm no error-type audit events
- [ ] Confirm response latency < 30s (poll timeout)
- [ ] Confirm no rate-limit false positives blocking legitimate users
- [ ] Spot-check 5 responses for scope boundary compliance

## Rollback Procedure

1. Set `ipai.copilot.enabled` = `False` in ir.config_parameter (immediate, no restart needed)
2. If module-level issue: `odoo -d <db> -u ipai_odoo_copilot --stop-after-init`
3. If Foundry-side issue: no action needed on Odoo side (gateway returns error, audit logs capture it)
4. Document rollback reason in `agents/foundry/ipai-odoo-copilot-azure/publish-policy.md` changelog

## Promotion to Grounded Advisory (next level)

Before promoting beyond Advisory Release, all of the following must be complete:

- [ ] AI Search index `ipai-knowledge-index` populated with 100+ chunks
- [ ] Retrieval grounding active in gateway controller
- [ ] Security trimming verified (kb_scope + group_ids filtering)
- [ ] Entra app roles registered and assigned
- [ ] Context envelope injected in every request path
- [ ] App Insights telemetry live and dashboard accessible
- [ ] Eval dataset expanded to 150+ cases
- [ ] Eval pass rate meets thresholds.yaml criteria at all levels
