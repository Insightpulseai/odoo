# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class APAgingController(http.Controller):
    """
    AP Aging Heatmap Dashboard Controller.

    Routes:
    - /ipai/finance/ap_aging/heatmap: Main heatmap visualization
    - /ipai/finance/ap_aging/api/data: JSON API for heatmap data
    """

    @http.route('/ipai/finance/ap_aging/heatmap', type='http', auth='user', website=True)
    def ap_aging_heatmap(self, employee_code=None, **kwargs):
        """
        Render AP Aging heatmap dashboard with ECharts visualization.

        Args:
            employee_code (str, optional): Employee code filter (defaults to current user's employee)

        Returns:
            Rendered HTML template with heatmap data
        """
        # Default to current user's employee code or 'RIM'
        if not employee_code:
            if request.env.user.employee_id:
                employee_code = request.env.user.employee_id.code or 'RIM'
            else:
                employee_code = 'RIM'

        _logger.info(f"Rendering AP Aging heatmap for employee: {employee_code}")

        # Get latest snapshot data
        try:
            aging_data = request.env['account.move.line'].sudo().cron_generate_ap_aging_snapshot(employee_code)
        except Exception as e:
            _logger.error(f"Failed to generate AP Aging snapshot: {str(e)}", exc_info=True)
            return request.render('ipai_finance_ap_aging.error_template', {
                'error_message': 'Failed to generate AP Aging data. Please contact system administrator.',
            })

        # Render template with ECharts
        return request.render('ipai_finance_ap_aging.heatmap_template', {
            'aging_data': json.dumps(aging_data),
            'employee_code': employee_code,
            'snapshot_date': aging_data['snapshot_date'],
            'total_payables': aging_data['total_payables'],
            'vendor_count': aging_data['vendor_count'],
            'total_overdue_90plus': aging_data['total_overdue_90plus'],
        })

    @http.route('/ipai/finance/ap_aging/api/data', type='json', auth='user')
    def ap_aging_api_data(self, employee_code='RIM'):
        """
        JSON API endpoint for AP Aging heatmap data.

        Args:
            employee_code (str): Employee code filter

        Returns:
            dict: AP Aging data with vendors and buckets
        """
        _logger.info(f"API request for AP Aging data: employee={employee_code}")
        return request.env['account.move.line'].sudo().cron_generate_ap_aging_snapshot(employee_code)

    @http.route('/ipai/finance/ap_aging/api/summary', type='json', auth='user')
    def ap_aging_api_summary(self, employee_code='RIM'):
        """
        JSON API endpoint for AP Aging summary KPIs.

        Args:
            employee_code (str): Employee code filter

        Returns:
            dict: Summary statistics
        """
        _logger.info(f"API request for AP Aging summary: employee={employee_code}")
        return request.env['account.move.line'].sudo().get_ap_aging_summary(employee_code)
