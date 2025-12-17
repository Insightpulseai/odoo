# -*- coding: utf-8 -*-
from odoo import fields, models


class ClosingGenerationRun(models.Model):
    """
    Audit log for each task generation run.

    Tracks what was created/updated for traceability and completeness reporting.
    """

    _name = "ipai.close.generation.run"
    _description = "Close/BIR Task Generation Run"
    _order = "create_date desc"

    seed_id = fields.Char(
        string="Seed ID",
        required=True,
        index=True,
        help="Identifier from the seed JSON (e.g., ipai_finance_ppm_closing_bir_seed_v1_1)",
    )
    cycle_code = fields.Char(
        string="Cycle Code",
        required=True,
        index=True,
        help="Cycle identifier (e.g., MONTH_END_CLOSE, BIR_TAX_FILING)",
    )
    cycle_key = fields.Char(
        string="Cycle Key",
        index=True,
        help="Instance key (e.g., MONTH_END_CLOSE|2025-11)",
    )
    dry_run = fields.Boolean(
        string="Dry Run",
        default=False,
        help="If True, no changes were persisted to the database.",
    )

    status = fields.Selection(
        [("pass", "PASS"), ("warn", "WARN"), ("fail", "FAIL")],
        string="Status",
        default="pass",
        required=True,
        help="Completeness status: PASS (no gaps), WARN (minor issues), FAIL (critical gaps)",
    )
    report_json = fields.Json(
        string="Report JSON",
        help="Detailed generation report with counts and issues.",
    )

    # Counters
    created_count = fields.Integer(
        string="Created",
        default=0,
        help="Number of tasks created in this run.",
    )
    updated_count = fields.Integer(
        string="Updated",
        default=0,
        help="Number of tasks updated in this run.",
    )
    unchanged_count = fields.Integer(
        string="Unchanged",
        default=0,
        help="Number of tasks that matched and required no update.",
    )
    obsolete_marked_count = fields.Integer(
        string="Obsolete Marked",
        default=0,
        help="Number of tasks marked as obsolete (no longer in seed).",
    )
    unresolved_assignee_count = fields.Integer(
        string="Unresolved Assignees",
        default=0,
        help="Number of tasks where assignee could not be resolved.",
    )

    # Relationships
    generated_map_ids = fields.One2many(
        "ipai.close.generated.map",
        "run_id",
        string="Generated Mappings",
    )


class ClosingGeneratedMap(models.Model):
    """
    Mapping between external keys and generated Odoo tasks.

    Provides the foundation for idempotent upserts - if an external_key exists,
    we update rather than create.
    """

    _name = "ipai.close.generated.map"
    _description = "Generated Task Map (External Key → Task)"
    _rec_name = "external_key"

    _sql_constraints = [
        (
            "external_key_uniq",
            "unique(external_key)",
            "External key must be unique.",
        )
    ]

    external_key = fields.Char(
        string="External Key",
        required=True,
        index=True,
        help="Deterministic key: {cycle_key}|{task_template_code}|{step_code}|{date_deadline}",
    )
    task_id = fields.Many2one(
        "project.task",
        string="Task",
        required=True,
        ondelete="cascade",
        index=True,
    )
    run_id = fields.Many2one(
        "ipai.close.generation.run",
        string="Generation Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    seed_hash = fields.Char(
        string="Seed Hash",
        index=True,
        help="SHA256 hash of the seed payload for change detection.",
    )
