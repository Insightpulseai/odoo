# Remote Foundry State Summary

> Snapshot date: 2026-03-15
> Agent: `ipai-odoo-copilot-azure` (`asst_45er4aG28tFTABadwxEhODIf`)

## Project

| Property | Value |
|----------|-------|
| Name | `data-intel-ph` |
| Resource | `data-intel-ph-resource` |
| Resource group | `rg-data-intel-ph` |
| Location | `eastus2` |
| Kind | AIServices (S0) |
| Endpoint | `https://data-intel-ph-resource.services.ai.azure.com` |
| Created | 2026-03-03 |
| Public access | Enabled |
| Network | Allow all (no VNet rules) |

## Agent

| Property | Value |
|----------|-------|
| ID | `asst_45er4aG28tFTABadwxEhODIf` |
| Name | `ipai-odoo-copilot-azure` |
| Model | `gpt-4.1` |
| Temperature | 0.4 (updated from 1.0) |
| Top P | 0.9 (updated from 1.0) |
| Tools | None wired |
| Knowledge sources | None wired |
| System prompt | v2.0.0 — scope boundaries, context awareness, advisory disclaimers |

## AI Search

| Property | Value |
|----------|-------|
| Service | `srch-ipai-dev` |
| Endpoint | `https://srch-ipai-dev.search.windows.net/` |
| Status | **EMPTY** — 0 indexes, 0 documents |
| Key | Vaulted at `ipai-odoo-dev-kv/srch-ipai-dev-api-key` |

## Content Safety

Active (4 categories: Hate, Sexual, Violence, SelfHarm). No custom blocklists.

## Evaluations

Zero Foundry-native evaluations. First manual evaluation run executed 2026-03-15 (30 cases).

## Identity

- 3 Cognitive Services User role assignments (service principals)
- `sp-ipai-azdevops` confirmed (Contributor, subscription-inherited)
- No Entra app roles registered yet

## Monitoring

No App Insights or diagnostics configured.

## Changes Applied (2026-03-15)

1. **System prompt updated** to v2.0.0 — added scope boundaries, context awareness, RBAC awareness, advisory disclaimers, live-data claim suppression
2. **Temperature reduced** from 1.0 to 0.4 for factual/grounded responses
3. **Top P adjusted** from 1.0 to 0.9

## Key Gaps Remaining

| Gap | Severity | Phase |
|-----|----------|-------|
| AI Search empty (no RAG) | HIGH | Requires content population |
| No tools wired | MEDIUM | Stage 2 per runtime contract |
| No App Insights | MEDIUM | Stage 2 |
| No Entra app roles | MEDIUM | Phase 2 of RBAC model |
| Public network access | LOW | Stage 3 |
