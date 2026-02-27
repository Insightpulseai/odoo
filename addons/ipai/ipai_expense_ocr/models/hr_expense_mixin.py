"""
hr.expense OCR mixin — adds "Digitize Receipt" action and audit smart button.

Extends hr.expense with:
- action_digitize_receipt(): POST latest image attachment to PaddleOCR → write back fields
- ocr_run_ids / ocr_run_count / ocr_confidence: computed from ipai.expense.ocr.run records
- action_open_ocr_runs(): opens audit list for this expense
"""

import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Confidence threshold below which a warning is shown (fields still fill)
LOW_CONFIDENCE_THRESHOLD = 0.4


class HrExpenseOCR(models.Model):
    _inherit = "hr.expense"

    ocr_run_ids = fields.One2many(
        "ipai.expense.ocr.run",
        "expense_id",
        string="OCR Runs",
        readonly=True,
    )
    ocr_run_count = fields.Integer(
        compute="_compute_ocr_run_count",
        string="OCR Scans",
        store=False,
    )
    ocr_confidence = fields.Float(
        compute="_compute_ocr_confidence",
        string="Last OCR Confidence",
        store=False,
    )

    @api.depends("ocr_run_ids")
    def _compute_ocr_run_count(self):
        for rec in self:
            rec.ocr_run_count = len(rec.ocr_run_ids)

    @api.depends("ocr_run_ids.confidence", "ocr_run_ids.status")
    def _compute_ocr_confidence(self):
        for rec in self:
            ok_runs = rec.ocr_run_ids.filtered(lambda r: r.status == "ok")
            rec.ocr_confidence = ok_runs[:1].confidence if ok_runs else 0.0

    # ------------------------------------------------------------------
    # Primary action
    # ------------------------------------------------------------------

    def action_digitize_receipt(self):
        """
        POST latest image attachment to PaddleOCR; write back extracted fields.

        Write-back rules (from prd.md):
        - Only writes to blank fields — never overwrites user-entered data
        - merchant → hr.expense.name
        - total    → hr.expense.unit_amount
        - date     → hr.expense.date
        - Creates ipai.expense.ocr.run audit record on every attempt
        """
        self.ensure_one()

        # 1. Find most recent image attachment
        att = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "hr.expense"),
                ("res_id", "=", self.id),
                ("mimetype", "like", "image/%"),
            ],
            limit=1,
            order="id desc",
        )
        if not att:
            raise UserError(
                _("No image attachment found. Upload a receipt image (JPEG, PNG) first.")
            )

        # 2. Read OCR endpoint from Odoo config
        endpoint = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ocr.endpoint_url", default="")
        )
        if not endpoint:
            raise UserError(
                _(
                    "OCR endpoint not configured. "
                    "Run scripts/odoo_config_mail_ai_ocr.py to set IPAI_OCR_ENDPOINT_URL."
                )
            )

        # 3. Decode attachment
        if not att.datas:
            raise UserError(_("Attachment has no data. Re-upload the receipt image."))
        image_bytes = base64.b64decode(att.datas)

        # 4. POST to PaddleOCR service
        from ..utils.ocr_client import fetch_image_text, parse_text

        try:
            raw_text = fetch_image_text(image_bytes, endpoint)
        except Exception as exc:
            _logger.warning("OCR service error for expense %s: %s", self.id, exc)
            self.env["ipai.expense.ocr.run"].create(
                {
                    "expense_id": self.id,
                    "attachment_id": att.id,
                    "status": "error",
                    "error": str(exc),
                }
            )
            raise UserError(_("OCR service error: %s") % str(exc)) from exc

        # 5. Parse extracted text
        result = parse_text(raw_text)

        # 6. Write back — blank fields only
        vals = {}
        if result.merchant and not self.name:
            vals["name"] = result.merchant[:100]
        if result.total and not self.unit_amount:
            vals["unit_amount"] = result.total
        if result.receipt_date and not self.date:
            vals["date"] = result.receipt_date
        if vals:
            self.write(vals)
        else:
            # All target fields already populated
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("No Changes"),
                    "message": _("Fields already populated — no changes made."),
                    "sticky": False,
                    "type": "info",
                },
            }

        # 7. Audit record
        self.env["ipai.expense.ocr.run"].create(
            {
                "expense_id": self.id,
                "attachment_id": att.id,
                "status": "ok",
                "confidence": result.confidence,
                "merchant": result.merchant,
                "receipt_date": result.receipt_date,
                "total": result.total,
                "raw_json": {"text": raw_text},
            }
        )

        # 8. Notification
        if result.confidence < LOW_CONFIDENCE_THRESHOLD:
            notif_type = "warning"
            title = _("Receipt Digitized (low confidence)")
            message = _(
                "Extracted: %(merchant)s | %(total)s | %(date)s\n"
                "Confidence %(pct)s%% — please verify the extracted values."
            ) % {
                "merchant": result.merchant or "—",
                "total": result.total or "—",
                "date": result.receipt_date or "—",
                "pct": int(result.confidence * 100),
            }
        else:
            notif_type = "success"
            title = _("Receipt Digitized")
            message = _(
                "Extracted: %(merchant)s | %(total)s | %(date)s (confidence %(pct)s%%)"
            ) % {
                "merchant": result.merchant or "—",
                "total": result.total or "—",
                "date": result.receipt_date or "—",
                "pct": int(result.confidence * 100),
            }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "sticky": notif_type == "warning",
                "type": notif_type,
            },
        }

    # ------------------------------------------------------------------
    # Smart button action
    # ------------------------------------------------------------------

    def action_open_ocr_runs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("OCR Scans"),
            "res_model": "ipai.expense.ocr.run",
            "domain": [("expense_id", "=", self.id)],
            "views": [(False, "list"), (False, "form")],
            "context": {"default_expense_id": self.id},
        }
