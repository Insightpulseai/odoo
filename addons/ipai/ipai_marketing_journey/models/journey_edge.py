# -*- coding: utf-8 -*-
"""Marketing Journey Edge - connections between nodes."""

from odoo import api, fields, models


class MarketingJourneyEdge(models.Model):
    """Edge connecting two nodes in a marketing journey."""

    _name = "marketing.journey.edge"
    _description = "Marketing Journey Edge"
    _order = "source_node_id, sequence"

    name = fields.Char(compute="_compute_name", store=True)
    journey_id = fields.Many2one(
        "marketing.journey",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)

    source_node_id = fields.Many2one(
        "marketing.journey.node",
        string="From Node",
        required=True,
        ondelete="cascade",
        index=True,
    )
    target_node_id = fields.Many2one(
        "marketing.journey.node",
        string="To Node",
        required=True,
        ondelete="cascade",
        index=True,
    )

    edge_type = fields.Selection(
        [
            ("default", "Default"),
            ("true", "True Branch"),
            ("false", "False Branch"),
        ],
        default="default",
        help="Edge type for branch nodes",
    )

    # Optional label for visualization
    label = fields.Char()

    @api.depends("source_node_id.name", "target_node_id.name", "edge_type")
    def _compute_name(self):
        for edge in self:
            src = edge.source_node_id.name or "?"
            tgt = edge.target_node_id.name or "?"
            if edge.edge_type in ("true", "false"):
                edge.name = f"{src} -> [{edge.edge_type}] -> {tgt}"
            else:
                edge.name = f"{src} -> {tgt}"

    @api.constrains("source_node_id", "target_node_id")
    def _check_no_self_loop(self):
        """Prevent edges from pointing to themselves."""
        for edge in self:
            if edge.source_node_id == edge.target_node_id:
                raise models.ValidationError("An edge cannot connect a node to itself.")

    @api.constrains("source_node_id", "target_node_id", "journey_id")
    def _check_same_journey(self):
        """Ensure both nodes belong to the same journey."""
        for edge in self:
            if edge.source_node_id.journey_id != edge.journey_id:
                raise models.ValidationError(
                    "Source node must belong to the same journey."
                )
            if edge.target_node_id.journey_id != edge.journey_id:
                raise models.ValidationError(
                    "Target node must belong to the same journey."
                )
