# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    """
    Extend account.move.line with AP Aging automation capabilities.

    Features:
    - Calculate aging buckets (0-30, 31-60, 61-90, 90+ days)
    - Employee-specific context filtering
    - n8n webhook integration
    - Automated snapshot generation
    """

    _inherit = "account.move.line"

    @api.model
    def cron_generate_ap_aging_snapshot(self, employee_code="RIM"):
        """
        Calculate AP Aging buckets for specified employee context.
        Trigger n8n webhook with heatmap data.

        Args:
            employee_code (str): Employee code for filtering (default: 'RIM')

        Returns:
            dict: Heatmap data with vendors and aging buckets
        """
        _logger.info(
            f"Starting AP Aging snapshot generation for employee: {employee_code}"
        )

        # SQL Query for Aging Buckets with optimized indexing
        query = """
            SELECT
                p.id AS partner_id,
                p.name AS vendor_name,
                p.vat AS vendor_vat,
                SUM(CASE
                    WHEN aml.date_maturity IS NULL THEN aml.amount_residual
                    WHEN CURRENT_DATE - aml.date_maturity <= 30
                    THEN aml.amount_residual
                    ELSE 0
                END) AS bucket_0_30,
                SUM(CASE
                    WHEN aml.date_maturity IS NOT NULL
                    AND CURRENT_DATE - aml.date_maturity BETWEEN 31 AND 60
                    THEN aml.amount_residual
                    ELSE 0
                END) AS bucket_31_60,
                SUM(CASE
                    WHEN aml.date_maturity IS NOT NULL
                    AND CURRENT_DATE - aml.date_maturity BETWEEN 61 AND 90
                    THEN aml.amount_residual
                    ELSE 0
                END) AS bucket_61_90,
                SUM(CASE
                    WHEN aml.date_maturity IS NOT NULL
                    AND CURRENT_DATE - aml.date_maturity > 90
                    THEN aml.amount_residual
                    ELSE 0
                END) AS bucket_90_plus,
                SUM(aml.amount_residual) AS total_outstanding,
                MAX(aml.date_maturity) AS latest_due_date,
                COUNT(DISTINCT aml.move_id) AS invoice_count
            FROM account_move_line aml
            JOIN res_partner p ON aml.partner_id = p.id
            JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN res_users u ON aml.create_uid = u.id
            LEFT JOIN hr_employee e ON u.id = e.user_id
            WHERE aa.account_type = 'liability_payable'
                AND aml.amount_residual > 0
                AND aml.reconciled = FALSE
                AND aml.parent_state = 'posted'
                AND (e.code = %s OR %s = 'ALL' OR e.code IS NULL)
            GROUP BY p.id, p.name, p.vat
            HAVING SUM(aml.amount_residual) > 0
            ORDER BY SUM(aml.amount_residual) DESC
            LIMIT 20
        """

        try:
            self.env.cr.execute(query, (employee_code, employee_code))
            results = self.env.cr.dictfetchall()

            _logger.info(f"AP Aging query returned {len(results)} vendors")

            # Format for n8n webhook and heatmap
            heatmap_data = {
                "employee_code": employee_code,
                "snapshot_date": fields.Date.today().isoformat(),
                "vendors": results,
                "total_payables": sum(
                    float(r["total_outstanding"] or 0) for r in results
                ),
                "total_overdue_90plus": sum(
                    float(r["bucket_90_plus"] or 0) for r in results
                ),
                "vendor_count": len(results),
                "generated_at": datetime.now().isoformat(),
            }

            # Trigger n8n webhook
            n8n_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("ipai_finance_ap_aging.n8n_webhook_url")
            )

            if n8n_url:
                try:
                    _logger.info(f"Triggering n8n webhook at {n8n_url}")
                    response = requests.post(
                        n8n_url,
                        json=heatmap_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )
                    response.raise_for_status()
                    _logger.info(
                        f"n8n webhook triggered successfully: {response.status_code}"
                    )
                except requests.exceptions.RequestException as e:
                    # Log error but don't fail cron
                    _logger.error(
                        f"Failed to trigger n8n webhook: {str(e)}", exc_info=True
                    )
                    self.env["ir.logging"].sudo().create(
                        {
                            "name": "AP Aging Webhook Error",
                            "type": "server",
                            "level": "error",
                            "message": f"Failed to trigger n8n webhook: {str(e)}",
                            "func": "cron_generate_ap_aging_snapshot",
                            "path": "ipai_finance_ap_aging.models.account_move_line",
                        }
                    )
            else:
                _logger.warning(
                    "n8n webhook URL not configured (ir.config_parameter: ipai_finance_ap_aging.n8n_webhook_url)"
                )

            return heatmap_data

        except Exception as e:
            _logger.error(
                f"AP Aging snapshot generation failed: {str(e)}", exc_info=True
            )
            raise

    @api.model
    def get_ap_aging_summary(self, employee_code="RIM"):
        """
        Get AP Aging summary for dashboard KPIs.

        Args:
            employee_code (str): Employee code for filtering

        Returns:
            dict: Summary statistics
        """
        data = self.cron_generate_ap_aging_snapshot(employee_code)

        return {
            "total_payables": data["total_payables"],
            "vendor_count": data["vendor_count"],
            "total_overdue_90plus": data["total_overdue_90plus"],
            "snapshot_date": data["snapshot_date"],
        }
