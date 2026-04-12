# Cost Governance

## Current controls (deployed 2026-04-13)

### Budget alert
- Name: `ipai-dev-monthly-500`
- Scope: Subscription `536d8cf6-89e1-4815-aef3-d5f2c5f4d070`
- Amount: $500/month
- Thresholds: 80% actual, 100% actual
- Contact: admin@insightpulseai.com

### Resource group tags
All 4 RGs tagged with: `env=dev`, `owner=jake`, `service=ipai`, `managed-by=bicep`
- rg-ipai-dev-odoo-runtime
- rg-ipai-dev-odoo-data
- rg-ipai-dev-platform
- rg-data-intel-ph

## Required controls (not yet implemented)
- Monthly budget review cadence (1st of each month)
- Variance threshold for escalation (>20% month-over-month)
- Unowned resource policy (tag enforcement via Azure Policy)
- Mandatory tag enforcement for new resources (`env`, `owner`, `service`)
- Per-service cost allocation reports

## Cost decision register

| Area | Current state | Decision needed | Owner | Due date |
|---|---|---|---|---|
| Analytics capacity | Fabric trial (fcipaidev) | Upgrade F2 vs migrate to Databricks | Jake | 2026-05-20 |
| Foundry region | East US 2 (cross-region from SEA) | Accept latency or migrate | Jake | 2026-06-01 |
| Meta CAPI Function App | Standalone `func-ipai-meta-capi` | Migrate to ACA or keep | Jake | 2026-06-01 |

## Evidence
- Budget created via `az rest` (2026-04-13)
- Tags applied via `az group update` (2026-04-13)
- Assessment: docs/evidence/20260413-0100/assessments/02-azure-waf-review.md (Cost pillar: 42%)
