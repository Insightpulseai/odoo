# -*- coding: utf-8 -*-
import logging

from odoo.exceptions import UserError, ValidationError

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SpectraExportWizard(models.TransientModel):
    """
    Wizard for creating Spectra export batches.

    Multi-step wizard workflow:
    1. Configure: Select date range and export type
    2. Preview: Show records that will be exported
    3. Generate: Create export batch and CSV file
    """

    _name = "tbwa.spectra.export.wizard"
    _description = "Spectra Export Wizard"

    # Step control
    state = fields.Selection(
        [
            ("configure", "Configure"),
            ("preview", "Preview"),
            ("done", "Done"),
        ],
        default="configure",
        string="State",
    )

    # Configuration fields
    period_start = fields.Date(
        string="Period Start",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    period_end = fields.Date(
        string="Period End", required=True, default=fields.Date.today
    )
    export_type = fields.Selection(
        [
            ("cash_advance", "Cash Advances"),
            ("expense_report", "Expense Reports"),
            ("journal_entry", "Journal Entries"),
        ],
        default="cash_advance",
        required=True,
        string="Export Type",
    )

    # Preview fields
    preview_count = fields.Integer(string="Records to Export", readonly=True)
    preview_total_amount = fields.Monetary(
        string="Total Amount", readonly=True, currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Result fields
    export_batch_id = fields.Many2one(
        "tbwa.spectra.export", string="Export Batch", readonly=True
    )

    @api.constrains("period_start", "period_end")
    def _check_period_dates(self):
        """Validate that period_end >= period_start."""
        for wizard in self:
            if wizard.period_end < wizard.period_start:
                raise ValidationError(_("Period end date must be after start date"))

    def action_preview(self):
        """
        Move to preview step and calculate what will be exported.
        """
        self.ensure_one()

        # Get records that will be exported
        domain = self._get_export_domain()

        if self.export_type == "cash_advance":
            records = self.env["hr.expense.advance"].search(domain)
            self.preview_count = len(records)
            self.preview_total_amount = sum(records.mapped("amount"))
        elif self.export_type == "expense_report":
            # Expense reports implementation
            records = self.env["hr.expense.sheet"].search(domain)
            self.preview_count = len(records)
            self.preview_total_amount = sum(records.mapped("total_amount"))
        else:
            # Journal entries implementation
            self.preview_count = 0
            self.preview_total_amount = 0.0

        if self.preview_count == 0:
            raise UserError(_("No records found for the selected period and type"))

        self.state = "preview"

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_generate(self):
        """
        Generate the export batch and CSV file.
        """
        self.ensure_one()

        # Create export batch
        export_batch = self.env["tbwa.spectra.export"].create(
            {
                "period_start": self.period_start,
                "period_end": self.period_end,
                "export_type": self.export_type,
                "state": "draft",
            }
        )

        # Add records to export batch
        domain = self._get_export_domain()

        if self.export_type == "cash_advance":
            records = self.env["hr.expense.advance"].search(domain)
            export_batch.write({"advance_ids": [(6, 0, records.ids)]})
        elif self.export_type == "expense_report":
            # Expense reports implementation
            records = self.env["hr.expense.sheet"].search(domain)
            export_batch.write({"expense_sheet_ids": [(6, 0, records.ids)]})

        # Generate CSV file
        try:
            export_batch.action_export_csv()
        except Exception as e:
            _logger.error(
                f"Failed to generate CSV for export batch {export_batch.name}: {e}"
            )
            raise UserError(_("Failed to generate CSV file: %s") % str(e))

        self.export_batch_id = export_batch
        self.state = "done"

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_view_export_batch(self):
        """
        Open the created export batch.
        """
        self.ensure_one()

        if not self.export_batch_id:
            raise UserError(_("No export batch has been created yet"))

        return {
            "type": "ir.actions.act_window",
            "res_model": "tbwa.spectra.export",
            "res_id": self.export_batch_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_cancel(self):
        """
        Close the wizard without creating export.
        """
        return {"type": "ir.actions.act_window_close"}

    def _get_export_domain(self):
        """
        Build domain for records to export based on wizard configuration.
        """
        self.ensure_one()

        if self.export_type == "cash_advance":
            # Cash advances: approved and paid within period
            return [
                ("state", "in", ["approved_l2", "paid", "liquidating", "done"]),
                ("approval_date", ">=", self.period_start),
                ("approval_date", "<=", self.period_end),
                ("exported_to_spectra", "=", False),
            ]
        elif self.export_type == "expense_report":
            # Expense reports: approved within period
            return [
                ("state", "in", ["approve", "done"]),
                ("approval_date", ">=", self.period_start),
                ("approval_date", "<=", self.period_end),
                ("exported_to_spectra", "=", False),
            ]
        else:
            # Journal entries
            return [
                ("date", ">=", self.period_start),
                ("date", "<=", self.period_end),
            ]
