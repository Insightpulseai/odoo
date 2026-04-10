# -*- coding: utf-8 -*-
"""
expense_parity_config.py — Computed detection of installed adjacent OCA modules.

This is a lightweight TransientModel that acts as a runtime probe.
It does NOT store configuration; it detects installed modules on-demand.

Computed fields:
  dms_installed         — True if OCA dms module is installed
  auditlog_installed    — True if OCA auditlog module is installed
  queue_job_installed   — True if OCA queue_job module is installed
  mis_builder_installed — True if OCA mis_builder module is installed

Usage:
  config = self.env["expense.parity.config"].get_config()
  if config["dms_installed"]:
      ...
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_OCA_MODULES = {
    "dms_installed": "dms",
    "auditlog_installed": "auditlog",
    "queue_job_installed": "queue_job",
    "mis_builder_installed": "mis_builder",
}


class ExpenseParityConfig(models.TransientModel):
    """Runtime probe for adjacent OCA module detection.

    All fields are computed on-the-fly by querying ir.module.module.
    No records need to be created — call get_config() as a class-level helper.
    """

    _name = "expense.parity.config"
    _description = "Expense Parity OCA Module Detection"

    dms_installed = fields.Boolean(
        string="DMS Installed",
        compute="_compute_oca_detection",
        help="True if OCA 'dms' module is installed.",
    )
    auditlog_installed = fields.Boolean(
        string="Auditlog Installed",
        compute="_compute_oca_detection",
        help="True if OCA 'auditlog' module is installed.",
    )
    queue_job_installed = fields.Boolean(
        string="Queue Job Installed",
        compute="_compute_oca_detection",
        help="True if OCA 'queue_job' module is installed.",
    )
    mis_builder_installed = fields.Boolean(
        string="MIS Builder Installed",
        compute="_compute_oca_detection",
        help="True if OCA 'mis_builder' module is installed.",
    )

    @api.depends_context("uid")
    def _compute_oca_detection(self):
        """Detect which adjacent OCA modules are installed."""
        Module = self.env["ir.module.module"].sudo()
        for rec in self:
            for field_name, module_name in _OCA_MODULES.items():
                installed = Module.search_count(
                    [("name", "=", module_name), ("state", "=", "installed")]
                )
                rec[field_name] = bool(installed)

    @api.model
    def get_config(self):
        """Return a plain dict of detected OCA module presence.

        This is the preferred call pattern — avoids TransientModel record
        lifecycle complexity.

        Returns:
            dict: {field_name: bool} for all _OCA_MODULES entries.
        """
        Module = self.env["ir.module.module"].sudo()
        result = {}
        for field_name, module_name in _OCA_MODULES.items():
            installed = Module.search_count(
                [("name", "=", module_name), ("state", "=", "installed")]
            )
            result[field_name] = bool(installed)
            if installed:
                _logger.debug("expense_wiring: OCA module '%s' detected as installed.", module_name)
            else:
                _logger.debug("expense_wiring: OCA module '%s' not installed — soft wiring skipped.", module_name)
        return result
