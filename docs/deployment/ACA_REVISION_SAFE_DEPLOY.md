# ACA revision-safe deployment — Pulser web landing

## Why this exists

The InsightPulseAI public website (`https://www.insightpulseai.com/`) is
served by a **single Azure Container App**:

| Resource | Value |
|---|---|
| ACA name | `ipai-website` |
| Resource group | `rg-ipai-dev-odoo-sea` |
| Region | Southeast Asia |
| Image | `acripaiodoo.azurecr.io/ipai-website:latest` |

There is **no separate staging ACA**. A flat `az containerapp update`
call flips 100% production traffic to the new revision immediately —
there is no time window to smoke-test the new revision before it goes
live to real visitors.

This document explains how the pipeline avoids that flat-cutover risk.

## The flow

```
Build  ->  Deploy (new revision @ 0% traffic)
       ->  Smoke (new revision FQDN, no prod traffic involved)
       ->  ManualValidation (approval gate)
       ->  ShiftTraffic (100% to new revision)
       ->  Smoke (production URL post-promote)
       ->  Evidence
```

The Container App is configured for **multi-revision mode** so that an
update creates a new revision while the previous revision keeps serving
100% of traffic. The pipeline's `Deploy` stage explicitly sets
`revisions-mode=multiple` (idempotent) before each deploy.

## Why the new revision starts at 0% traffic

In multi-revision mode, `az containerapp update --revision-suffix <s>`
creates a new revision but does **not** automatically shift traffic to
it — existing traffic remains on whatever revisions currently have
weight > 0. As a defensive measure, the pipeline also explicitly pins
the previous revision at 100% and the new revision at 0% before moving
on, so even on the first transition from single → multi mode the new
revision cannot accidentally take production traffic.

## Smoke testing the new revision

Each new revision in ACA gets its own per-revision FQDN, distinct from
the production app FQDN. The pipeline captures the new revision's FQDN
from `az containerapp revision show ... --query properties.fqdn` and
smokes it directly:

| Route | Expected | Source |
|---|---|---|
| `/` | 200 + body contains `InsightPulse` | SPA homepage |
| `/security` | 301 → `/#security` | Server redirect (Scope A) |
| `/subprocessors` | 301 → `/#subprocessors` | Server redirect (Scope A) |
| `/llms.txt` | 200 (text/plain) | Static file (Scope A) |
| `/sitemap.xml` | 200 (text/xml) | Static file (Scope A) |
| `/robots.txt` | 200 (text/plain) | Static file (Scope A) |
| `/features` | 301 → `/` | Server redirect (Scope A) |

Smoke against the per-revision FQDN does NOT route through production
ingress and does NOT affect real visitors.

## Manual approval gate

After smoke passes, the pipeline pauses at a `ManualValidation@0` step.
The reviewer sees:
- New revision name and FQDN
- Previous revision name (rollback target)
- Approve / Reject options

**Approve** triggers the `PromoteShiftTraffic` stage, which runs:

```bash
az containerapp ingress traffic set \
  --name ipai-website \
  --resource-group rg-ipai-dev-odoo-sea \
  --revision-weight <new-revision>=100
```

After the shift, the pipeline smokes the production URL one more time
to confirm the cutover served the new content correctly, then publishes
evidence.

**Reject** (or timeout — default 72h) leaves the new revision at 0%
traffic. The new revision is preserved in ACA history; production
continues serving the previous revision unchanged. To clean up an
abandoned revision, deactivate it (see Rollback section below).

## Rollback

### Scenario A — production has already been promoted to the new revision and we want to revert

```bash
# 1. Identify the previous good revision.
az containerapp revision list \
  --name ipai-website \
  --resource-group rg-ipai-dev-odoo-sea \
  --query "[?properties.active].{name: name, created: properties.createdTime, weight: properties.trafficWeight}" \
  --output table

# 2. Shift 100% traffic back to the previous good revision.
az containerapp ingress traffic set \
  --name ipai-website \
  --resource-group rg-ipai-dev-odoo-sea \
  --revision-weight <previous-revision>=100

# 3. Smoke the production URL.
curl -sI https://www.insightpulseai.com/
```

### Scenario B — manual approval was rejected; we want to clean up the unused new revision

```bash
# Deactivate the unused new revision (does not delete history).
az containerapp revision deactivate \
  --name ipai-website \
  --resource-group rg-ipai-dev-odoo-sea \
  --revision <new-revision>
```

### Scenario C — partial / canary traffic split (advanced)

The pipeline currently shifts 100% on approval. For a slower canary,
manually run:

```bash
# 10% canary on new revision, 90% on previous good revision.
az containerapp ingress traffic set \
  --name ipai-website \
  --resource-group rg-ipai-dev-odoo-sea \
  --revision-weight <new-revision>=10 <previous-revision>=90
```

A future PR can wire a canary stage into the pipeline if needed.

## Trigger and authority

- **CI/CD authority split per ADR-0010**: GitHub Actions through staging;
  Azure Pipelines for production apply. This pipeline runs in Azure
  Pipelines.
- **Trigger**: pushes to `main` that touch `web/ipai-landing/**`. Changes
  to `azure-pipelines/**` (including this file) do NOT auto-trigger the
  deploy pipeline — they are repo-only.
- **Manual trigger** for revision-safe deploy after a doc-only PR or
  emergency hotfix: `az pipelines run --name web-landing-deploy --branch main`
  (requires Azure DevOps PAT or the dev team's queue access).

## What this does NOT do

- It does NOT change DNS or Azure Front Door routing.
- It does NOT deploy to a separate staging ACA (one does not exist).
- It does NOT modify the shared `templates/jobs/deploy-containerapp.yml`
  template; that template is still used by other pipelines that want
  flat-deploy semantics. Web landing now uses inline `az` calls instead.
- It does NOT auto-promote without manual approval.
- It does NOT autoroll back; rollback is manual per the procedures above.
- It does NOT send notifications; the ManualValidation step is the
  notification surface.

## References

- Azure Container Apps revisions: https://learn.microsoft.com/en-us/azure/container-apps/revisions
- `az containerapp ingress traffic set`: https://learn.microsoft.com/en-us/cli/azure/containerapp/ingress/traffic
- ManualValidation task: https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/manual-validation-v0
- ADR-0010 (CI deploy authority split): see `docs/architecture/adrs/`
