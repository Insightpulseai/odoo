# RG Normalization — Official Closeout

Date: 2026-03-20

## Status

| Lane | Status |
|------|--------|
| RG Normalization | **accepted** |
| ACA Runtime Cutover | **complete** |
| Legacy Agents RG Cleanup | **complete** |
| Old Runtime Hold | **active until 2026-03-23** |
| Operational State | **live on rg-ipai-dev-odoo-runtime** |

## Go-Live Interpretation

This work covers **platform infrastructure go-live**, specifically:
- ACA environment readiness
- Storage attachment readiness
- Front Door routing readiness
- Runtime migration readiness
- Legacy resource retirement readiness
- SSOT/runtime-truth alignment

It is a **prerequisite** for application capability go-live, not the same thing.

## Post-Cutover Follow-Up

**Normalize ACA ACR auth posture after stabilization hold.**

During Phase 3, ACR admin credentials were used as the deployment recovery
path (system-assigned identity lacked AcrPull on the new app at creation time).
This is the live pull posture for apps using `ipaiodoodevacr`.

After the stabilization hold expires (2026-03-23):
1. Grant each app's system-assigned identity `AcrPull` on `ipaiodoodevacr`
2. Update registry config from `username/passwordSecretRef` to `identity: system`
3. Remove `acr-password` secret from each app
4. Delete old apps in `rg-ipai-dev`

## Evidence

- `phase3-closeout.md` — app deployment and health check evidence
- `phase4-retirement-plan.md` — legacy resource deletion scope
- `ssot/azure/operator_view.yaml` — canonical status
- `infra/ssot/azure/rg-normalization-matrix.yaml` — migration matrix
- `ssot/azure/resource_rationalization.yaml` — resource mapping
