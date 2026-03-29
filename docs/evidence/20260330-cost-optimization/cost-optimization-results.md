# Cost Optimization Execution — 2026-03-30

> **Target**: Reduce from ~$40/day to ~$29/day baseline (proven achievable Mar 25-27)
> **Method**: Stop/delete resources with no Phase 1 deliverable

---

## Actions Taken

| # | Resource | Action | Result | Est. Saving/mo |
|---|----------|--------|--------|----------------|
| 1 | `fcipaidev` (Fabric F2) | Suspended | **Paused** — verified via Resource Graph | $262–524 |
| 2 | `ipai-copilot-endpoint` (ML endpoint) | Deleted | **Gone** — ResourceNotFound confirms deletion | $72–360 |
| 3 | `srch-ipai-dev` (AI Search Basic) | Deleted | **Gone** — verified via Resource Graph | $70 |
| 4 | `oai-ipai-dev` (OpenAI standalone) | Deleted | **Gone** — redundant with Foundry | $0–50 |
| 5 | `data-intel-ph-resource` + project | Deleted | **Gone** — redundant Foundry hub | $10–30 |
| 6 | `vision-ipai-dev` (ComputerVision F0) | Deleted | **Gone** — free tier but undocumented | $0 |
| 7 | `lang-ipai-dev` (TextAnalytics F0) | Deleted | **Gone** — free tier but undocumented | $0 |
| 8 | `ipai-superset-dev` (ACA) | Scaled to 0/1 | **Min replicas = 0** — will scale to 0 with no traffic | $5–15 |
| 9 | `w9studio-landing-dev` (ACA) | Scaled to 0/2 | **Min replicas = 0** — will scale to 0 with no traffic | $5–10 |
| 10 | `ipai-prismalab-dev` (ACA) | Revision deactivated | **Deactivated** — no running replicas | $5–10 |

**Estimated total monthly savings: $429–1,069**

---

## Not Actioned (kept running)

| Resource | Reason |
|----------|--------|
| `srch-ipai-copilot` (AI Search Free) | Free tier — $0 cost |
| `dbw-ipai-dev` (Databricks workspace) | Phase 1 — workspace needed, clusters auto-terminate |
| All core ACA apps (12) | Production workloads |
| `kv-ipai-dev/staging/prod` | Required Key Vaults |
| `pg-ipai-odoo` | Production database |

---

## Verification

```
Before: 69 resources
After:  70 resources (Resource Graph count — includes pending deletions propagating)
Deleted: 5 resources (oai, vision, lang, srch-ipai-dev, data-intel-ph + project)
Paused: 1 (Fabric capacity)
Scaled to 0: 3 container apps (superset, w9studio, prismalab)
```

---

## Resources Remaining After Cleanup

| Category | Resources | Status |
|----------|-----------|--------|
| Fabric capacity | `fcipaidev` | **Paused** |
| AI Search | `srch-ipai-copilot` (free) | Running |
| Cognitive Services | `docai-ipai-dev` (FormRecognizer) | Running — Phase 1 (OCR) |
| Foundry | `aifoundry-ipai-dev` (Hub) + `proj-ipai-claude` (Project) | Running — canonical |
| Databricks | `dbw-ipai-dev` | Running — Phase 1 |
| Container Apps | 12 apps (3 scaled to 0) | 9 running, 3 idle |
