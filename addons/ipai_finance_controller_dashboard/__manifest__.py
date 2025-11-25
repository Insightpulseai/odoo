# -*- coding: utf-8 -*-
{
    'name': 'IPAI Finance Controller Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Finance',
    'summary': 'Finance Controller Dashboard with 6 ECharts Visualizations for Month-End Close KPI Monitoring',
    'description': """
Finance Controller Dashboard
=============================

Comprehensive Finance Controller Dashboard with 6 Apache ECharts visualizations:

1. **KPI Gauges**: 3 gauge charts (timeliness, reconciliation, BIR filing rate)
2. **Calendar Heatmap**: Workload density with BIR deadline overlays
3. **WBS Tree**: Collapsible task hierarchy (Phase → Task → Subtask)
4. **Gantt Chart**: Task execution timeline with owners and dates
5. **Sunburst RACI**: Responsibility distribution by phase and cluster
6. **Dependency Graph**: Task prerequisite network visualization

Features:
- Employee context filtering (RIM, CKVC, BOM, JPAL, etc.)
- Daily KPI snapshot automation (9 AM PHT)
- Real-time data refresh via AJAX
- Print-friendly dashboard export
- n8n workflow integration for alerts
- Mattermost notifications for KPI thresholds (<85%)

Integration:
- LogFrame indicators from ipai_finance_ppm_tdi
- Month-End Close tasks from ipai_finance_monthly_closing
- Shared ECharts patterns from ipai_finance_ap_aging
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'project',
        'hr',
        'ipai_finance_ppm_tdi',
        'ipai_finance_monthly_closing',
        'ipai_finance_ap_aging',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/controller_dashboard_cron.xml',
        'views/controller_dashboard_views.xml',
        'views/controller_dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ipai_finance_controller_dashboard/static/src/xml/dashboard_template.xml',
            'ipai_finance_controller_dashboard/static/src/xml/kpi_gauges.xml',
            'ipai_finance_controller_dashboard/static/src/xml/calendar_heatmap.xml',
            'ipai_finance_controller_dashboard/static/src/xml/wbs_tree.xml',
            'ipai_finance_controller_dashboard/static/src/xml/gantt_chart.xml',
            'ipai_finance_controller_dashboard/static/src/xml/raci_sunburst.xml',
            'ipai_finance_controller_dashboard/static/src/xml/dependency_graph.xml',
            'ipai_finance_controller_dashboard/static/src/css/dashboard_styles.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
