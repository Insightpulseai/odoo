# Runbook — FinOps baseline

> Turns FinOps from concept into implementation order.
> Companion: `docs/architecture/completeness-matrix-finance-projectops-data-intel-finops.md`.
> Reference: https://learn.microsoft.com/en-us/cloud-computing/finops/
> Locked 2026-04-15.

---

## 0. What this runbook does

FinOps is the full cloud-financial practice:

```
ingestion → allocation → reporting/analytics → anomaly → forecasting/budgeting → governance/onboarding → chargeback
```

This runbook defines the **order we build each capability**, the **artifacts that prove it's live**, and the **gates Azure Pipelines enforces**. Reuses upstream `microsoft/finops-toolkit` per `ssot/governance/upstream-adoption-register.yaml`.

---

## 1. Capability build order

| Step | Capability | State | Owner artifact | Gate |
|---|---|---|---|---|
| 1 | **Ingestion — FOCUS export** | ✅ Live (PAYG) | `ipai-focus-cost-payg` cost-management export → `stipaidevlake/msexports/focuscost/subscription-<payg-id>/` | `azure-pipelines/templates/finops-export-validate.yml` |
| 2 | **Ingestion — workload-onboarding SSOT** | In progress | `ssot/finops/workload-onboarding.yaml` | Schema lint in `bicep-lint-validate.yml` |
| 3 | **Allocation model** | In progress | `platform/contracts/finops/cost-allocation-model.yaml` | Tag-policy check (required tags: `product`, `costCenter`, `environment`, `owner`) |
| 4 | **Reporting / analytics** | Blocked on Fabric F2 | `docs/runbooks/fabric-finops-workspace.md §3` | Power BI semantic model on UC `ipai_dev.metrics.*` |
| 5 | **Anomaly management** | Pending | Alert rules on `appi-ipai-dev-agent-sea` + scheduled actions | Synthetic spike test |
| 6 | **Forecasting / budgeting** | Pending | Monthly budget × tenant × product | Variance > 20% triggers review |
| 7 | **Governance / onboarding** | Pending | `ssot/finops/workload-onboarding.yaml` + quarterly review cadence | Workload-onboarding checklist CI check |
| 8 | **Chargeback** | Future | `ipai_finance_chargeback` module | N/A until step 7 lives |

---

## 2. Ingestion — operational state

### 2.1 Active exports (verified 2026-04-15)

| Export name | Sub | Format | Dest | Recurrence | Status |
|---|---|---|---|---|---|
| `ipai-focus-cost-payg` | PAYG (`536d8cf6` — deleted 2026-04-18) | FOCUS CSV | `stipaidevlake/msexports/focuscost/subscription-536d8cf6-89e1-4815-aef3-d5f2c5f4d070/` | Daily | **Decommissioned** — sub deleted |
| (none) | Sponsorship (`eba824fb`) | — | — | — | **Blocked** — offer MS-AZR-0036P unsupported by Cost Management FOCUS API |

### 2.2 Sponsorship-sub workaround

Sponsorship cost data is **not available via Cost Management exports** (offer exclusion). Two paths to close the gap:

1. **Keep PAYG as canonical cost surface** — accept that Sponsorship burn is only visible via the Azure portal Cost Analysis blade. Most IPAI infra spend (ACA runtime, PG, Foundry) lives on PAYG, so residual blindness is tolerable near-term.
2. **Migrate Sponsorship workloads to PAYG** — aligns with `project_sponsored_sub_migration_adr.md` (ADR-002 A/no/safe-first). Databricks + storage already on Sponsorship; migrating them has cost implications. Deferred until after Fabric decision.

### 2.3 Verification

```bash
az storage blob list \
  --account-name stipaidevlake \
  --container-name msexports \
  --prefix focuscost/ \
  --auth-mode login -o table
```

Expected by tomorrow: CSV at `focuscost/subscription-<payg-id>/<YYYY-MM>/*.csv`.

---

## 3. Allocation model (to implement)

Target allocation dimensions (see `platform/contracts/finops/cost-allocation-model.yaml` for SSOT):

- **Subscription** (PAYG = agent runtime; Sponsorship = data plane)
- **Resource group** (5+1 RG model — `rg-ipai-dev-odoo-runtime`, `rg-ipai-dev-data-sea`, `rg-ipai-dev-ai-sea`, `rg-ipai-dev-platform`, etc.)
- **Product tag** — `pulser`, `odoo`, `prismalab`, `w9`
- **Cost center tag** — `ipai-platform`, `ipai-finance`, `ipai-research`
- **Environment tag** — `dev`, `staging`, `prod`
- **Owner tag** — team or persona (`platform`, `finance`, `research`)
- **Tenant** (res.company mapping from Odoo — IPAI=1, W9=2, OMC=3, TBWA\SMP=4)

Required tag set is enforced by Azure Policy (see `infra/azure/policy/`).

---

## 4. Reporting (blocked on Fabric F2)

Per `docs/runbooks/fabric-finops-workspace.md`:
- Fabric trial expires ~2026-05-20
- F2 SKU ~USD $262.80/mo pay-as-you-go
- Decision required before trial expiry: provision OR accept no-Fabric analytics path

Power BI FinOps workspace dashboards (once Fabric attached):
- Monthly Azure spend (target: < budget)
- Spend by service (ACA, PG, Foundry, Databricks, AI Search)
- Spend by tag (product, costCenter, environment)
- Reserved-instance coverage (target: ≥ 60% where applicable)
- Per-agent cost (cost per Pulser Finance run — target < $0.10)
- Per-BIR-filing cost (target < $0.50)

---

## 5. Anomaly management (to implement)

| Signal | Threshold | Action |
|---|---|---|
| Daily spend spike | > 2× trailing 7-day avg | Alert to `appi-ipai-dev-agent-sea` → platform oncall |
| New service introduced | Any resource.type not in allowlist | Block via Azure Policy |
| Tag compliance | < 100% | Fail azure-pipelines deploy gate |
| Budget variance | > 20% over monthly | Review + scale-down runbook |

---

## 6. Forecasting / budgeting (to implement)

- **Tenant × product monthly budget** in `ssot/finops/budgets.yaml` (to write)
- **Variance view** — Power BI dashboard per §4
- **Review cadence** — weekly for dev, monthly for prod
- **Forecast horizon** — 90 days rolling

---

## 7. Governance / onboarding (to implement)

Every new workload onboarded to IPAI platform must pass the workload-onboarding checklist (`ssot/finops/workload-onboarding.yaml`):

- [ ] Tagged with `product`, `costCenter`, `environment`, `owner`
- [ ] Allocated to a tenant (res.company)
- [ ] Budget line-item created
- [ ] Observability wired (App Insights / Log Analytics)
- [ ] Deprovisioning runbook documented

---

## 8. Azure Pipelines gates

| Pipeline | What it validates | File |
|---|---|---|
| `finops-export-validate` | FOCUS CSV landed; schema parses; totals plausible | `azure-pipelines/templates/finops-export-validate.yml` |
| `bicep-lint-validate` | `az bicep build` + `what-if` on all infra Bicep modules | `azure-pipelines/templates/bicep-lint-validate.yml` |
| `uc-external-location-smoke` | UC external location resolves; `SELECT 1` succeeds | (pending) |
| `tag-policy-gate` | Required tags present on all Microsoft.Storage/ACA/PG resources | (pending) |

---

## 9. Upstream dependencies (adopt, don't fork)

Per CLAUDE.md Engineering Execution Doctrine (reuse first, build the delta only):

- `microsoft/finops-toolkit` — scheduled actions, Power BI reports, data pipelines (clone_as_reference, see `ssot/governance/upstream-adoption-register.yaml`)
- `microsoft/CDM` — schema manifests for FOCUS entity (`focus_cost_v1.cdm.json`)
- `microsoft/unified-data-foundation` — Terraform templates for Databricks + Fabric (strong adopt; time-sensitive)

Do **not** fork. Configure `ipai_*` as thin deltas only.

---

## 10. Definition of done (FinOps baseline)

This runbook is "done" when all of the following hold:

- [x] FOCUS ingestion live on PAYG
- [ ] FOCUS ingestion live on Sponsorship (or formal workaround documented)
- [ ] Allocation model enforced via Azure Policy
- [ ] Power BI FinOps dashboard published
- [ ] Anomaly alerts wired to oncall
- [ ] Monthly budgets loaded; variance dashboard live
- [ ] Workload onboarding checklist in CI gate
- [ ] Chargeback view reporting per tenant

---

*Runbook locked 2026-04-15. Next refresh after Fabric F2 decision resolves §4.*
