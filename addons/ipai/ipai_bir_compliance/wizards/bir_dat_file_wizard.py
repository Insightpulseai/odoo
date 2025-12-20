# -*- coding: utf-8 -*-
import base64
from datetime import datetime

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class BirDatFileWizard(models.TransientModel):
    """Wizard to generate BIR RELIEF/Alphalist DAT files."""

    _name = "ipai.bir.dat.wizard"
    _description = "Generate BIR RELIEF/Alphalist File"

    date_start = fields.Date(
        string="Start Date",
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    report_type = fields.Selection(
        [
            ("relief", "RELIEF (Reconciliation of Listing for Enforcement)"),
            ("map", "MAP (Monthly Alphalist of Payees)"),
            ("sawt", "SAWT (Summary Alphalist of Withholding Taxes)"),
        ],
        string="Report Type",
        required=True,
        default="relief",
    )

    file_data = fields.Binary("DAT File", readonly=True)
    file_name = fields.Char("File Name", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        default="draft",
    )

    # Summary fields
    record_count = fields.Integer("Records Processed", readonly=True)
    total_amount = fields.Monetary(
        "Total Income", readonly=True, currency_field="currency_id"
    )
    total_tax = fields.Monetary(
        "Total Tax Withheld", readonly=True, currency_field="currency_id"
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )

    def generate_dat_file(self):
        """Generate the DAT file based on selected report type."""
        self.ensure_one()

        if self.date_start > self.date_end:
            raise UserError(_("Start date must be before end date."))

        # Fetch posted vendor invoices in date range
        invoices = self.env["account.move"].search(
            [
                ("move_type", "=", "in_invoice"),
                ("invoice_date", ">=", self.date_start),
                ("invoice_date", "<=", self.date_end),
                ("state", "=", "posted"),
            ]
        )

        if not invoices:
            raise UserError(
                _("No posted vendor invoices found in the selected date range.")
            )

        # Generate based on report type
        if self.report_type == "relief":
            content, stats = self._generate_relief(invoices)
        elif self.report_type == "map":
            content, stats = self._generate_map(invoices)
        else:
            content, stats = self._generate_sawt(invoices)

        # Create file
        period = self.date_start.strftime("%Y%m")
        self.file_data = base64.b64encode(content.encode("utf-8"))
        self.file_name = f"{self.report_type.upper()}_{period}.dat"
        self.state = "done"
        self.record_count = stats["count"]
        self.total_amount = stats["total_amount"]
        self.total_tax = stats["total_tax"]

        # Return same wizard with results
        return {
            "type": "ir.actions.act_window",
            "res_model": "ipai.bir.dat.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def _generate_relief(self, invoices):
        """
        Generate RELIEF (Reconciliation of Listing for Enforcement) format.

        BIR RELIEF format specification:
        - Fixed-width text file
        - One line per payee
        """
        lines = []
        company = self.env.company
        total_amount = 0.0
        total_tax = 0.0

        # Header record (H01)
        header = self._format_header_record(company)
        lines.append(header)

        # Detail records (D01)
        for inv in invoices:
            if not inv.partner_id.vat:
                continue  # Skip vendors without TIN

            ewt_amount = inv.ewt_amount or (inv.amount_untaxed * 0.02)

            detail = self._format_detail_record(inv, ewt_amount)
            lines.append(detail)

            total_amount += inv.amount_untaxed
            total_tax += ewt_amount

        # Control record (C01)
        control = self._format_control_record(len(invoices), total_amount, total_tax)
        lines.append(control)

        content = "\r\n".join(lines)
        return content, {
            "count": len(invoices),
            "total_amount": total_amount,
            "total_tax": total_tax,
        }

    def _generate_map(self, invoices):
        """Generate MAP (Monthly Alphalist of Payees) format."""
        lines = []
        total_amount = 0.0
        total_tax = 0.0

        for inv in invoices:
            tin = self._clean_tin(inv.partner_id.vat)
            name = (inv.partner_id.name or "")[:50].upper()
            amount = inv.amount_untaxed
            ewt = inv.ewt_amount or (amount * 0.02)

            # MAP format: TIN,Name,Address,Amount,Tax
            line = f"{tin},{name},{amount:.2f},{ewt:.2f}"
            lines.append(line)

            total_amount += amount
            total_tax += ewt

        content = "\r\n".join(lines)
        return content, {
            "count": len(invoices),
            "total_amount": total_amount,
            "total_tax": total_tax,
        }

    def _generate_sawt(self, invoices):
        """Generate SAWT (Summary Alphalist of Withholding Taxes) format."""
        lines = []
        total_amount = 0.0
        total_tax = 0.0

        # Group by partner
        partner_totals = {}
        for inv in invoices:
            partner = inv.partner_id
            if partner.id not in partner_totals:
                partner_totals[partner.id] = {
                    "partner": partner,
                    "amount": 0.0,
                    "tax": 0.0,
                }
            partner_totals[partner.id]["amount"] += inv.amount_untaxed
            ewt = inv.ewt_amount or (inv.amount_untaxed * 0.02)
            partner_totals[partner.id]["tax"] += ewt

        for data in partner_totals.values():
            partner = data["partner"]
            tin = self._clean_tin(partner.vat)
            name = (partner.name or "")[:50].upper()

            line = f"{tin},{name},{data['amount']:.2f},{data['tax']:.2f}"
            lines.append(line)

            total_amount += data["amount"]
            total_tax += data["tax"]

        content = "\r\n".join(lines)
        return content, {
            "count": len(partner_totals),
            "total_amount": total_amount,
            "total_tax": total_tax,
        }

    def _clean_tin(self, tin):
        """Clean TIN by removing dashes and padding."""
        if not tin:
            return "000000000000"
        return tin.replace("-", "").replace(" ", "").ljust(12, "0")[:12]

    def _format_header_record(self, company):
        """Format header record for RELIEF."""
        tin = self._clean_tin(company.vat)
        name = (company.name or "")[:50].ljust(50)
        period = self.date_end.strftime("%m%Y")
        return f"H01,{tin},{name},{period}"

    def _format_detail_record(self, invoice, ewt_amount):
        """Format detail record for RELIEF."""
        tin = self._clean_tin(invoice.partner_id.vat)
        name = (invoice.partner_id.name or "")[:50].ljust(50)
        amount = f"{invoice.amount_untaxed:015.2f}"
        tax = f"{ewt_amount:015.2f}"
        atc = "WC160"  # Default ATC for services
        return f"D01,{tin},{name},{atc},{amount},{tax}"

    def _format_control_record(self, count, total_amount, total_tax):
        """Format control/footer record for RELIEF."""
        return f"C01,{count:010d},{total_amount:015.2f},{total_tax:015.2f}"
