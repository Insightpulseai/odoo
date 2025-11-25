# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    """Extend account.move for BIR 2307 compliance."""
    _inherit = 'account.move'

    # BIR 2307 Fields
    bir_2307_generated = fields.Boolean(
        string='2307 Generated',
        default=False,
        help='Indicates if BIR Form 2307 has been generated for this invoice'
    )
    bir_2307_date = fields.Date(
        string='2307 Date',
        help='Date when BIR Form 2307 was generated'
    )

    # Withholding Tax Summary
    ewt_amount = fields.Monetary(
        string='EWT Amount',
        compute='_compute_ewt_amount',
        store=True,
        help='Total Expanded Withholding Tax amount'
    )

    @api.depends('line_ids.tax_line_id', 'line_ids.balance')
    def _compute_ewt_amount(self):
        """Compute total EWT from tax lines."""
        for move in self:
            ewt_total = 0.0
            for line in move.line_ids:
                # Check if this is a withholding tax line (typically negative)
                if line.tax_line_id and 'EWT' in (line.tax_line_id.name or '').upper():
                    ewt_total += abs(line.balance)
            move.ewt_amount = ewt_total

    def action_generate_bir_2307(self):
        """Generate BIR Form 2307 for this invoice."""
        self.ensure_one()
        self.write({
            'bir_2307_generated': True,
            'bir_2307_date': fields.Date.today(),
        })
        return self.env.ref('ipai_bir_compliance.action_report_bir_2307').report_action(self)

    def get_ewt_lines(self):
        """Get invoice lines that have withholding tax applied."""
        self.ensure_one()
        return self.invoice_line_ids.filtered(
            lambda l: any('EWT' in (t.name or '').upper() for t in l.tax_ids)
        )
