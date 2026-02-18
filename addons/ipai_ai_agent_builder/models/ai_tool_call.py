# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IpaiAiToolCall(models.Model):
    """Tool invocation audit log."""

    _name = "ipai.ai.tool.call"
    _description = "IPAI AI Tool Call"
    _order = "create_date desc"

    run_id = fields.Many2one(
        comodel_name="ipai.ai.run",
        string="Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    tool_id = fields.Many2one(
        comodel_name="ipai.ai.tool",
        string="Tool",
        required=True,
        ondelete="restrict",
        index=True,
    )
    tool_key = fields.Char(
        related="tool_id.key",
        string="Tool Key",
        store=True,
    )
    input_json = fields.Text(
        string="Input JSON",
        help="The input parameters passed to the tool.",
    )
    output_json = fields.Text(
        string="Output JSON",
        help="The output returned by the tool.",
    )
    status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("success", "Success"),
            ("error", "Error"),
            ("dry_run", "Dry Run"),
        ],
        string="Status",
        default="pending",
        required=True,
    )
    error_message = fields.Text(
        string="Error Message",
        help="Error message if the tool execution failed.",
    )
    dry_run = fields.Boolean(
        string="Dry Run",
        default=False,
    )
    execution_time_ms = fields.Integer(
        string="Execution Time (ms)",
    )
    create_date = fields.Datetime(
        string="Created At",
        readonly=True,
    )
    user_id = fields.Many2one(
        related="run_id.user_id",
        string="User",
        store=True,
    )
    company_id = fields.Many2one(
        related="run_id.company_id",
        string="Company",
        store=True,
    )
