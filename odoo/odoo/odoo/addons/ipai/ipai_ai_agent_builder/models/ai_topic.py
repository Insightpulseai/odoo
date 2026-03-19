# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IpaiAiTopic(models.Model):
    """Topic instruction bundle that assigns tools to an agent."""

    _name = "ipai.ai.topic"
    _description = "IPAI AI Topic"
    _order = "sequence, name"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    agent_id = fields.Many2one(
        comodel_name="ipai.ai.agent",
        string="Agent",
        required=True,
        ondelete="cascade",
        index=True,
    )
    instructions = fields.Text(
        string="Instructions",
        help="Instructions that guide the agent's behavior for this topic.",
    )
    tool_ids = fields.Many2many(
        comodel_name="ipai.ai.tool",
        relation="ipai_ai_topic_tool_rel",
        column1="topic_id",
        column2="tool_id",
        string="Tools",
        help="Tools available to the agent when this topic is active.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    company_id = fields.Many2one(
        related="agent_id.company_id",
        string="Company",
        store=True,
    )
