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

## Strategic OKR Layer

Operational KPIs (kpi_001 through kpi_017) are linked to strategic objectives (A-E) and canonical OKRs (O1-O3) in the enterprise OKR framework:

- **SSOT**: `ssot/governance/enterprise_okrs.yaml`
- **Validator**: `scripts/ci/validate_enterprise_okrs.py`

The OKR framework groups KPIs by strategic objective:

| Objective | KPIs |
|-----------|------|
| A: Delivery Speed | kpi_001, kpi_016, kpi_017 |
| B: Safety & Reliability | kpi_010, kpi_014, kpi_015 |
| C: Infrastructure Efficiency | kpi_007, kpi_008, kpi_011 |
| D: Cost & Governance | kpi_002, kpi_003, kpi_004 |
| E: Security & Compliance | kpi_005, kpi_006, kpi_012 |

## Cross-References

- KPI contracts: `platform/data/contracts/control_room_kpis.yaml`
- Event contracts: `platform/data/contracts/control_room_events.yaml`
- Strategic OKRs: `ssot/governance/enterprise_okrs.yaml`
- Control Room spec: `spec/control-room-platform/`
- Enterprise target state spec: `spec/enterprise-target-state/`
- Operating model: `docs/governance/ENTERPRISE_OPERATING_MODEL.md`
