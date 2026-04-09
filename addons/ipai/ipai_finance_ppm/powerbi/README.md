# Finance PPM — Power BI OKR Dashboard

Replaces the ECharts HTML dashboard with a Power BI report connected to live Odoo data via PostgreSQL views.

## Architecture

```
Odoo PostgreSQL (ipai-odoo-dev-pg)
  └─ pbi schema (read-only views)
       ├─ dim_team_member
       ├─ dim_project
       ├─ dim_stage
       ├─ dim_tag
       ├─ dim_milestone
       ├─ fact_task
       ├─ fact_task_assignment
       ├─ fact_task_tag
       ├─ agg_team_performance
       ├─ agg_stage_distribution
       └─ agg_milestone_progress
            │
            ▼
Power BI Desktop (.pbix)
  ├─ Theme: FinancePPM_OKR_Theme.json
  ├─ Model: FinancePPM_OKR_Model.json
  ├─ Layout: FinancePPM_OKR_ReportLayout.json
  └─ 5 pages: OKRs & KPIs │ Logframe │ WBS Timeline │ Team Load │ Tax Filing
            │
            ▼
Power BI Service (publish)
  └─ Embed URL → Odoo ir.config_parameter
       └─ OWL component renders Power BI iframe
```

## Setup

### 1. Deploy PostgreSQL views

```bash
# Azure (default)
./deploy_powerbi_views.sh odoo_dev

# Local dev
DB_HOST=localhost DB_USER=tbwa DB_PORT=5432 ./deploy_powerbi_views.sh odoo_dev
```

### 2. Build the .pbix in Power BI Desktop

1. **Get Data** → PostgreSQL → `ipai-odoo-dev-pg` / `odoo_dev`
2. Select all `pbi.*` views
3. **Import theme**: `FinancePPM_OKR_Theme.json`
4. Create relationships per `FinancePPM_OKR_Model.json`
5. Add DAX measures per `FinancePPM_OKR_Model.json`
6. Build report pages per `FinancePPM_OKR_ReportLayout.json`

### 3. Publish and embed

1. **Publish** the report to Power BI Service
2. Use **Publish to Web** (public) or **Embed for your organization** (private)
3. Copy the embed URL
4. In Odoo: Settings → Technical → System Parameters
   - Key: `ipai_finance_ppm.powerbi_embed_url`
   - Value: `https://app.powerbi.com/view?r=<token>`

### 4. Verify

Navigate to **Project → Finance PPM → OKR Dashboard** — Power BI report renders inline.

To revert to ECharts: clear the `ipai_finance_ppm.powerbi_embed_url` parameter.

## Files

| File | Purpose |
|------|---------|
| `FinancePPM_OKR_Theme.json` | Power BI theme — teal/gold TBWA\SMP palette |
| `FinancePPM_OKR_Model.json` | Semantic model: tables, relationships, DAX measures |
| `FinancePPM_OKR_ReportLayout.json` | Report page blueprints (5 pages) |
| `deploy_powerbi_views.sh` | Deploys pbi.* schema to PostgreSQL |
| `../data/powerbi_views.sql` | SQL source for all views |
| `../data/ir_config_parameter_powerbi.xml` | Odoo config parameter for embed URL |

## DAX Measures

| Measure | Expression |
|---------|-----------|
| Total Tasks | `COUNTROWS(fact_task)` |
| Done Tasks | `CALCULATE(COUNTROWS(fact_task), fact_task[is_done] = TRUE())` |
| Completion % | `DIVIDE([Done Tasks], [Total Tasks], 0)` |
| OKR Score | `ROUND([Completion %] / 100, 2)` |
| Overdue Tasks | `CALCULATE(COUNTROWS(fact_task), fact_task[is_overdue] = TRUE())` |
| Blocked Tasks | `CALCULATE(COUNTROWS(fact_task), fact_task[kanban_state] = "blocked")` |
| Risk Score | `DIVIDE([Overdue Tasks] + [Blocked Tasks], [Total Tasks], 0)` |
| Milestone Hit Rate | `DIVIDE(CALCULATE(COUNTROWS(dim_milestone), dim_milestone[is_reached] = TRUE()), COUNTROWS(dim_milestone), 0)` |
