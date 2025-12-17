# -*- coding: utf-8 -*-
"""
Finance PPM Closing Generator Models
====================================

Core models for generative task creation from seed JSON templates:

1. ipai.close.task.template - Template storage (cycles, phases, workstreams, tasks, steps)
2. ipai.close.generation.run - Audit trail for generator executions
3. ipai.close.generated.map - External key → Odoo task ID mapping

Architecture:
    Seed JSON → Templates → Generation Run → Task Instances → Mapping

Idempotency:
    - external_key uniqueness constraint prevents duplicates
    - SHA256 hashing detects template changes
    - Upsert strategy: update if exists, create if new
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import hashlib
import json
import logging

_logger = logging.getLogger(__name__)


class CloseTaskTemplate(models.Model):
    """
    Template Storage for Generative Task Creation

    Stores hierarchical structure from seed JSON:
    - Cycles (MONTH_END_CLOSE, QUARTER_END_CLOSE, etc.)
    - Phases (top-level grouping)
    - Workstreams (process grouping)
    - Task Templates (repeatable task definitions)
    - Steps (PREP, REVIEW, APPROVAL)

    Templates are instantiated by the generator to create actual project.task records.
    """
    _name = 'ipai.close.task.template'
    _description = 'Closing Task Template'
    _order = 'cycle_code, phase_seq, workstream_seq, template_seq, step_seq'

    # Template Identity
    template_code = fields.Char(
        string='Template Code',
        required=True,
        index=True,
        help='Unique template identifier (e.g., CT_PAYROLL_PERSONNEL)'
    )
    template_version = fields.Char(
        string='Version',
        default='1.0.0',
        help='Semantic version for template evolution'
    )

    # Hierarchy
    cycle_code = fields.Selection([
        ('MONTH_END_CLOSE', 'Month-End Close'),
        ('QUARTER_END_CLOSE', 'Quarter-End Close'),
        ('YEAR_END_CLOSE', 'Year-End Close'),
        ('BIR_TAX_FILING', 'BIR Tax Filing'),
        ('TAX_FILING_MONTHLY', 'Tax Filing - Monthly'),
        ('TAX_FILING_QUARTERLY', 'Tax Filing - Quarterly'),
        ('TAX_FILING_ANNUAL', 'Tax Filing - Annual')
    ], string='Cycle Type', required=True, index=True)

    phase_code = fields.Char(
        string='Phase Code',
        required=True,
        index=True,
        help='Phase identifier (e.g., PHASE_RECON, PHASE_JE, PHASE_REPORTS)'
    )
    phase_name = fields.Char(string='Phase Name', required=True)
    phase_seq = fields.Integer(string='Phase Sequence', default=10)

    workstream_code = fields.Char(
        string='Workstream Code',
        index=True,
        help='Process grouping (e.g., WS_BANK_RECON, WS_GL_RECON)'
    )
    workstream_name = fields.Char(string='Workstream Name')
    workstream_seq = fields.Integer(string='Workstream Sequence', default=10)

    category_code = fields.Char(
        string='Category Code',
        index=True,
        help='Category identifier (e.g., PAYROLL_PERSONNEL, SSS_PHILHEALTH)'
    )
    category_name = fields.Char(string='Category Name')
    category_seq = fields.Integer(string='Category Sequence', default=10)

    template_seq = fields.Integer(string='Template Sequence', default=10)

    step_code = fields.Selection([
        ('PREP', 'Preparation'),
        ('REVIEW', 'Review'),
        ('APPROVAL', 'Approval'),
        ('REPORT_APPROVAL', 'Report Approval'),
        ('PAYMENT_APPROVAL', 'Payment Approval'),
        ('FILE_PAY', 'File & Pay'),
        ('EXEC', 'Execution'),
        ('VALIDATE', 'Validation')
    ], string='Step Type', index=True)
    step_seq = fields.Integer(string='Step Sequence', default=10)

    # Task Definition
    task_name_template = fields.Char(
        string='Task Name Template',
        required=True,
        help='Template with placeholders: {period}, {month}, {year}, etc.'
    )
    task_description = fields.Text(string='Description')

    # Scheduling
    recurrence_rule = fields.Char(
        string='Recurrence Rule',
        help='RRULE format (e.g., FREQ=MONTHLY;BYMONTHDAY=1)'
    )
    duration_days = fields.Integer(string='Duration (days)', default=1)
    offset_from_period_end = fields.Integer(
        string='Offset from Period End',
        help='Negative = before period end, Positive = after period end'
    )

    # Assignment
    responsible_role = fields.Char(
        string='Responsible Role',
        help='Generic role (e.g., FINANCE_SUPERVISOR, SENIOR_MANAGER)'
    )
    employee_code = fields.Char(
        string='Default Employee Code',
        help='Default assignee employee code'
    )

    # Clarity PPM Fields
    wbs_code_template = fields.Char(
        string='WBS Code Template',
        help='Template for WBS code generation'
    )
    critical_path = fields.Boolean(string='On Critical Path', default=False)
    phase_type = fields.Selection([
        ('initial', 'Initial'),
        ('accruals', 'Accruals'),
        ('review', 'Review'),
        ('finalization', 'Finalization'),
        ('tax_filing', 'Tax Filing'),
        ('initiation', 'Initiation'),
        ('planning', 'Planning'),
        ('execution', 'Execution'),
        ('monitoring', 'Monitoring'),
        ('closeout', 'Closeout')
    ], string='Phase Type')

    # Metadata
    is_active = fields.Boolean(string='Active', default=True, index=True)
    seed_hash = fields.Char(
        string='Seed Hash',
        compute='_compute_seed_hash',
        store=True,
        index=True,
        help='SHA256 hash for change detection'
    )

    _sql_constraints = [
        ('template_code_uniq', 'UNIQUE(template_code, template_version)',
         'Template code + version must be unique')
    ]

    @api.depends('template_code', 'cycle_code', 'phase_code', 'workstream_code', 'category_code',
                 'task_name_template', 'step_code', 'duration_days', 'offset_from_period_end')
    def _compute_seed_hash(self):
        """Compute SHA256 hash of template payload for change detection"""
        for record in self:
            payload = {
                'template_code': record.template_code,
                'cycle_code': record.cycle_code,
                'phase_code': record.phase_code,
                'workstream_code': record.workstream_code,
                'category_code': record.category_code,
                'task_name_template': record.task_name_template,
                'step_code': record.step_code,
                'duration_days': record.duration_days,
                'offset_from_period_end': record.offset_from_period_end,
                'employee_code': record.employee_code,
                'critical_path': record.critical_path
            }
            payload_str = json.dumps(payload, sort_keys=True)
            record.seed_hash = hashlib.sha256(payload_str.encode()).hexdigest()


class CloseGenerationRun(models.Model):
    """
    Audit Trail for Generator Executions

    Tracks each generator run with:
    - Input parameters (cycle_key, dry_run mode)
    - Execution status (pending, running, completed, failed)
    - Output report (counts, warnings, errors)
    - Timestamp and user tracking
    """
    _name = 'ipai.close.generation.run'
    _description = 'Closing Task Generation Run'
    _order = 'create_date DESC'

    # Run Identity
    name = fields.Char(
        string='Run Name',
        compute='_compute_name',
        store=True
    )
    seed_id = fields.Char(
        string='Seed ID',
        help='Unique identifier from seed JSON (e.g., seed-v1.2.0-20251121)'
    )
    seed_version = fields.Char(string='Seed Version', default='1.0.0')

    # Input Parameters
    cycle_key = fields.Char(
        string='Cycle Key',
        required=True,
        index=True,
        help='Instance key: MONTH_END_CLOSE|2025-11'
    )
    cycle_type = fields.Selection([
        ('MONTH_END_CLOSE', 'Month-End Close'),
        ('QUARTER_END_CLOSE', 'Quarter-End Close'),
        ('YEAR_END_CLOSE', 'Year-End Close'),
        ('BIR_TAX_FILING', 'BIR Tax Filing'),
        ('TAX_FILING_MONTHLY', 'Tax Filing - Monthly'),
        ('TAX_FILING_QUARTERLY', 'Tax Filing - Quarterly')
    ], string='Cycle Type', compute='_compute_cycle_type', store=True)

    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)

    dry_run = fields.Boolean(
        string='Dry Run',
        default=True,
        help='If True, simulate without creating tasks'
    )

    # Execution Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending', required=True, tracking=True)

    # Output Report
    report_json = fields.Text(
        string='Generation Report',
        help='JSON report with counts, warnings, errors'
    )
    report_status = fields.Selection([
        ('PASS', 'Pass'),
        ('WARN', 'Warning'),
        ('FAIL', 'Fail')
    ], string='Report Status', compute='_compute_report_status', store=True)

    # Counts
    task_count_created = fields.Integer(string='Tasks Created', default=0)
    task_count_updated = fields.Integer(string='Tasks Updated', default=0)
    task_count_obsolete = fields.Integer(string='Tasks Obsoleted', default=0)
    task_count_skipped = fields.Integer(string='Tasks Skipped', default=0)

    warning_count = fields.Integer(string='Warnings', compute='_compute_counts', store=True)
    error_count = fields.Integer(string='Errors', compute='_compute_counts', store=True)

    # Relationships
    project_id = fields.Many2one(
        'project.project',
        string='Target Project',
        help='Project where tasks will be created'
    )
    generated_task_ids = fields.One2many(
        'ipai.close.generated.map',
        'generation_run_id',
        string='Generated Tasks'
    )

    # Metadata
    user_id = fields.Many2one('res.users', string='Executed By', default=lambda self: self.env.user)
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration_seconds = fields.Integer(
        string='Duration (seconds)',
        compute='_compute_duration',
        store=True
    )

    @api.depends('cycle_key', 'create_date')
    def _compute_name(self):
        """Generate run name: CYCLE_KEY @ TIMESTAMP"""
        for record in self:
            if record.create_date:
                timestamp = fields.Datetime.to_string(record.create_date)[:16]
                record.name = f"{record.cycle_key} @ {timestamp}"
            else:
                record.name = record.cycle_key or 'New Run'

    @api.depends('cycle_key')
    def _compute_cycle_type(self):
        """Extract cycle type from cycle_key (before |)"""
        for record in self:
            if record.cycle_key and '|' in record.cycle_key:
                record.cycle_type = record.cycle_key.split('|')[0]
            else:
                record.cycle_type = False

    @api.depends('report_json')
    def _compute_report_status(self):
        """Determine report status from JSON: FAIL if errors, WARN if warnings, else PASS"""
        for record in self:
            if not record.report_json:
                record.report_status = False
                continue

            try:
                report = json.loads(record.report_json)
                errors = report.get('errors', [])
                warnings = report.get('warnings', [])

                if errors:
                    record.report_status = 'FAIL'
                elif warnings:
                    record.report_status = 'WARN'
                else:
                    record.report_status = 'PASS'
            except (json.JSONDecodeError, KeyError):
                record.report_status = False

    @api.depends('report_json')
    def _compute_counts(self):
        """Extract warning/error counts from report_json"""
        for record in self:
            if not record.report_json:
                record.warning_count = 0
                record.error_count = 0
                continue

            try:
                report = json.loads(record.report_json)
                record.warning_count = len(report.get('warnings', []))
                record.error_count = len(report.get('errors', []))
            except (json.JSONDecodeError, KeyError):
                record.warning_count = 0
                record.error_count = 0

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        """Calculate duration in seconds"""
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration_seconds = int(delta.total_seconds())
            else:
                record.duration_seconds = 0


class CloseGeneratedMap(models.Model):
    """
    External Key → Odoo Task ID Mapping

    Ensures idempotent task generation:
    - external_key uniqueness prevents duplicate task creation
    - Supports upsert strategy: if external_key exists, update; else create
    - Links back to generation run for audit trail
    """
    _name = 'ipai.close.generated.map'
    _description = 'Generated Task Mapping'
    _order = 'generation_run_id DESC, external_key'

    # Mapping Identity
    external_key = fields.Char(
        string='External Key',
        required=True,
        index=True,
        help='Full deduplication key: CYCLE_KEY|TEMPLATE_CODE|STEP_CODE'
    )

    # Relationships
    generation_run_id = fields.Many2one(
        'ipai.close.generation.run',
        string='Generation Run',
        required=True,
        ondelete='cascade',
        index=True
    )
    task_id = fields.Many2one(
        'project.task',
        string='Odoo Task',
        required=True,
        ondelete='cascade',
        index=True
    )
    template_id = fields.Many2one(
        'ipai.close.task.template',
        string='Source Template',
        ondelete='set null'
    )

    # Metadata
    operation = fields.Selection([
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('skipped', 'Skipped')
    ], string='Operation', required=True)

    seed_hash_at_generation = fields.Char(
        string='Seed Hash',
        help='Template hash at time of generation (for change detection)'
    )

    _sql_constraints = [
        ('external_key_uniq', 'UNIQUE(external_key)',
         'External key must be unique (prevents duplicate task creation)')
    ]

    @api.model
    def get_or_create_mapping(self, external_key, generation_run_id, template_id=None):
        """
        Idempotent Mapping Retrieval

        Returns:
            tuple: (mapping_record, is_new)
                - mapping_record: existing or new ipai.close.generated.map
                - is_new: True if created, False if found existing
        """
        existing = self.search([('external_key', '=', external_key)], limit=1)

        if existing:
            return existing, False
        else:
            new_mapping = self.create({
                'external_key': external_key,
                'generation_run_id': generation_run_id,
                'template_id': template_id,
                'operation': 'created'
            })
            return new_mapping, True
