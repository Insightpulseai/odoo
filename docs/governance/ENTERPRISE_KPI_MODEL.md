# Enterprise KPI Model

## Purpose

Human-readable guide to the InsightPulse AI KPI framework.

## Machine-Readable SSOT

The canonical KPI and event contracts are:

```
platform/data/contracts/control_room_kpis.yaml   (17 KPIs)
platform/data/contracts/control_room_events.yaml  (11 events)
```

CI check: `.github/workflows/control-room-governance.yml`

## KPI Categories

| Category | KPIs | Owner |
|----------|------|-------|
| Finance Operations | Approval turnaround, expense processing, close cycle | Odoo ERP |
| Tax Compliance | BIR filing on-time rate, compliance score | Odoo ERP |
| Automation | OCR accuracy, workflow success rate | n8n / OCR |
| Agent Platform | Tool success rate, grounding coverage | Azure Foundry |
| Platform Health | Sync latency, uptime, error rate | Supabase |

## Event-KPI Linkage

Events drive KPI measurements. Each event contract in `control_room_events.yaml` references the KPIs it feeds via `kpi_linkage`.

## Cross-References

- KPI contracts: `platform/data/contracts/control_room_kpis.yaml`
- Event contracts: `platform/data/contracts/control_room_events.yaml`
- Control Room spec: `spec/control-room-platform/`
- Operating model: `docs/governance/ENTERPRISE_OPERATING_MODEL.md`
