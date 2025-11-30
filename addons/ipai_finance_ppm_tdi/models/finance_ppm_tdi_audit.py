# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FinancePPMTDIAudit(models.Model):
    """
    Audit trail for Finance PPM Transaction Data Ingestion (TDI) operations.
    Tracks all data imports with detailed statistics and error logging.
    """

    _name = "finance.ppm.tdi.audit"
    _description = "Finance PPM TDI Audit Log"
    _order = "import_date desc, id desc"
    _rec_name = "display_name"

    # Import metadata
    import_type = fields.Selection(
        [
            ("team", "Finance Team Members"),
            ("tasks", "Month-End Closing Tasks"),
            ("bir", "BIR Filing Calendar"),
            ("logframe", "LogFrame KPI Definitions"),
        ],
        string="Import Type",
        required=True,
        index=True,
    )

    file_name = fields.Char(string="File Name", required=True)
    import_date = fields.Datetime(
        string="Import Date", required=True, default=fields.Datetime.now, index=True
    )

    user_id = fields.Many2one(
        "res.users",
        string="Imported By",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
    )

    # Import statistics
    records_created = fields.Integer(
        string="Records Created", default=0, help="Number of new records created"
    )
    records_updated = fields.Integer(
        string="Records Updated", default=0, help="Number of existing records updated"
    )
    records_skipped = fields.Integer(
        string="Records Skipped",
        default=0,
        help="Number of records skipped (already exist, update disabled)",
    )
    records_failed = fields.Integer(
        string="Records Failed",
        default=0,
        help="Number of records that failed to import",
    )

    total_records = fields.Integer(
        string="Total Records",
        compute="_compute_total_records",
        store=True,
        help="Total number of records processed",
    )

    success_rate = fields.Float(
        string="Success Rate (%)",
        compute="_compute_success_rate",
        store=True,
        help="Percentage of successfully imported records",
    )

    # Import results
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Completed"),
            ("partial", "Partial Success"),
            ("failed", "Failed"),
        ],
        string="State",
        default="draft",
        required=True,
        index=True,
    )

    import_summary = fields.Text(
        string="Import Summary", help="Summary of import operation"
    )

    error_log = fields.Text(
        string="Error Log", help="Detailed error messages from failed imports"
    )

    has_errors = fields.Boolean(
        string="Has Errors",
        compute="_compute_has_errors",
        store=True,
        help="True if import had any errors or failures",
    )

    # Display fields
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    @api.depends(
        "records_created", "records_updated", "records_skipped", "records_failed"
    )
    def _compute_total_records(self):
        """Calculate total number of records processed."""
        for audit in self:
            audit.total_records = (
                audit.records_created
                + audit.records_updated
                + audit.records_skipped
                + audit.records_failed
            )

    @api.depends("records_created", "records_updated", "total_records")
    def _compute_success_rate(self):
        """Calculate success rate percentage."""
        for audit in self:
            if audit.total_records > 0:
                successful = audit.records_created + audit.records_updated
                audit.success_rate = (successful / audit.total_records) * 100
            else:
                audit.success_rate = 0.0

    @api.depends("error_log", "records_failed")
    def _compute_has_errors(self):
        """Check if import had any errors."""
        for audit in self:
            audit.has_errors = bool(audit.error_log) or audit.records_failed > 0

    @api.depends("import_type", "file_name", "import_date")
    def _compute_display_name(self):
        """Generate display name for audit record."""
        for audit in self:
            import_type_label = dict(self._fields["import_type"].selection).get(
                audit.import_type, "Unknown"
            )

            date_str = fields.Datetime.to_string(audit.import_date)
            audit.display_name = f"{import_type_label} - {audit.file_name} ({date_str})"

    def action_view_details(self):
        """Open form view with import details."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Import Details",
            "res_model": "finance.ppm.tdi.audit",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_errors(self):
        """Display error log in a wizard."""
        self.ensure_one()
        if not self.error_log:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No Errors",
                    "message": "This import completed without errors.",
                    "type": "success",
                    "sticky": False,
                },
            }

        # Return a wizard displaying the error log
        return {
            "type": "ir.actions.act_window",
            "name": "Error Log",
            "res_model": "finance.ppm.tdi.audit",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"show_error_log": True},
        }

    def action_revert_import(self):
        """
        Placeholder for import rollback functionality.
        Would delete records created by this import operation.
        """
        self.ensure_one()
        _logger.warning(
            f"Revert import requested for audit {self.id} - not yet implemented"
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Not Implemented",
                "message": "Import rollback functionality is not yet available.",
                "type": "warning",
                "sticky": False,
            },
        }

    @api.model
    def get_import_statistics(self, import_type=None, date_from=None, date_to=None):
        """
        Get aggregated import statistics for dashboard/reporting.

        Args:
            import_type: Filter by import type (team/tasks/bir/logframe)
            date_from: Start date for filtering
            date_to: End date for filtering

        Returns:
            dict: Aggregated statistics
        """
        domain = []

        if import_type:
            domain.append(("import_type", "=", import_type))
        if date_from:
            domain.append(("import_date", ">=", date_from))
        if date_to:
            domain.append(("import_date", "<=", date_to))

        audits = self.search(domain)

        if not audits:
            return {
                "total_imports": 0,
                "successful_imports": 0,
                "failed_imports": 0,
                "total_records_created": 0,
                "total_records_updated": 0,
                "total_records_failed": 0,
                "average_success_rate": 0.0,
            }

        return {
            "total_imports": len(audits),
            "successful_imports": len(audits.filtered(lambda a: a.state == "done")),
            "failed_imports": len(audits.filtered(lambda a: a.state == "failed")),
            "total_records_created": sum(audits.mapped("records_created")),
            "total_records_updated": sum(audits.mapped("records_updated")),
            "total_records_failed": sum(audits.mapped("records_failed")),
            "average_success_rate": (
                sum(audits.mapped("success_rate")) / len(audits) if audits else 0.0
            ),
        }

    @api.model
    def cleanup_old_audits(self, days=90):
        """
        Archive or delete old audit records (data retention policy).

        Args:
            days: Number of days to retain audit logs (default 90)

        Returns:
            int: Number of records cleaned up
        """
        cutoff_date = fields.Datetime.subtract(fields.Datetime.now(), days=days)

        old_audits = self.search(
            [
                ("import_date", "<", cutoff_date),
                ("state", "in", ["done", "partial"]),
            ]
        )

        count = len(old_audits)
        old_audits.unlink()

        _logger.info(f"Cleaned up {count} audit records older than {days} days")

        return count
