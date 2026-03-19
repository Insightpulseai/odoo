# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class DocDigitizationConfig(models.Model):
    """Singleton configuration for Document Digitization / OCR integration.

    Stores non-secret metadata only. API keys and credentials are resolved
    at runtime via environment variables or Azure Key Vault.
    """

    _name = "ipai.doc.digitization.config"
    _description = "Document Digitization Configuration"
    _rec_name = "name"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(
        string="Name",
        default="Default",
        required=True,
    )
    provider = fields.Selection(
        selection=[
            ("azure_di", "Azure Document Intelligence"),
            ("tesseract", "Tesseract OCR"),
            ("custom", "Custom Endpoint"),
        ],
        string="Provider",
        default="azure_di",
        required=True,
    )
    endpoint = fields.Char(
        string="Endpoint URL",
        help="OCR / Document Intelligence endpoint URL (no secrets).",
    )
    model = fields.Char(
        string="Model",
        default="prebuilt-invoice",
        help="Document Intelligence model to use (e.g. prebuilt-invoice, prebuilt-receipt).",
    )
    storage_mode = fields.Selection(
        selection=[
            ("attachment", "Odoo Attachment"),
            ("azure_blob", "Azure Blob Storage"),
        ],
        string="Storage Mode",
        default="attachment",
        required=True,
    )
    async_enabled = fields.Boolean(
        string="Async Processing",
        default=True,
        help="Process documents asynchronously via background jobs.",
    )
    min_file_size = fields.Integer(
        string="Min File Size (KB)",
        default=0,
        help="Minimum file size in KB to process. Files below this threshold are skipped.",
    )
    last_test_date = fields.Datetime(
        string="Last Test Date",
        readonly=True,
    )
    last_test_result = fields.Char(
        string="Last Test Result",
        readonly=True,
    )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_test_connection(self):
        """Test connectivity to the configured OCR / Document Intelligence endpoint."""
        self.ensure_one()
        import requests  # noqa: PLC0415 — deferred import

        if not self.endpoint:
            result = _("No endpoint configured.")
            self.write(
                {
                    "last_test_date": fields.Datetime.now(),
                    "last_test_result": result,
                }
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Document Digitization Test"),
                    "message": result,
                    "type": "warning",
                    "sticky": False,
                },
            }

        try:
            resp = requests.get(
                self.endpoint.rstrip("/") + "/info",
                timeout=10,
            )
            if resp.status_code < 400:
                result = _("OK — HTTP %s") % resp.status_code
            else:
                result = _("Error — HTTP %s: %s") % (
                    resp.status_code,
                    resp.text[:200],
                )
        except requests.RequestException as exc:
            result = _("Connection failed: %s") % str(exc)[:200]

        self.write(
            {
                "last_test_date": fields.Datetime.now(),
                "last_test_result": result,
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Document Digitization Test"),
                "message": result,
                "type": "info" if "OK" in result else "warning",
                "sticky": False,
            },
        }
