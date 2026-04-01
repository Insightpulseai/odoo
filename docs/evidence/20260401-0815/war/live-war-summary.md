# Well-Architected Review — Live Evidence Summary

**Date**: 2026-04-01T09:02:36Z
**Status**: live (Azure CLI backed)
**Related**: #649
**Score**: 86% (13/15 assessed, 3 skipped)

## Results by Pillar

### Reliability (4 checks)
| Check | Result | Detail |
|---|---|---|
| ACA zone redundancy | FAIL | Not zone-redundant (dev tier, acceptable for dev) |
| PG backup retention | PASS | 35 days |
| PG geo-redundant backup | WARN | Disabled (recommend for prod) |
| ACA min replicas | PASS | 1 (no cold start risk) |

### Security (5 checks)
| Check | Result | Detail |
|---|---|---|
| Defender for Cloud | SKIP | Query permissions insufficient |
| Key Vault purge protection | SKIP | `kv-ipai-dev` not provisioned |
| PIM governance module | PASS | Bicep exists + eligible assignments live |
| Policy tag governance module | PASS | Bicep exists + 3 assignments deployed |
| ACA managed identity | PASS | SystemAssigned |

### Cost Optimization (2 checks)
| Check | Result | Detail |
|---|---|---|
| ACA consumption plan | PASS | Pay-per-use |
| Resource group count | PASS | 3 (target <= 8) |

### Operational Excellence (5 checks)
| Check | Result | Detail |
|---|---|---|
| Bicep modules | PASS | 18 modules |
| Monitoring workbook | PASS | Exists |
| Alert rules | PASS | Exists |
| CI/CD workflows | PASS | 49 workflows |
| Platform SOP | PASS | Documented |

### Performance Efficiency (2 checks)
| Check | Result | Detail |
|---|---|---|
| Front Door profile | SKIP | Profile name mismatch in query |
| PostgreSQL tier | PASS | GeneralPurpose |

## Actionable Findings

1. **ACA zone redundancy** (FAIL): Dev environment, acceptable. Enable for staging/prod.
2. **PG geo-redundant backup** (WARN): Enable for production database.
3. **Key Vault** (SKIP): `kv-ipai-dev` not yet provisioned — tracked separately.
4. **Defender for Cloud** (SKIP): May need elevated permissions to query pricing tier.
5. **Front Door** (SKIP): Script queries `afd-ipai-dev` in `rg-ipai-dev-platform` but AFD may be named `ipai-fd-dev` or in a different RG.
