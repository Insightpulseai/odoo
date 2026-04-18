# FinOps Hub -- Implementation Plan

> Phased delivery plan for IPAI cost observability on Microsoft Azure Sponsorship.

---

## Phase 0: Tag Governance Prep (prerequisite)

**Goal:** All billable resources carry allocation tags.

- Audit 63 resources for `tenant`, `cost_center`, `env` tags via Resource Graph
- Apply missing tags via `infra/azure/policies/` Azure Policy definitions
- Gate future resource creation on tag presence (deny policy)

**Exit:** `az graph query "Resources | where tags !has 'tenant' | count"` returns 0.

## Phase 1: Upstream Hub Deploy

**Goal:** Production FinOps Hub running in `rg-ipai-dev-mon-sea`.

- Pin `microsoft/finops-toolkit` at v13 in `infra/finops-hub/vendor/`
- Author `infra/finops-hub/main.bicep` consuming upstream modules
- Parameter file for sponsored sub (`eba824fb`) + SEA region
- Azure Pipeline `azure-pipelines/finops-hub-deploy.yml` with what-if + approval gate
- Wire managed identity to `stdevipai` storage + `stipaidevlake` lake
- Create Cost Management daily export targeting the hub's ingest container

**Exit:** Hub resources deployed; first FOCUS daily export visible in `stdevipai/finops/`.

## Phase 2: Power BI Dashboards

**Goal:** Business-facing cost visibility.

- Provision Power BI workspace `wks-ipai-finops`
- Deploy upstream Power BI starter templates via `fabric-deploy` skill
- Customize: per-tenant slicer (W9, Prismalab, Pulser, shared), per-RG spend, idle-resource view
- Publish to Fabric capacity; share with finance operators

**Exit:** Dashboard accessible at `app.powerbi.com/.../wks-ipai-finops` with last-30-day RG spend.

## Phase 3: Alerts and Idle Detection

**Goal:** Proactive cost protection.

- Budget alerts (80% / 95% / 100%) via `ag-ipai-dev-sea` Action Group
- Upstream FinOps Alerts deployment for idle resources
- Custom rule: flag ACA revisions in `Failed` state (covers `ipai-w9studio-dev` class of leak)
- Slack integration via existing Slack agent for alert delivery

**Exit:** Simulated 80% budget breach triggers Slack alert within 4h.

## Phase 4: Fabric Mirror + Pulser Grounding

**Goal:** Cost data becomes conversational via Pulser finance copilot.

- Register FOCUS tables in Unity Catalog; enable OneLake mirror
- Expose via MCP Knowledge/Retrieval layer (`consumed_by: [app-pulser-erp]`)
- Add `finance-fpa-analyst` persona (from `.claude/agents/upstream/agency/`) as grounded copilot surface
- Evals in `agents/evals/finops/` verifying accuracy vs Cost Management ground truth

**Exit:** Pulser answers "what did `ipai-odoo-dev` cost last week?" within ±2% of ground truth.

## Phase 5: Optimization Feedback Loop

**Goal:** Close the optimize-measure-optimize loop.

- Monthly `finance-fpa-analyst` report committed to `docs/evidence/<YYYYMM>/finops/`
- Roadmap of recommended decommissions → feeds Azure DevOps Boards backlog
- Track savings realized per month
