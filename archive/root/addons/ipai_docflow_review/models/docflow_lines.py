from odoo import fields, models


class DocflowDocumentLine(models.Model):
    _name = "docflow.document.line"
    _description = "DocFlow Extracted Line Item"
    _order = "sequence, id"

    document_id = fields.Many2one("docflow.document", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)

    description = fields.Char(required=True, default="Item")
    quantity = fields.Float(default=1.0)
    unit_price = fields.Float(default=0.0)
    line_total = fields.Float(compute="_compute_line_total", store=True)

    def _compute_line_total(self):
        for r in self:
            r.line_total = (r.quantity or 0.0) * (r.unit_price or 0.0)
