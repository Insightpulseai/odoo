# WAF Assessment — 2026-04-17

> Validated against Azure Architecture Center + Well-Architected Framework.
> Overall score: **5.2/10** — development-grade, not production-ready.

## Pillar scores

| Pillar | Score | Critical gap |
|---|---|---|
| Reliability | 4/10 | No HA on PG, no zone redundancy on ACA, single-region, no DR |
| Security | 6/10 | PG 0.0.0.0 firewall, KV public, no Defender, password auth |
| Cost | 5/10 | PG 2x over-provisioned, idle old-sub resources |
| Ops Excellence | 6/10 | Bicep exists but not deployed via pipelines |
| Performance | 5/10 | Cross-region latency SEA↔EUS2, no caching |

## Top 10 actions

| # | Action | Priority | Effort |
|---|---|---|---|
| 1 | Deploy private endpoints for PG + KV | P0 | 2 hrs |
| 2 | Enable Defender for Cloud (free tier) | P0 | 15 min |
| 3 | Downsize PG D4s_v3 → D2s_v3 or B2ms | P0 | 30 min |
| 4 | Remove PG AllowAzureServices 0.0.0.0 | P0 | 5 min |
| 5 | Wire ACA to VNet + zone redundancy | P1 | 3 hrs |
| 6 | Enable Entra auth on PG Flex | P1 | 2 hrs |
| 7 | Deploy APIM GenAI Gateway | P1 | 4 hrs |
| 8 | Fix CDM export pipeline | P1 | 2 hrs |
| 9 | Resolve Fabric trial expiry | P1 | 1 hr |
| 10 | Audit Databricks serving costs | P1 | 1 hr |

## Key finding

Bicep modules are well-designed but NOT deployed. The gap is deployment, not design.

## Sources

- Azure WAF Service Guides (ACA, PG, KV)
- Azure Security Benchmark
- Baseline Foundry Chat Architecture
- Modern Analytics with Databricks
- PG Cost Optimization guide
