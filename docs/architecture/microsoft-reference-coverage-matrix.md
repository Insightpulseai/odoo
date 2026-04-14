# Microsoft Reference Coverage Matrix

> **Authoritative coverage map.** Reconciles three Microsoft reference articles against IPAI's existing ADO epic taxonomy, identifies gaps, and locks the cross-tool doctrine.
>
> **Last updated:** 2026-04-14
> **Anchor:** `spec/pulser-odoo/prd.md` §0 (four-plane), `ssot/azure/bom.yaml`, `docs/backlog/azdo_normalization_matrix.md`

## Cross-tool authority doctrine (canonical)

```
Azure DevOps covers the planning/governance layer, but the Microsoft reference
stack is not Azure DevOps-only:
- Databricks/Fabric is mixed GitHub/Azure DevOps for CI/CD
- Foundry is AI-platform-centric (not DevOps-centric)
- AI-led SDLC is GitHub-first with Azure-hosted runtime + preview infra
```

**Cross-tool authority split:**
- **Azure DevOps** — portfolio / governance / test management / selected enterprise CI/CD gating
- **GitHub** — code / PR / agentic SDLC execution
- **Foundry** — AI platform control plane
- **Databricks + Fabric** — governed data intelligence
- **Azure** — runtime, identity, observability, deployment substrate

This refines (does not contradict) `ssot/governance/platform-authority-split.yaml`.

---

## Reference 1 — Databricks + Fabric data intelligence

**Source:** `techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621`

**Center of gravity:** Data architecture. Names BOTH Azure DevOps AND GitHub for CI/CD/version control. Centers Event Hubs, ADLS Gen2, Delta/medallion, Unity Catalog, Purview, Power BI/Fabric, Key Vault, Azure Monitor, Entra, Defender.

### Coverage

| Concern | Existing ADO epic | Coverage |
|---|---|---|
| OLTP/OLAP separation | #4 [OBJ-004] Data Intelligence & OLTP/OLAP Separation | ✅ Architecture |
| Data intelligence operating model | #241 Data Intelligence Operating Model | ✅ Theme |
| Cross-environment governance | #106 Schema Governance | ✅ Partial |
| Azure substrate | #1 [OBJ-001] Identity Baseline & Platform Foundation | ✅ Substrate |
| Event Hubs ingestion | — | ❌ **MISSING** |
| Medallion (bronze/silver/gold) contracts | — | ❌ **MISSING** |
| Unity Catalog governance | — | ❌ **MISSING** |
| Purview metadata publishing | — | ❌ **MISSING** |
| Power BI semantic model publishing (from gold) | — | ❌ **MISSING** |
| Delta Sharing / external data sharing posture | — | ❌ **MISSING** |
| Mixed GitHub/Azure DevOps CI/CD posture | #240 AI-Led Engineering Model + #521 Delivery Governance | ⚠️ Partial — biased toward AzDO |

### Missing issue buckets to add under #4 / #241

```
Issue: Event Hubs ingestion contract (Odoo events → bronze)
Issue: Medallion bronze/silver/gold data product contracts
Issue: Unity Catalog governance + access controls
Issue: Purview metadata publishing pipeline
Issue: Power BI semantic model publishing from governed gold data
Issue: Delta Sharing / external data sharing posture
```

---

## Reference 2 — Microsoft Foundry AI platform

**Source:** `techcommunity.microsoft.com/blog/azure-ai-foundry-blog/microsoft-foundry-an-end-to-end-platform-for-building-governing-and-scaling-ai/4496736`

**Center of gravity:** AI platform. Model access, orchestration, grounding with enterprise data, evaluation, safety, governance, identity/security/compliance, lifecycle. NOT Azure DevOps-centric.

### Coverage

| Concern | Existing ADO epic | Coverage |
|---|---|---|
| Foundry runtime + copilot framing | #3 [OBJ-003] Foundry Agent Runtime & Copilot | ✅ Theme |
| AI platform operating model | #239 AI Platform Operating Model | ✅ Theme |
| Production agent hardening | #341 Production Agent Runtime Hardening (deferred) | ✅ Deferred lane |
| Foundry evaluation framework | — | ❌ **MISSING** |
| Safety / Responsible AI controls | — | ❌ **MISSING** |
| Cost / latency / quality benchmarks | — | ❌ **MISSING** |
| Grounding with enterprise data | — | ❌ **MISSING** (partially in PrismaLab RAG) |
| AI lifecycle management / observability | — | ❌ **MISSING** |
| Model access + choice catalog | — | ❌ **MISSING** |

### Missing issue buckets to add under #3 / #239

```
Issue: Foundry evaluation framework (model-as-judge + content safety + metrics)
Issue: Safety / Responsible AI controls + red-team patterns
Issue: Cost / latency / quality benchmarks per agent
Issue: Grounding strategy — enterprise data connections + retrieval contracts
Issue: AI lifecycle management + production observability (OTel + Foundry evaluators)
Issue: Model access + choice catalog (Foundry catalog → Pulser tool registry)
```

---

## Reference 3 — AI-led SDLC (GitHub + Azure)

**Source:** `techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896`

**Center of gravity:** GitHub-first. Spec Kit, GitHub issues, GitHub Copilot coding agent, PR review, GitHub Actions, Playwright MCP, Azure-hosted preview/runtime infra.

**This is the article most under-served by the current Azure-DevOps-biased epic structure.**

### Coverage

| Concern | Existing ADO epic | Coverage |
|---|---|---|
| AI-led engineering model | #240 AI-Led Engineering Model | ✅ Theme (rename per normalization matrix → "Delivery Plane — AI-Led SDLC") |
| GitHub + Azure Pipelines delivery governance | #521 Pulser for Odoo — GitHub + Azure Pipelines Delivery Governance | ✅ Direct |
| DevEx + automation consolidation | #5 [OBJ-005] Developer Experience & Automation Consolidation | ✅ Theme |
| Spec Kit → issue flow | — | ❌ **MISSING** (have spec/ bundles but no issue-generation flow) |
| GitHub Copilot coding agent operating model | — | ❌ **MISSING** |
| PR review with human-in-the-loop | — | ❌ **MISSING** (implicit only) |
| GitHub Actions deterministic deploy path | — | ⚠️ Partial — split with AzDO per `platform-authority-split.yaml` |
| Playwright MCP / proof-of-change loop | — | ❌ **MISSING** |
| Azure sandbox / preview environment pattern | — | ❌ **MISSING** |

### Missing issue buckets to add under #240 / #521 / #5

```
Issue: Spec Kit → GitHub issue auto-generation flow
Issue: GitHub Copilot coding agent operating model + role policy
Issue: PR review with human-in-the-loop (review checklist + approval gates)
Issue: GitHub Actions deterministic deploy (per platform-authority-split.yaml)
Issue: Playwright MCP / proof-of-change validation loop
Issue: Azure sandbox / preview environment pattern (per-PR ephemeral env)
```

---

## Coverage scorecard

| Reference article | Existing epic theme coverage | Issue-bucket coverage | Net assessment |
|---|---|---|---|
| Databricks + Fabric | 5/5 themes (✅) | 0/6 specific buckets (❌) | **Architecture covered, execution detail missing** |
| Foundry AI platform | 3/3 themes (✅) | 0/6 specific buckets (❌) | **Theme covered, governance/evaluation missing** |
| AI-led SDLC | 3/3 themes (✅) | 1/6 specific buckets (⚠️ — only delivery gov) | **GitHub-first execution under-served by AzDO bias** |

**Aggregate:** epics cover ~100% at theme level, ~5% at execution-detail level.

---

## What this changes

1. **No new epics** — existing taxonomy is correct (per `docs/backlog/azdo_normalization_matrix.md`).
2. **Add 18 missing issue buckets** under existing epics (6 per reference).
3. **Refine the cross-tool authority split** in messaging:
   - Stop framing AzDO as the primary engineering surface for AI-led SDLC.
   - GitHub is engineering truth; AzDO is portfolio/governance/test-mgmt.
   - Foundry + Databricks/Fabric are platform planes, not DevOps lanes.
4. **Update PRD §0.4 four-plane mapping** to include cross-tool split:
   - Transaction = Odoo + Azure runtime (CI: GitHub Actions; deploy gating: AzDO)
   - Data = Databricks + Fabric (CI: mixed GH/AzDO; canonical Microsoft reference)
   - Agent = Foundry (NOT AzDO-managed; AI platform control plane)
   - Delivery = GitHub-native AI-led SDLC (Spec Kit + Copilot agent + Actions + Playwright MCP) with AzDO for portfolio/test management

## Next actions (post-merge of PR #738)

1. **Create 18 Issues under existing epics** (grouped by reference article).
   - Use `wit_add_child_work_items` per parent epic ID.
   - Tag: `pulser-odoo; benchmark; coverage-gap; <article-tag>`.
2. **Per-Issue Tasks come later** — buckets first to make gaps visible.
3. **Optional:** Per-reference one-pager (3 small docs) that delivery teams can hand to a feature owner.

## Anchors

- **PRD doctrine:** [`spec/pulser-odoo/prd.md`](../../spec/pulser-odoo/prd.md) §0
- **Authority split:** [`ssot/governance/platform-authority-split.yaml`](../../ssot/governance/platform-authority-split.yaml)
- **ADO normalization matrix:** [`docs/backlog/azdo_normalization_matrix.md`](../backlog/azdo_normalization_matrix.md)
- **Wave-01 boards spec:** [`docs/backlog/wave-01-finance-agents-project-ops.md`](../backlog/wave-01-finance-agents-project-ops.md)
- **Memory:** `feedback_microsoft_reference_coverage_doctrine.md`

## Changelog

- **2026-04-14** Initial coverage matrix + cross-tool authority refinement. 18 missing issue buckets identified.
