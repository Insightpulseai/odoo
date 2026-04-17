# Completeness Matrix — Finance + Project Operations + Data Intelligence + FinOps

> **Canonical "are we actually done?" view.**
> Benchmarked against Microsoft reference architectures: Dynamics 365 Finance, D365 Project Operations, Azure AI Well-Architected, CDM + Data Lake, Databricks/Fabric end-to-end, FinOps Framework, Azure Boards governance.
> Locked 2026-04-15. Next refresh after P0 gaps close.

---

## Overall verdict

```text
Substrate:            mostly provisioned
Reference alignment:  broadly correct
Codebase completeness: not yet
Production readiness:  not yet
```

The diagnosis is **not** "wrong architecture." It is **"correct architecture, incomplete implementation."** The Databricks/Fabric, AI Well-Architected, and FinOps references all assume the substrate exists first — we have that. The missing layer is **governed data flow, runtime hardening, FinOps control loops, and reproducible delivery.**

CI/CD authority is Azure Pipelines only (per `ssot/governance/platform-authority-split.yaml`). GitHub Actions and Vercel are forbidden (CLAUDE.md rev 2026-04-14).

---

## Main completeness matrix

| Capability lane | What the reference expects | Provisioned | Coded | Production-ready | Gap to close next |
|---|---|:-:|:-:|:-:|---|
| **Azure Boards governance spine** | Backlogs, boards, sprints, queries, portfolio hierarchy, GitHub linkage, permissions | Partial | Partial | No | Lock Epic/Feature/Issue hierarchy, queries, iteration paths, PR-linkage contract. 23 epics + 120 issues populated (2026-04-14) but normalization matrix still has 2 renames / 3 merges pending. |
| **Finance benchmark (D365 Finance)** | Planning, budgeting, forecasting, close, tax, AR/collections, cash visibility, analytics, reconciliation agent | Partial | Partial | No | Finish finance core parity (GL/AP/AR). Reconciliation Agent v0. Collections workflow. BIR Phase 1 DAT+PDF already live (Issue 9); SAWT/QAP/SLSP/2550M generators pending. |
| **Project Operations benchmark (D365 PO)** | Pricing/costing, project accounting, resource utilization, forecasting snapshots, time/expense, AI productivity | Partial | Partial | No | Complete PSA/project-accounting/resource/time-expense backlog. No project agents yet. Primary Odoo parity: `project` + `hr_timesheet` + OCA `project-reporting` + OCA `account-analytic`. |
| **AI runtime plane (Well-Architected AI)** | App design, app platform, data platform, ops, testing/evals, personas, responsible AI | Mostly | Partial | No | Finish agent identity (Entra Agent ID frontier-gated; catalog registration pending May 1 M365 E7 GA). Eval/ops hardening. Safe Outputs subsystem. Tool allowlist enforcement. Review loops. |
| **Databricks/Fabric data-intelligence plane** | Data export to lake, ADLS setup, workspace creation, ingestion, semantic consumption in Power BI/Fabric | Mostly | Partial | No | CDM export pipeline code shipped (DLT pipeline `3495d54a-bfc9-47aa-9fc5-517f190e430b`) — first run pending. Fabric capacity decision (F2 $262/mo) blocked on operator approval before trial expires ~2026-05-20. Semantic consumption path not yet wired. |
| **CDM / lake interoperability** | CDM folders, manifests, `model.json`, entity metadata, producer/consumer separation, AAD + ACL authorization | Partial | Partial | No | Finish CDM export pipeline path=arg fix on Gold tables. Generate `manifest.cdm.json` on first run. Write producer/consumer ACL contract. Swap UC external location from phantom `stipaidevlake` to real `stipaidevlake` (resolved 2026-04-15). |
| **FinOps practice** | Usage/cost ingestion, allocation, reporting/analytics, anomaly mgmt, forecasting, budgeting, governance, chargeback | Partial | Low | No | PAYG FOCUS cost export created 2026-04-15 → `stipaidevlake/msexports/focuscost/subscription-<payg-id>/`. Sponsorship sub excluded (MS-AZR-0036P unsupported). Reporting/allocation/anomaly loops not yet built. See `docs/runbooks/finops-baseline.md`. |
| **FinOps IaC / automation** | Reusable Bicep modules for scheduled actions and FinOps enablement | Low | Low | No | Add FinOps Toolkit Bicep Registry consumption. Codify scheduled actions as Bicep modules. Use `microsoft/finops-toolkit` upstream reference (per `ssot/governance/upstream-adoption-register.yaml`). |
| **Delivery / ALM** | CI/CD, environment promotion, issue tracking, deployment discipline | Mostly | Partial | No | Remove manual-only islands. Codify Azure Pipelines for UC/data path/FinOps path. Evidence gates on all deploys. GitHub Actions fully removed 2026-04-14. |
| **Marketplace/package readiness** | Offer packaging, proof packs, TCO/benchmark evidence, private-offer readiness | Low | Low | No | Finish proof packs after finance/project/data/identity are cleaner. Marketplace last. Issue 29 scope: publish `ipai_odoo_on_aca` private offer. |

---

## FinOps-specific matrix

| FinOps capability | Current state | What "done" looks like |
|---|:-:|---|
| **Data ingestion** | Partial | FOCUS cost/usage exports land in `stipaidevlake/msexports/focuscost/` and refresh daily (PAYG live 2026-04-15; Sponsorship excluded by offer type). |
| **Allocation** | Low | Subscription / resource-group / workload / tenant allocation model documented (`platform/contracts/finops/cost-allocation-model.yaml`) and enforced via `product`, `costCenter`, `environment`, `owner` tags. |
| **Reporting + analytics** | Low | Power BI FinOps workspace (once Fabric F2 provisioned) consuming FOCUS data via Lakehouse shortcut. KPI cards per `docs/runbooks/fabric-finops-workspace.md §3`. |
| **Anomaly management** | Low | Thresholds + scheduled actions + alert routing to `appi-ipai-dev-agent-sea`. Runbook-based response. |
| **Forecasting / budgeting** | Low | Monthly budget per tenant × product. Variance dashboard. Review cadence (weekly). |
| **Governance / onboarding** | Low | Workload-onboarding checklist (`ssot/finops/workload-onboarding.yaml`). Tag/allocation policy checks in Azure Pipelines. Quarterly review cadence. |

---

## Priority gap order

### P0 — must close before GA (Dec 15 2026)

1. **Agent identity / runtime hardening** — Safe Outputs, MCP allowlist, Key Vault isolation, Content Safety. Ref CLAUDE.md "Agentic Workflow Security Doctrine."
2. **CDM export pipeline first run** — fix DLT `path=` arg on Gold tables, trigger run, emit manifest, record evidence.
3. **Azure Pipelines coverage for UC/data-path** — `azure-pipelines/templates/finops-export-validate.yml`, `bicep-lint-validate.yml`, UC smoke pipeline.
4. **Fabric semantic/business-consumption completion** — F2 capacity provision OR commit to Databricks-only analytics (Fabric Data Agent deferred).
5. **Finance core + Reconciliation Agent + Collections + Tax moat** — D365 Finance parity via Odoo + OCA + `ipai_bir_*`.

### P1 — required for partner-shippable

6. Project Operations parity + project agents.
7. FinOps workspace + ingestion + reporting baseline operationalized.
8. CDM / AAD / ACL authorization hardening — enforce producer/consumer separation.
9. FinOps anomaly / budget / governance loops.

### P2 — revenue-path

10. Marketplace private-offer packaging (Issue 29).
11. Chargeback / unit-economics maturity (cost per agent request, cost per BIR filing).
12. Advanced workload onboarding / benchmark loops.

---

## Cross-benchmark status summary

**Strongest lanes:** Azure substrate, Foundry resource model, Databricks workspace + Unity Catalog direction, overall architecture split, planning benchmark selection, reference-architecture alignment.

**Incomplete lanes:**
- **Data path not closed** — Databricks/Fabric end-to-end requires ADLS + export + workspace + ingestion + reporting; we have ~70%.
- **AI operations not complete** — testing/evals, runtime ops, personas, responsible AI all partial.
- **FinOps is mostly a future control layer** — full practice spans ingestion → allocation → reporting → anomaly → forecasting → governance → chargeback → onboarding; only ingestion exists today.

---

## Repo-ready artifacts landing with this matrix

```
docs/architecture/completeness-matrix-finance-projectops-data-intel-finops.md   ← this file
docs/runbooks/finops-baseline.md
docs/runbooks/bicep-authoring-standard.md
ssot/finops/workload-onboarding.yaml
platform/contracts/finops/cost-allocation-model.yaml
azure-pipelines/templates/finops-export-validate.yml
azure-pipelines/templates/bicep-lint-validate.yml
infra/azure/modules/data-lake-canonical.bicep         ← stipaidevlake Bicep recapture
infra/azure/README.md
docs/evidence/20260415-missing-resources/README.md
```

---

## References

- Fabric for FinOps: https://learn.microsoft.com/en-us/cloud-computing/finops/fabric/create-fabric-workspace-finops
- Azure AI Well-Architected: https://learn.microsoft.com/en-us/azure/well-architected/ai/get-started
- FinOps Framework: https://learn.microsoft.com/en-us/cloud-computing/finops/
- Azure Boards: https://learn.microsoft.com/en-us/azure/devops/boards/
- D365 Finance: https://www.microsoft.com/en-us/dynamics-365/products/finance
- D365 Project Operations: https://www.microsoft.com/en-us/dynamics-365/products/project-operations
- CDM + Data Lake: https://learn.microsoft.com/en-us/common-data-model/data-lake
- FinOps Toolkit Bicep Registry: https://learn.microsoft.com/en-us/cloud-computing/finops/toolkit/bicep-registry/modules

---

*Blunt final word:*

```text
You have enough provisioned to execute seriously.
You do not yet have enough coded and operationalized to call the platform complete.
The missing layer is no longer "more architecture."
It is governed data flow, runtime hardening, FinOps control loops, and reproducible delivery.
```
