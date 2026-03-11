# DO -> Azure Migration Plan

> **Status**: COMPLETE
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-11T23:40+08:00
> **SSOT**: `infra/ssot/migration/do-to-azure-service-mapping.yaml`

## Objective
Decommission the DigitalOcean runtime while preserving canonical hostnames behind Cloudflare and Azure Front Door.

## Executed Scope
1. Inventory DO runtime and confirm DO-backed origin groups.
2. Provision Azure runtime targets for remaining DO-backed services.
3. Swap Front Door origins to Azure targets without changing public hostnames.
4. Validate DNS, ingress, and public health checks.
5. Snapshot and decommission DO droplet.
6. Update SSOT/reporting artifacts.

## Final State
- DO origins in Front Door: `0`
- DO droplet (`odoo-erp-prod`, `542793289`): deleted
- Canonical hostnames preserved:
  - `erp.insightpulseai.com`
  - `auth.insightpulseai.com`
  - `mcp.insightpulseai.com`
  - `n8n.insightpulseai.com`
  - `ocr.insightpulseai.com`
  - `superset.insightpulseai.com`
  - `plane.insightpulseai.com`
  - `www.insightpulseai.com`
  - `insightpulseai.com`

## Service Wave Outcomes
| Wave | Scope | Result |
|---|---|---|
| 1 | Edge/DNS baseline | PASS |
| 2 | DO-backed origins (`auth`, `mcp`, `ocr`, `superset`) | PASS |
| 3 | Public hostname validation | PASS (except non-DO `n8n=502`) |
| 4 | DO snapshot + deletion | PASS |

## Remaining Exceptions (Non-Blocking for DO Decommission)
- `n8n.insightpulseai.com` health endpoint returns `502` on Azure VM backend (`4.193.100.31`).
- Auth runtime parity (Keycloak-grade behavior) remains pending; traffic is already Azure-native.

## Evidence
- `web/docs/evidence/20260311-2326+0800/do-to-azure-finalize/logs/afd-origins-all.log`
- `web/docs/evidence/20260311-2326+0800/do-to-azure-finalize/logs/afd-origin-hosts-unique.log`
- `web/docs/evidence/20260311-2326+0800/do-to-azure-finalize/logs/public-health-checks.log`
- `web/docs/evidence/20260311-2326+0800/do-to-azure-finalize/logs/do-snapshot-action-post-delete.log`
- `web/docs/evidence/20260311-2326+0800/do-to-azure-finalize/logs/do-droplet-list-post-delete.log`
