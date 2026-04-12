# Excel Studio

> Publishable-quality workbook generation from Odoo metrics and OKR data.

## Capability

Generate formula-safe workbooks (XLSX) from Finance PPM OKR scores,
record-level metrics, task/milestone data, and derived calculations.

## Grounding sources

1. Finance PPM OKR objectives and key results (computed scores)
2. Record-level metrics from Odoo models
3. Task, milestone, and gate status data
4. Derived formulas and KPI definitions

## Output types

| Type | Description | Example |
|------|-------------|---------|
| OKR dashboard workbook | Operational KPI and KR scorecard | Finance PPM OKR tracker |
| Skill matrix | Capability readiness with scored dimensions | Office skills capability matrix |
| Release tracker | Release visibility and dependency control | R1/R2/R3 milestone tracker |
| KPI model | Financial or operational model with scenarios | Cash flow projection, variance analysis |
| Scenario workbook | What-if analysis with input parameters | BIR readiness scenario model |

## Quality gates

- [ ] Formula integrity: all formulas resolve correctly, no #REF! or #VALUE! errors
- [ ] Recalc validation: workbook recalculates correctly when inputs change
- [ ] Cell overflow: no truncated content, column widths appropriate
- [ ] Conditional formatting: RAG indicators, score-based styling applied correctly
- [ ] Grounded: all data points traced to Odoo records or derived formulas

## Publish gate

1. Content grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes resolved and retained copies stored in Odoo Documents.
4. Final output ready to circulate externally without reformatting.

## Dependencies

- `openpyxl` — native XLSX generation
- OCA `report_xlsx` — Odoo server-side XLSX export
- `ipai_odoo_copilot` — Odoo context packaging
- Odoo Documents — retained copy storage

## Phase

R1 Foundation → R2 Core → R3 Hardening
