# Runbook — GitHub Actions billing via Azure subscription

**Status:** Required before any GHA workflow is created under the scoped exception.
**Authority:** `CLAUDE.md` §"Engineering & Delivery Authority (REVISED 2026-04-16)" + `ssot/governance/gha-scoped-exception.yaml`
**Rev:** 2026-04-16

---

## Outcome

GitHub Actions minutes billed against an Insightpulseai Azure subscription, with budget alerts and monthly spending cap. No direct-to-GitHub billing for GHA.

---

## Prerequisites

- Org admin on `Insightpulseai` GitHub organization
- Azure subscription with billing admin rights (Sponsored or Pay-As-You-Go)
- Subscription ID documented (pick one: `<sub-id>`)
- Azure tenant ID (`<tenant-id>`)

---

## Steps (one-time setup, ~15 min)

### 1. Link Azure subscription to GitHub org billing

1. GitHub Org → Settings → **Billing and plans** → **Spending limits**
2. Click **Add payment method** → select **Azure Subscription**
3. Sign in to Azure (same tenant as IPAI infra)
4. Select the subscription — recommend **Pay-As-You-Go** (Sponsored subs may not support GHA metered billing; verify in Microsoft docs at publish time)
5. Confirm. GitHub shows "Billed through Azure subscription: `<sub-id>`"

### 2. Set spending limits (defense against runaway)

1. GitHub Org Billing → **GitHub Actions** → **Manage spending limit**
2. Set monthly cap: **$50** for R2 (tighten later as usage patterns emerge)
3. Enable notification at **50%** and **90%** thresholds

### 3. Configure Azure budget alerts

```bash
az account set --subscription <sub-id>

az consumption budget create \
  --budget-name gha-monthly-50usd \
  --amount 50 \
  --time-grain Monthly \
  --start-date $(date +%Y-%m-01) \
  --end-date $(date -v+1y +%Y-%m-01) \
  --category Cost \
  --notification \
    enabled=true \
    threshold=80 \
    operator=GreaterThan \
    contact-emails=platform-engineering@insightpulseai.com \
    notification-type=Actual

# Repeat for forecast alert at 100% (early warning)
```

### 4. Verify meter appears in Cost Management

1. Azure Portal → Cost Management → Cost analysis
2. Filter: **Meter category = "GitHub Actions"**
3. After first workflow run (see §Validation), non-zero usage should appear within 24-48h

### 5. Document in the governance register

1. Update `ssot/governance/gha-scoped-exception.yaml` → `hard_conditions.billing.configuration_steps` with the actual sub-id used (redact if sensitive, reference KV secret if stored)
2. Commit with message: `chore(governance): record GHA Azure-subscription billing sub-id`

---

## Validation

Create a trivial validation workflow in a sandbox repo (not production):

```yaml
# .github/workflows/billing-validation.yml
name: billing-validation
on:
  workflow_dispatch:
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - run: echo "GHA billing validation $(date)"
```

Trigger manually. Wait 24-48h. Check:
1. Azure Cost Management shows non-zero "GitHub Actions" line item
2. GitHub Org → Billing shows spend under the configured subscription
3. Neither the $50 monthly cap nor the 80% alert has tripped on a single trivial run

Delete the validation workflow after confirmation.

---

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| GitHub billing page shows "no payment method" after linking | Tenant mismatch | Ensure Azure login was to the same tenant that owns IPAI infra |
| "Sponsored subscriptions don't support metered billing" | Known MS limitation | Use a Pay-As-You-Go sub instead; document which one |
| Azure budget alert never fires | Delayed meter emission | Budgets evaluate daily; allow 24-48h after first workflow |
| GHA workflow runs but no Azure meter appears | Billing configuration incomplete | Recheck step 1; may need to re-link if initial attempt failed silently |
| Spending cap hit unexpectedly | Cache misses, matrix explosion | Audit workflow; reduce matrix; cache dependencies; consider moving to Azure Pipelines |

---

## Rollback

If the scoped exception proves too costly / noisy:

1. Remove all GHA workflow files from `.github/workflows/` (except non-CI config)
2. Update `ssot/governance/gha-scoped-exception.yaml` → `status: revoked`
3. Revert `CLAUDE.md` §"Engineering & Delivery Authority" to the 2026-04-14 absolute-forbidden version
4. GitHub Org Billing → **Remove Azure subscription payment method** (optional; keeps room to flip back quickly)
5. Document rollback in `docs/evidence/<stamp>/gha-rollback/` with cost report + reason

---

## Ownership

- **Owner (runbook):** platform-engineering@insightpulseai.com
- **Owner (billing subscription):** record in `ssot/governance/gha-scoped-exception.yaml`
- **Approver (new workflows):** platform-engineering team via PR review

---

## Anchors

- `CLAUDE.md` §"Engineering & Delivery Authority (REVISED 2026-04-16)"
- `ssot/governance/gha-scoped-exception.yaml`
- `ssot/governance/ci-cd-authority-matrix.yaml`
- Azure Cost Management docs: https://learn.microsoft.com/azure/cost-management-billing/
- GitHub Actions billing docs: https://docs.github.com/en/billing/managing-billing-for-github-actions/
