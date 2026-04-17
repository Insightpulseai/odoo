# Runbook — Fabric workspace + FinOps FOCUS cost export

> Closes Issue 27 (Fabric capacity) + adds FinOps FOCUS cost tracking lane.
> Two ships: (a) FOCUS cost export to ADLS (no Fabric needed), (b) Fabric capacity
> provisioning when user commits to the spend.
> Source: https://learn.microsoft.com/en-us/cloud-computing/finops/fabric-workspace
> Locked 2026-04-15.

---

## 0. Scope

| Deliverable | Depends on Fabric capacity? | Status |
|---|---|---|
| FOCUS cost export → ADLS | No — uses Cost Management + Storage only | **Ship now** |
| Lakehouse shortcut to FOCUS data | Yes — Fabric workspace required | Blocked on #1 |
| Power BI FOCUS report | Yes — Power BI workspace + Fabric | Blocked |
| Semantic model for Pulser "Cost per agent request" KPI | Yes — Fabric | Blocked |
| Fabric Data Agent wrapping UC metrics | Yes — Fabric F2+ | Blocked |

**Operator decision required:** Fabric trial expires ~2026-05-20. Either:
- Provision paid Fabric capacity (F2 starts ~USD $262.80/month)
- Rely on Databricks-only path for analytics + skip Fabric Data Agent surface (accept loss of M365 Copilot Analyst integration)

---

## 1. FOCUS cost export — ship now (no Fabric needed)

### 1.1 Prerequisites (verify before running)

- Owner on target Azure subscription (verified — user is Subscription Owner on both IPAI subs)
- Storage Blob Data Contributor on target storage account OR use Account Key auth
- Existing ADLS Gen2 storage account with HNS enabled

### 1.2 Target storage — canonical choice

Per live inventory (2026-04-15):

| Storage account | Sub | RG | Region | HNS | Use |
|---|---|---|---|---|---|
| `stlkipaidev` | Sponsorship | `rg-ipai-dev-data-sea` | SEA | Verify | **Canonical lake — use this for FOCUS exports** |
| `stipaidevagent` | Sponsorship | `rg-ipai-dev-data-sea` | SEA | Yes | Agent artifacts (BIR PDFs, DATs) — don't mix with FOCUS |
| `stipaidevlake` | — | — | — | **DOES NOT EXIST** | Referenced in UC but missing — see §4 drift note |

### 1.3 Create FOCUS export via Azure Cost Management

```bash
az account set --subscription "Azure subscription 1"  # PAYG has more cost-relevant resources
SUB_ID=$(az account show --query id -o tsv)
STORAGE_ID=$(az storage account show -n stlkipaidev -g rg-ipai-dev-data-sea --subscription "Microsoft Azure Sponsorship" --query id -o tsv)

# Create FOCUS-format cost export on PAYG subscription
az costmanagement export create \
  --name ipai-focus-cost-payg \
  --type "FocusCost" \
  --scope "/subscriptions/$SUB_ID" \
  --storage-account-id "$STORAGE_ID" \
  --storage-container "msexports" \
  --storage-directory "focuscost/subscription-$SUB_ID" \
  --timeframe "MonthToDate" \
  --recurrence "Daily" \
  --recurrence-period from="2026-04-15" to="2027-04-15" \
  --format "Csv" \
  --compression-mode "None"
```

Repeat for the Sponsorship subscription with different scope + directory. Result: daily FOCUS CSV exports land in `stlkipaidev/msexports/focuscost/subscription-<id>/<YYYY-MM>/focus-cost.csv`.

### 1.4 Trigger first export manually

```bash
az costmanagement export execute --name ipai-focus-cost-payg --scope "/subscriptions/$SUB_ID"
```

### 1.5 Verification

```bash
az storage blob list \
  --account-name stlkipaidev \
  --container-name msexports \
  --prefix focuscost/ \
  --auth-mode login -o table | head -10
```

Expected: CSV file present at `focuscost/subscription-<id>/<YYYY-MM>/*.csv`.

---

## 2. Fabric capacity provisioning (when user commits)

### 2.1 Decision needed

| Option | SKU | Cost (USD/mo, estimated) | When to pick |
|---|---|---|---|
| Extend Fabric trial | Trial F64 equiv | Free (expires ~2026-05-20) | Temporary — same-as-today; demo purposes only |
| F2 production | Microsoft.Fabric/capacities `F2` | ~$262.80 pay-as-you-go | TBWA pilot confirmed, Fabric Data Agent path needed |
| F4 | `F4` | ~$525.60 | Multi-customer production |
| F8+ | `F8` | ~$1051.20 | Scale |

**Recommendation: F2 for 1-2 months, evaluate usage, then decide on F4 or higher.**

### 2.2 Bicep deploy (when ready)

```bicep
// infra/azure/fabric-capacity.bicep
targetScope = 'resourceGroup'

param capacityName string = 'fcipaidev'
param location string = 'southeastasia'
param skuName string = 'F2'  // change to F4/F8 per scale decision
param administrators array = ['admin@insightpulseai.com']

resource fabric 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: capacityName
  location: location
  sku: {
    name: skuName
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: administrators
    }
  }
  tags: {
    environment: 'dev'
    product: 'pulser'
    owner: 'platform'
    costCenter: 'ipai-platform'
  }
}
```

Deploy:

```bash
az deployment group create \
  --resource-group rg-ipai-dev-ai-sea \
  --template-file infra/azure/fabric-capacity.bicep \
  --parameters skuName=F2
```

### 2.3 Create Fabric workspace + lakehouse (post-capacity)

Via Fabric portal (after capacity assigned) — no az CLI path:

1. Sign in to https://app.fabric.microsoft.com
2. Create workspace `fcipaidev` with capacity `fcipaidev` attached
3. Create lakehouse `ipai-finance-ppm-lakehouse`
4. Create shortcuts:
   - To `stlkipaidev/msexports/focuscost/` (FOCUS cost data)
   - To Databricks `ipai_dev.gold` (via Databricks-to-Fabric mirroring OR direct shortcut)

### 2.4 Power BI semantic model

Per `docs/architecture/semantic-layer.md §3`:
- Semantic model reads from Unity Catalog metric views (`ipai_dev.metrics.*`)
- NOT from local DAX measures — UC is the single source of truth

---

## 3. FinOps KPIs to track

### 3.1 Platform spend (IPAI infra)

| KPI | Source | Target |
|---|---|---|
| Monthly Azure spend | FOCUS / Cost Management | < budget |
| Spend by service (ACA, PG, Foundry, Databricks, AI Search) | FOCUS breakdown | — |
| Spend by tag (product, costCenter, environment) | FOCUS + resource tags | — |
| Reserved instance coverage | Advisor + FOCUS | ≥ 60% where applicable |

### 3.2 Per-agent cost (Pulser ops — Kira's "Cost per analysis request")

| KPI | Source | Target |
|---|---|---|
| Cost per Pulser Finance agent run | `appi-ipai-dev-agent-sea` custom metrics + Foundry token usage | < $0.10 |
| Cost per BIR filing generated | ops.agent_run × resource consumption | < $0.50 |
| GPT-4.1 vs GPT-4.1-mini usage ratio | Foundry deployment metrics | Mini ≥ 70% of total calls (volume-tier policy) |

These KPIs depend on joining:
- FOCUS cost data (by resource + tag)
- Foundry telemetry (token usage per deployment)
- Pulser trace data (`appi-ipai-dev-agent-sea` — per agent_run attribution)

All three plane into Unity Catalog metrics (once DLT pipeline populates Bronze/Silver/Gold per Issue 26).

---

## 4. Known drift (must fix before DLT first run)

`ipai-lake-dev` Unity Catalog external location points to `abfss://gold@stipaidevlake.dfs.core.windows.net/` — but `stipaidevlake` storage account **does not exist** on either subscription.

Three fix options:

| Option | Action | Pros | Cons |
|---|---|---|---|
| A | Create storage account `stipaidevlake` with HNS on Sponsorship | Matches existing UC references | New Azure resource; naming inconsistent with `stlkipaidev` |
| B | Recreate UC catalog `ipai_dev` pointing at `stlkipaidev` (existing) | Uses canonical lake | Requires UC catalog delete + recreate + reassigning schemas |
| C | Add a new UC external location `ipai-lake-sponsorship` on `stlkipaidev`, leave `ipai-lake-dev` for future | Additive, doesn't break existing | Two lake paths long-term |

**Recommend Option B** — cleaner canonical state; the Unity Catalog was just bootstrapped yesterday so recreation cost is low.

Blocked on: user decision.

---

## 5. Operator checklist

**Ship now (no Fabric spend):**
- [ ] Decide A/B/C for `stipaidevlake` drift (§4)
- [ ] Create FOCUS exports for both IPAI subs → `stlkipaidev/msexports/focuscost/` (§1.3)
- [ ] Verify first export landed (§1.5)

**Decide this week (before 2026-05-20 Fabric trial expiry):**
- [ ] Provision Fabric F2 via Bicep (§2.2) OR accept no-Fabric path for analytics
- [ ] If provisioned: create Fabric workspace + lakehouse + shortcuts (§2.3)

**Ship after Fabric capacity exists:**
- [ ] Power BI semantic model on UC metrics
- [ ] Fabric Data Agent wrapping `ipai_dev.metrics.*` (→ M365 Copilot Analyst surface)
- [ ] Finance PPM dashboard for TBWA\SMP + internal use

---

## 6. Related

- `docs/architecture/semantic-layer.md` — Unity Catalog as canonical metric layer
- `docs/architecture/data-model-erd.md` — §0.2 storage account inventory
- `docs/evidence/20260415-uc-bootstrap/` — UC catalog creation evidence
- `docs/runbooks/foundry-connections-and-tools.md` — Foundry integration
- `platform/contracts/cdm-entity-map.yaml` — CDM Gold projection SSOT
- `ssot/governance/upstream-adoption-register.yaml` — FinOps toolkit / unified-data-foundation entries
- Memory: `project_fabric_finance_ppm` (Fabric trial state)

---

*Runbook locked 2026-04-15. Next refresh when (a) user decides on Fabric capacity provisioning OR (b) `stipaidevlake` drift is resolved.*
