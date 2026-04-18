# FinOps Hub -- Task Breakdown

> Execution tasks derived from `plan.md`. Each task is independently
> verifiable and committed with evidence under `docs/evidence/`.

---

## Phase 0 — Tag Governance

- [ ] T0.1 Resource Graph audit of 63 sponsored-sub resources for missing tags
- [ ] T0.2 Author `infra/azure/policies/require-tenant-tag.bicep` (audit mode first)
- [ ] T0.3 Backfill tags on existing resources via bulk `az tag update`
- [ ] T0.4 Flip policy from `audit` to `deny`; confirm new deployments enforce

## Phase 1 — Hub Deploy

- [ ] T1.1 Vendor `microsoft/finops-toolkit@v13` into `infra/finops-hub/vendor/`
- [ ] T1.2 Author `infra/finops-hub/main.bicep` (consumes upstream `hub` module)
- [ ] T1.3 Parameter file for sub `eba824fb`, region SEA, RG `rg-ipai-dev-mon-sea`
- [ ] T1.4 Pipeline `azure-pipelines/finops-hub-deploy.yml` (what-if → approval → apply)
- [ ] T1.5 Grant hub MI `Storage Blob Data Contributor` on `stdevipai`
- [ ] T1.6 Create Cost Management daily FOCUS export → `stdevipai/finops/`
- [ ] T1.7 Evidence: `docs/evidence/<stamp>/finops/phase1/` with deploy logs + first export file listing

## Phase 2 — Power BI

- [ ] T2.1 Create `wks-ipai-finops` Power BI workspace
- [ ] T2.2 Deploy upstream Power BI starter via `fabric-deploy` skill
- [ ] T2.3 Add IPAI-specific slicer: tenant (W9 / Prismalab / Pulser / shared)
- [ ] T2.4 Publish + share with `finance@w9studio.net`, `accounts@w9studio.net`
- [ ] T2.5 Evidence: screenshot + link committed

## Phase 3 — Alerts

- [ ] T3.1 Budget (80/95/100%) via Bicep, routed to `ag-ipai-dev-sea`
- [ ] T3.2 Deploy upstream FinOps Alerts (idle VMs, stopped SQL, orphaned disks)
- [ ] T3.3 Custom rule: ACA revisions in `Failed` state
- [ ] T3.4 Slack webhook sink (via `apps/slack-agent/`)
- [ ] T3.5 Simulated breach test; verify Slack alert arrival time ≤ 4h

## Phase 4 — Fabric Mirror + Pulser

- [ ] T4.1 Register FOCUS tables in Unity Catalog (`catalog=ipai, schema=finops`)
- [ ] T4.2 Enable Fabric OneLake mirror on `finops` schema
- [ ] T4.3 Add FOCUS tables to MCP Knowledge source registry
- [ ] T4.4 Wire `finance-fpa-analyst` persona into Pulser as grounded surface
- [ ] T4.5 Authoring `agents/evals/finops/eval-v1.jsonl` (20 Q&A against ground truth)
- [ ] T4.6 Pass rate ≥ 90% before enabling in prod

## Phase 5 — Optimization Loop

- [ ] T5.1 Monthly report job (Azure Function or Logic App, Azure-native)
- [ ] T5.2 First month committed under `docs/evidence/<YYYYMM>/finops/report.md`
- [ ] T5.3 Recommendations routed to ADO Boards backlog tag `area/finops`
- [ ] T5.4 Savings-realized metric tracked on Power BI exec page

## Cross-cutting

- [ ] X.1 No secrets committed (repo scan pre-merge gate)
- [ ] X.2 All bicep passes `azure-runtime-review` skill checks
- [ ] X.3 `azure-principal-architect` review sign-off on Phase 1 architecture
- [ ] X.4 SSOT update: add `finops` domain to `docs/architecture/SSOT_BOUNDARIES.md`
- [ ] X.5 Update `ssot/repo/github-org-inventory.yaml` with `infra/finops-hub/` path
