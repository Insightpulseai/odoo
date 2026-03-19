# Release Promotion Runbook

> Version: 1.0.0
> Last updated: 2026-03-14
> Canonical repo: `infra`

## Purpose

Step-by-step procedure for promoting an InsightPulseAI offering from one publish level to the next.

## Pre-Promotion Checklist

- [ ] Evaluation results committed to `agents/evals/odoo-copilot/results/`
- [ ] All threshold metrics pass (see `agents/evals/odoo-copilot/thresholds.yaml`)
- [ ] No critical safety failures in latest eval run
- [ ] DNS target state confirmed for offering hostname
- [ ] TLS certificate valid for offering hostname
- [ ] Auth/identity baseline met for target stage
- [ ] Release evidence directory created: `docs/evidence/<YYYYMMDD-HHMM>/<offering>/`

## Promotion Procedure

### 1. Verify Evaluation Evidence

```bash
# Check eval results exist
ls agents/evals/odoo-copilot/results/

# Verify thresholds pass
python3 scripts/evals/check_thresholds.py \
  --results agents/evals/odoo-copilot/results/latest.json \
  --thresholds agents/evals/odoo-copilot/thresholds.yaml
```

### 2. Verify Runtime Health

```bash
# Foundry health probe
curl -s https://data-intel-ph-resource.services.ai.azure.com/openai/assistants?api-version=2024-12-01-preview \
  -H "api-key: $AZURE_FOUNDRY_API_KEY" | jq '.data | length'

# Odoo health probe
curl -s https://erp.insightpulseai.com/ipai/copilot/health

# Docs widget health
curl -s https://docs.insightpulseai.com/api/health
```

### 3. Verify DNS and TLS

```bash
# DNS resolution
dig +short <offering>.insightpulseai.com CNAME
dig +short <offering>.insightpulseai.com A

# TLS validation
curl -sI https://<offering>.insightpulseai.com | head -5
```

### 4. Update Publish Policy

Edit `agents/foundry/ipai-odoo-copilot-azure/publish-policy.md`:
- Add changelog entry with date, from/to levels, and evidence reference
- Update "Current State" section

### 5. Create Release Evidence

```bash
mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/<offering>/
# Copy eval results, health probe output, DNS verification
```

### 6. Commit and Tag

```bash
git add agents/ docs/evidence/
git commit -m "feat(copilot): promote to <level> — eval evidence attached"
git tag -a "copilot-<level>-$(date +%Y%m%d)" -m "Copilot promoted to <level>"
```

## Rollback Procedure

### Immediate Rollback

1. Update `publish-policy.md` to previous level
2. If DNS was changed, revert to previous target (see DNS_CUTOVER_CHECKLIST.md rollback table)
3. If runtime mode was changed, revert `read_only_mode` to True in Odoo Settings
4. Commit with: `fix(copilot): rollback to <previous_level> — <reason>`

### Post-Incident

1. Create incident report in `docs/evidence/<YYYYMMDD-HHMM>/incident/`
2. Root cause analysis within 48 hours
3. Update guardrails if new failure mode discovered
4. Re-run evaluation suite before re-attempting promotion

## Promotion Path

```
Internal Prototype
  ↓ (quality + safety evals pass)
Advisory Release
  ↓ (tool/action evals pass, draft_only validated)
Guided Actions Beta
  ↓ (full eval suite, hardened auth, SLA, security review)
GA
```

## Environment Mapping

| Level | Runtime Mode | Foundry Config | Auth |
|-------|-------------|---------------|------|
| Internal Prototype | read_only | API key OK | Odoo session |
| Advisory Release | read_only | Managed identity preferred | Odoo session |
| Guided Actions Beta | draft_only | Managed identity required | Odoo session + confirmation |
| GA | configurable | Managed identity only | Odoo session + MFA for actions |
