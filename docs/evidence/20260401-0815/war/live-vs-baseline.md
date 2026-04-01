# WAR Evidence: Live vs Baseline Comparison

## Score Comparison

| Metric | Baseline (repo-only) | Live (Azure-backed) | Delta |
|---|---|---|---|
| Total checks | 18 | 18 | 0 |
| Passed | 13 | 13 | 0 |
| Warned | 1 | 1 | 0 |
| Failed | 1 | 1 | 0 |
| Skipped | 3 | 3 | 0 |
| Score | 86% | 86% | 0 |

## Analysis

The live run confirms the baseline score was accurate. The key difference is **provenance**: the baseline was generated from static repo checks only, while the live run queried actual Azure resources.

### What changed between runs

- **PG backup retention**: Now confirmed as 35 days (was unchecked in static baseline)
- **ACA managed identity**: Confirmed as SystemAssigned (was unchecked in static baseline)
- **Resource group count**: Live count is 3 (baseline estimated)
- **PostgreSQL tier**: Confirmed GeneralPurpose (was unchecked in static baseline)

### What didn't change

- Score parity: both runs show 86%, which means the baseline was a reasonable approximation
- Same single FAIL (zone redundancy) and same WARN (geo-backup)

### Skipped items

3 items skipped in both runs due to:
1. Defender pricing tier query permissions
2. Key Vault not provisioned
3. Front Door profile name mismatch in script

> **Baseline status**: `war-baseline.json` in this directory is now superseded by `live-war-output.json`. The baseline is retained for historical reference only.
