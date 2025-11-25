# -*- coding: utf-8 -*-

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class FinanceControllerDashboardController(http.Controller):
    """
    Finance Controller Dashboard HTTP Routes

    Provides 7 routes for Finance Controller Dashboard:
    1. Main dashboard page (/ipai/finance/controller/dashboard)
    2. KPI Gauges API (/ipai/finance/controller/api/kpi_gauges)
    3. Calendar Heatmap API (/ipai/finance/controller/api/calendar_heatmap)
    4. WBS Tree API (/ipai/finance/controller/api/wbs_tree)
    5. Gantt Chart API (/ipai/finance/controller/api/gantt)
    6. RACI Sunburst API (/ipai/finance/controller/api/raci_sunburst)
    7. Dependency Graph API (/ipai/finance/controller/api/dependency_graph)
    """

    @http.route('/ipai/finance/controller/dashboard', type='http', auth='user', website=True)
    def controller_dashboard(self, employee_code=None, **kwargs):
        """
        Main Finance Controller Dashboard page

        Args:
            employee_code (str): Employee code for filtering (e.g., 'RIM', 'CKVC')
            **kwargs: Additional query parameters

        Returns:
            Rendered QWeb template with all 6 ECharts visualizations
        """
        if not employee_code:
            employee_code = request.env.user.employee_id.code or 'RIM'

        return request.render('ipai_finance_controller_dashboard.dashboard_template', {
            'employee_code': employee_code,
        })

    @http.route('/ipai/finance/controller/api/kpi_gauges', type='json', auth='user')
    def api_kpi_gauges(self, employee_code='RIM'):
        """
        KPI Gauges API - 3 gauge charts

        Returns:
            dict: {
                'timeliness': float (0-100%),
                'reconciliation': float (0-100%),
                'filing_rate': float (0-100%),
                'tasks_completed': int,
                'closing_adjustments': int,
                'daily_completion_pct': list of dict (7 days)
            }
        """
        return request.env['finance.controller.kpi'].sudo().get_kpi_gauge_data(employee_code)

    @http.route('/ipai/finance/controller/api/calendar_heatmap', type='json', auth='user')
    def api_calendar_heatmap(self, employee_code='RIM'):
        """
        Calendar Heatmap API - Workload density + BIR milestones

        Returns:
            dict: {
                'heatmap_data': list of [date, task_count],
                'milestones': list of dict with {date, type, label}
            }
        """
        return request.env['finance.controller.kpi'].sudo().get_calendar_heatmap_data(employee_code)

    @http.route('/ipai/finance/controller/api/wbs_tree', type='json', auth='user')
    def api_wbs_tree(self, employee_code='RIM'):
        """
        WBS Tree API - Task hierarchy

        Returns:
            dict: {
                'name': 'root',
                'children': list of nested dict with task hierarchy
            }
        """
        return request.env['finance.controller.kpi'].sudo().get_wbs_tree_data(employee_code)

    @http.route('/ipai/finance/controller/api/gantt', type='json', auth='user')
    def api_gantt(self, employee_code='RIM'):
        """
        Gantt Chart API - Task execution timeline

        Returns:
            list: [
                {
                    'name': 'Task Name',
                    'start': 'YYYY-MM-DD',
                    'end': 'YYYY-MM-DD',
                    'owner': 'RIM',
                    'phase': 'Phase 1'
                }
            ]
        """
        return request.env['finance.controller.kpi'].sudo().get_gantt_data(employee_code)

    @http.route('/ipai/finance/controller/api/raci_sunburst', type='json', auth='user')
    def api_raci_sunburst(self, employee_code='RIM'):
        """
        RACI Sunburst API - Responsibility distribution

        Returns:
            dict: {
                'name': 'root',
                'children': list of nested dict with RACI hierarchy
            }
        """
        return request.env['finance.controller.kpi'].sudo().get_raci_sunburst_data(employee_code)

    @http.route('/ipai/finance/controller/api/dependency_graph', type='json', auth='user')
    def api_dependency_graph(self, employee_code='RIM'):
        """
        Dependency Graph API - Task prerequisite network

        Returns:
            dict: {
                'nodes': list of dict {id, name, category},
                'links': list of dict {source, target}
            }
        """
        return request.env['finance.controller.kpi'].sudo().get_dependency_graph_data(employee_code)
