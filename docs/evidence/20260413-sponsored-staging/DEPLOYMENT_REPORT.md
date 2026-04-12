# Sponsored Staging Deployment — 2026-04-13

**Subscription:** `Microsoft Azure Sponsorship` (`eba824fb-332d-4623-9dfb-2c9f7ee83f4e`)
**Tenant:** `402de71a-87ec-4302-a609-fb76098d1da7`
**Region:** `southeastasia`
**Executor:** `admin@insightpulseai.com` via az CLI

---

## 1. What merged

**Nothing.** No mergeable PRs exist that are blocked only by systemic CI noise.

| PR | State | Reason not merged |
|---|---|---|
| [#703](https://github.com/Insightpulseai/odoo/pull/703) `fix(copilot): wire Document Intelligence + enforce cross-repo PPM sourcing` | `CONFLICTING / DIRTY` | 61 commits behind `main`, diff >300 files — genuine semantic conflict. Per mission rule "Do not merge conflicted or semantically broken work." Left blocked. |

Cross-org search returned no additional open PRs in reachable repos. Session's prior 7 PRs (#714–#732) already merged on `main`.

## 2. What deployed

Four resources created in `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` / `southeastasia`:

| Type | Name | Resource group | Purpose |
|---|---|---|---|
| Resource group | `rg-ipai-stg-odoo-runtime` | — | Staging runtime RG |
| Resource group | `rg-ipai-stg-odoo-data` | — | Staging data RG |
| `Microsoft.OperationalInsights/workspaces` | `log-ipai-stg` | `rg-ipai-stg-odoo-runtime` | ACA env log sink (required dependency) |
| `Microsoft.App/managedEnvironments` | `ipai-stg-env` | `rg-ipai-stg-odoo-runtime` | ACA managed environment — minimum runtime substrate |

### ACA environment
- **Name:** `ipai-stg-env`
- **Default domain:** `happycoast-577e3b67.southeastasia.azurecontainerapps.io`
- **Provisioning state:** `Succeeded`
- **Region:** `Southeast Asia`
- **Log Analytics:** `log-ipai-stg` (customerId `213d8af6-a91d-4548-8498-d13c8d4c7133`)

### Tagging (canonical baseline from `ssot/azure/tagging-standard.yaml`)

All 4 resources carry the same required+recommended tag set:

```
env                 = staging
app                 = platform-shared
costcenter          = 55332
owner               = platform@insightpulseai.com
data-classification = internal
businessunit        = ipai
managed-by          = azcli
created-date        = 2026-04-13
repo                = Insightpulseai/odoo
```

Note: Azure CLI additionally writes `managedBy: cli` on RGs (system metadata, harmless).

## 3. What validated

| Check | Result |
|---|---|
| Subscription accessible | ✓ `Microsoft Azure Sponsorship` visible from `admin@insightpulseai.com` |
| Target RGs created | ✓ Both RGs reach `Succeeded` state |
| Log Analytics workspace | ✓ Provisioned, customerId captured |
| ACA env reaches Succeeded | ✓ Confirmed via `az containerapp env show` |
| Tags applied per canonical schema | ✓ 9 required+recommended tags on every resource |
| `id-ipai-dev` Contributor on sponsored sub | ✓ `az role assignment list` confirms |
| `id-ipai-dev` AcrPull on `acripaiodoo` | ✓ Role assignment present on prod-sub registry |
| Default branch protection on main | — **Disabled** (confirmed via `gh api /branches/main/protection` → 404) |

## 4. What remains blocked

### Blocker 1 — Vercel deprecated status check pollution
- **Symptom:** Every PR to `main` receives a red `Vercel / failure` status check from `vercel.com/tbwa/insightpulseai-web` (deprecated TBWA project).
- **Impact:** Cosmetic — branch protection is disabled so Vercel doesn't *block* merges, but `UNSTABLE` status clutters every PR and trains reviewers to ignore check failures.
- **Source:** External Vercel GitHub integration/app on the repo. No `vercel.json`, no `.vercel/`, no workflow file references it.
- **One concrete next action:** Owner visits https://vercel.com/tbwa/insightpulseai-web/settings/git and clicks **Disconnect Git Repository** (or alternatively, GitHub repo → Settings → Integrations → Vercel → Configure → remove `Insightpulseai/odoo` from the project's repo list). Zero CLI path for this — requires Vercel dashboard access by the project owner.

### Blocker 2 — PR #703 genuinely conflicted
- **Symptom:** 61 commits behind main, `MergeStateStatus: DIRTY`, `>300 files` in diff.
- **Impact:** Cannot be merged without a manual rebase/recreate.
- **One concrete next action:** Author closes #703, re-opens a focused PR containing only the Document Intelligence wiring (small change), against current main. The cross-repo PPM sourcing work belongs in a separate PR.

### Blocker 3 — Staging DB + ACR pull path end-to-end validation
- **Symptom:** No app deployed yet — the ACA env is empty. Cannot confirm end-to-end `acripaiodoo → staging ACA` image pull until a real container app is deployed.
- **Impact:** The "prove staged rollout capability" objective from the mission is partially satisfied (env ready) but not fully closed (no app deployed yet to prove a full pull+start cycle).
- **One concrete next action:** Deploy a single ACA app (e.g., a smoke-test image or a clone of `ipai-bot-proxy-dev`) into `ipai-stg-env` referencing `acripaiodoo.azurecr.io/ipai-bot-proxy:latest` with `id-ipai-dev` as the pull identity. First Deploy is a revision-create; ~2 min. If image pulls and starts, the staged rollout substrate is fully validated.

### Blocker 4 — PostgreSQL Flexible Server for staging (out of scope for this slice)
- **Symptom:** `rg-ipai-stg-odoo-data` is empty.
- **Impact:** Odoo staging app cannot be deployed until a staging PG exists.
- **Deliberate deferral:** Per mission rule "only if required by the chosen deployment slice" — this slice validates the ACA+logging substrate, not a full Odoo staging instance. PG should land in a separate focused PR (`infra/azure/deploy-stg-postgres.bicep`).
- **One concrete next action:** When Odoo-staging clone work begins, deploy via `az postgres flexible-server create -n pg-ipai-stg -g rg-ipai-stg-odoo-data -l southeastasia --sku-name Standard_D2ds_v5 --tier GeneralPurpose --storage-size 32 --version 16 --administrator-login odooadmin --administrator-login-password <from kv-ipai-dev/stg-pg-admin-password>` + canonical tags + Fabric mirroring config to match prod `pg-ipai-odoo` architecture.

## 5. Recommended immediate next 3 actions

1. **Owner disconnects Vercel GitHub integration** from https://vercel.com/tbwa/insightpulseai-web/settings/git — removes the cosmetic failure status from all future PRs and closes the CI-hygiene mission item cleanly.
2. **Deploy a single test container app** into `ipai-stg-env` pulling `acripaiodoo.azurecr.io/ipai-bot-proxy:latest` via `id-ipai-dev`. Validates the cross-subscription ACR pull path end-to-end. Single `az containerapp create` call; reversible.
3. **Author re-scopes PR #703** into two focused PRs — one for the Document Intelligence wiring (small, reviewable), one for the cross-repo PPM sourcing rules (spec bundle update). Close #703 as-is; both replacement PRs will merge clean against current main.

---

## Execution evidence

### Commands executed (in order)

```bash
az account set --subscription eba824fb-332d-4623-9dfb-2c9f7ee83f4e

az group create -n rg-ipai-stg-odoo-runtime -l southeastasia --tags ...
az group create -n rg-ipai-stg-odoo-data    -l southeastasia --tags ...

az monitor log-analytics workspace create -n log-ipai-stg \
  -g rg-ipai-stg-odoo-runtime -l southeastasia --tags ...

az containerapp env create -n ipai-stg-env \
  -g rg-ipai-stg-odoo-runtime -l southeastasia \
  --logs-workspace-id <id> --logs-workspace-key <key> --tags ...

# tag reconciliation (original `--tags "$STR"` collapsed 9 pairs into 1):
az group update         -n <rg>  --set tags.env=staging tags.app=platform-shared ...
az resource tag  --ids <ws-id>   --tags env=staging app=platform-shared ...
az containerapp env update -n ipai-stg-env -g rg-ipai-stg-odoo-runtime --tags env=staging ...

az account set --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070  # return to prod context
```

### Validation snapshots

```
$ az containerapp env show -n ipai-stg-env -g rg-ipai-stg-odoo-runtime \
    --query "{state:properties.provisioningState, fqdn:properties.defaultDomain}"
{
  "state": "Succeeded",
  "fqdn": "happycoast-577e3b67.southeastasia.azurecontainerapps.io"
}

$ az role assignment list --assignee 1aee831f-3813-4eed-b49c-f7665330f0f6 \
    --scope "/subscriptions/eba824fb-332d-4623-9dfb-2c9f7ee83f4e"
Contributor

$ az role assignment list --assignee 1aee831f-3813-4eed-b49c-f7665330f0f6 \
    --scope "/subscriptions/536d8cf6.../registries/acripaiodoo"
AcrPull
```

---

*Report generated 2026-04-13 by Claude Code agent session.*
*Canonical tagging standard: [ssot/azure/tagging-standard.yaml](../../../ssot/azure/tagging-standard.yaml)*
*Audit tool: [scripts/azure/audit-tags.sh](../../../scripts/azure/audit-tags.sh)*
