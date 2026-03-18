from odoo import fields, models


class ExpenseOCRRun(models.Model):
    """Expense OCR Run - Audit trail for OCR extraction."""

    _name = "ipai.expense.ocr.run"
    _description = "Expense OCR Run (Audit)"
    _order = "create_date desc"

    expense_id = fields.Many2one(
        "hr.expense",
        string="Expense",
        required=True,
        ondelete="cascade",
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Receipt Attachment",
        required=True,
        ondelete="cascade",
    )
    status = fields.Selection(
        [("ok", "OK"), ("error", "Error")],
        string="Status",
        default="ok",
        required=True,
    )
    confidence = fields.Float(
        string="Confidence Score",
        default=0.0,
        help="OCR extraction confidence (0.0 - 1.0)",
    )
    merchant = fields.Char(
        string="Merchant",
        help="Extracted merchant/vendor name",
    )
    receipt_date = fields.Date(
        string="Receipt Date",
        help="Extracted date from receipt",
    )
    total = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        help="Extracted total amount",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    raw_json = fields.Json(
        string="Raw OCR Data",
        help="Complete JSON output from OCR engine",
    )
    error = fields.Text(
        string="Error Message",
        help="Error details if OCR failed",
    )
