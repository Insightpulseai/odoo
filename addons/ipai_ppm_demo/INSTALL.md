# IPAI PPM Demo - Installation Guide

## Quick Installation

### 1. Update Odoo Module List

```bash
# Navigate to Odoo directory
cd /Users/tbwa/odoo-ce

# Update module list (if running locally)
# Odoo will auto-detect the new module in addons/ipai_ppm_demo
```

### 2. Install Module via Odoo UI

1. Log into Odoo as Administrator
2. Navigate to **Apps** menu
3. Click **Update Apps List** (may need to enable Developer Mode)
4. Search for **"IPAI PPM Demo"**
5. Click **Install**

### 3. Access Dashboard

Once installed:

1. Navigate to **Project** app
2. Click **PPM Demo** menu
3. Select **PPM Dashboard** to view Planview-style visualizations

## What Gets Installed

### Seed Data
- **4 Projects**: Digital Banking Revamp, Core System Migration, Analytics Platform, Branch Kiosk
- **5 Financial Periods**: Q1-Q3 2025 Capex/Opex data
- **4 Dependency Nodes**: Critical path tracking
- **3 Intake Requests**: Project intake pipeline
- **2 AI Insights**: Portfolio risk summaries
- **Kanban Board**: 3 columns with 4 project cards
- **Dashboard KPIs**: Portfolio health metrics
- **Strategy Spend**: Budget allocation by strategy

### Dashboard Sections

1. **Project Planning & Management** (Gauges)
   - Project Health: 78%
   - Budget Health: 72%

2. **Portfolio Planning & Prioritization** (Treemap)
   - Customer Experience: $12M
   - Risk & Compliance: $14.5M
   - Data & Insights: $8M
   - Branch Transformation: $6.5M

3. **Scenario Analysis** (Area Chart)
   - Planned vs Actual vs Earned Value
   - Q1-Q3 2025 trends

4. **Intake & Demand Management** (Heatmap)
   - Business Value scores
   - Ease of Implementation
   - Strategic Alignment

## Troubleshooting

### Dashboard Not Loading

**Symptom**: Blank screen or JavaScript errors

**Solution**:
1. Verify ECharts library exists: `ls addons/ipai_ppm_demo/static/lib/echarts.min.js`
2. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
3. Check browser console for errors (F12 → Console tab)
4. Restart Odoo server: `systemctl restart odoo` or your local dev server

### No Data Showing in Charts

**Symptom**: Charts render but show no data

**Solution**:
1. Verify seed data loaded: Navigate to **PPM Demo → Intake Requests** (should show 3 records)
2. Check database: `psql $POSTGRES_URL -c "SELECT COUNT(*) FROM ppm_dashboard_kpi;"`
3. If no data: Uninstall and reinstall module (data loaded via `noupdate="1"`)

### Module Not Found in Apps List

**Symptom**: "IPAI PPM Demo" doesn't appear after updating apps list

**Solution**:
1. Verify directory structure: `ls addons/ipai_ppm_demo/__manifest__.py`
2. Check Odoo addons path includes `/Users/tbwa/odoo-ce/addons`
3. Check Odoo logs for syntax errors: `tail -f /var/log/odoo/odoo.log`
4. Restart Odoo with `--addons-path` flag if needed

## Dependencies

- **Odoo CE 18.0** (tested)
- **project** module (core Odoo)
- **hr** module (core Odoo)
- **web** module (core Odoo)
- **Apache ECharts 5.4.3** (bundled in `static/lib/`)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Development Notes

### Extending the Dashboard

To add new chart sections:

1. Add new model in `models/`
2. Add seed data in `data/ppm_demo_data.xml`
3. Update security in `security/ir.model.access.csv`
4. Add data fetching in `static/src/js/ppm_dashboard.js` (`loadData()`)
5. Add chart rendering method (e.g., `renderNewChart()`)
6. Add template section in `static/src/xml/ppm_dashboard.xml`

### Customizing Charts

ECharts options are in the `renderXXX()` methods in `ppm_dashboard.js`. Refer to [ECharts documentation](https://echarts.apache.org/en/option.html) for configuration options.

## License

AGPL-3 (Odoo Community Association compliance)

## Support

For issues or questions:
- GitHub: https://github.com/InsightPulseAI/odoo-ce/issues
- Email: jake@insightpulseai.com
