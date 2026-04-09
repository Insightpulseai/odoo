"""Extend account.move with TaxPulse review linkage and posting blocker.

Constitution C2.5: Block autoposting when validation fails.
"""

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    tax_review_ids = fields.One2many(
        "ipai.tax.review",
        "move_id",
        string="Tax Reviews",
    )
    tax_review_count = fields.Integer(
        string="Tax Review Count",
        compute="_compute_tax_review_count",
    )
    tax_review_state = fields.Selection(
        related="tax_review_ids.state",
        string="Tax Review Status",
        readonly=True,
    )

    @api.depends("tax_review_ids")
    def _compute_tax_review_count(self):
        for move in self:
            move.tax_review_count = len(move.tax_review_ids)

    def action_post(self):
        """Block posting if tax review is needs_review or rejected."""
        for move in self:
            blocking_reviews = move.tax_review_ids.filtered(
                lambda r: r.state in ("needs_review", "rejected")
            )
            if blocking_reviews:
                raise UserError(
                    "This document has unresolved tax review findings. "
                    "Please resolve or override the tax review before posting.\n\n"
                    f"Review: {blocking_reviews[0].name} — Status: {blocking_reviews[0].state}"
                )
        return super().action_post()

    def action_view_tax_reviews(self):
        """Open tax reviews for this document."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tax Reviews",
            "res_model": "ipai.tax.review",
            "domain": [("move_id", "=", self.id)],
            "view_mode": "tree,form",
            "context": {"default_move_id": self.id},
        }
