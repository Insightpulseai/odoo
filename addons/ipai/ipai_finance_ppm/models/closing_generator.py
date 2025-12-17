# -*- coding: utf-8 -*-
"""
Finance PPM Closing Task Generator
===================================

Generative task creation from seed JSON templates with idempotent upsert strategy.

Generator Contract:
    INPUT: Seed JSON (cycles → phases → workstreams → task_templates → steps)
    PROCESS: Validate → Compute → Upsert → Audit
    OUTPUT: project.task records + Generation report (PASS/WARN/FAIL)

Idempotency Rules:
    - external_key uniqueness prevents duplicates
    - SHA256 hashing detects template changes
    - Upsert strategy: update if exists AND hash changed, create if new
    - Obsolete marking: tasks not in current seed get x_obsolete=True

Architecture:
    Seed JSON → Templates → Instance Generation → Task Upserts → Mapping Updates → Report

Example Usage:
    generator = env['ipai.close.generator']
    report = generator.generate_tasks_from_seed(
        seed_json_path='addons/ipai_finance_ppm/data/seed_v1_2_aligned.json',
        cycle_key='MONTH_END_CLOSE|2025-12',
        period_start='2025-12-01',
        period_end='2025-12-31',
        project_id=30,
        dry_run=False
    )
    # Returns: {"status": "PASS", "created": 15, "updated": 3, "obsolete": 0, "warnings": [], "errors": []}
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import hashlib
import logging
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr

_logger = logging.getLogger(__name__)


class ClosingGenerator(models.Model):
    """
    Generator Contract Implementation

    Orchestrates seed JSON processing → template storage → task generation → audit trail.
    """
    _name = 'ipai.close.generator'
    _description = 'Closing Task Generator'

    name = fields.Char(string='Generator Name', default='Finance Closing Task Generator')

    @api.model
    def generate_tasks_from_seed(self, seed_json_path=None, seed_json_dict=None, cycle_key=None,
                                  period_start=None, period_end=None, project_id=None, dry_run=True):
        """
        Main Generator Entry Point

        Args:
            seed_json_path (str): Path to seed JSON file (optional if seed_json_dict provided)
            seed_json_dict (dict): Seed JSON dictionary (optional if seed_json_path provided)
            cycle_key (str): Instance key (e.g., 'MONTH_END_CLOSE|2025-12')
            period_start (str|date): Period start date (ISO format or date object)
            period_end (str|date): Period end date (ISO format or date object)
            project_id (int): Target project ID for task creation
            dry_run (bool): If True, simulate without creating tasks (default: True)

        Returns:
            dict: Generation report with status, counts, warnings, errors
        """
        # Create generation run for audit trail
        generation_run = self.env['ipai.close.generation.run'].create({
            'cycle_key': cycle_key,
            'period_start': period_start,
            'period_end': period_end,
            'project_id': project_id,
            'dry_run': dry_run,
            'status': 'running',
            'start_time': fields.Datetime.now()
        })

        try:
            # Load seed JSON
            if seed_json_dict:
                seed_data = seed_json_dict
            elif seed_json_path:
                seed_data = self._load_seed_json(seed_json_path)
            else:
                raise ValidationError("Either seed_json_path or seed_json_dict must be provided")

            # Validate seed completeness
            validation_report = self._validate_seed_completeness(seed_data)
            if validation_report['status'] == 'FAIL':
                generation_run.write({
                    'status': 'failed',
                    'end_time': fields.Datetime.now(),
                    'report_json': json.dumps(validation_report)
                })
                return validation_report

            # Extract cycle configuration
            cycle_type = cycle_key.split('|')[0] if '|' in cycle_key else None
            cycle_config = next(
                (c for c in seed_data.get('cycles', []) if c.get('cycle_code') == cycle_type),
                None
            )

            if not cycle_config:
                raise ValidationError(f"Cycle type '{cycle_type}' not found in seed JSON")

            # Store/update templates
            self._upsert_templates(seed_data, generation_run)

            # Generate task instances
            task_report = self._generate_task_instances(
                cycle_config=cycle_config,
                cycle_key=cycle_key,
                period_start=period_start,
                period_end=period_end,
                project_id=project_id,
                generation_run=generation_run,
                dry_run=dry_run
            )

            # Mark obsolete tasks (not in current seed)
            if not dry_run:
                obsolete_count = self._mark_obsolete_tasks(cycle_key, generation_run)
                task_report['obsolete'] = obsolete_count

            # Finalize generation run
            final_report = {
                'status': validation_report['status'],  # PASS/WARN/FAIL
                'created': task_report.get('created', 0),
                'updated': task_report.get('updated', 0),
                'obsolete': task_report.get('obsolete', 0),
                'skipped': task_report.get('skipped', 0),
                'warnings': validation_report.get('warnings', []),
                'errors': validation_report.get('errors', []),
                'dry_run': dry_run
            }

            generation_run.write({
                'status': 'completed',
                'end_time': fields.Datetime.now(),
                'report_json': json.dumps(final_report),
                'task_count_created': final_report['created'],
                'task_count_updated': final_report['updated'],
                'task_count_obsolete': final_report['obsolete'],
                'task_count_skipped': final_report['skipped']
            })

            return final_report

        except Exception as e:
            generation_run.write({
                'status': 'failed',
                'end_time': fields.Datetime.now(),
                'report_json': json.dumps({
                    'status': 'FAIL',
                    'errors': [str(e)]
                })
            })
            _logger.error(f"Generator failed: {str(e)}", exc_info=True)
            raise

    def _load_seed_json(self, file_path):
        """Load and parse seed JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValidationError(f"Failed to load seed JSON: {str(e)}")

    def _validate_seed_completeness(self, seed_data):
        """
        Data Completeness Validation

        Returns:
            dict: {"status": "PASS|WARN|FAIL", "warnings": [...], "errors": [...]}
        """
        warnings = []
        errors = []

        # Required top-level keys
        required_keys = ['seed_id', 'cycles']
        for key in required_keys:
            if key not in seed_data:
                errors.append(f"Missing required key: {key}")

        # Check for version (can be either 'version' or 'seed_version')
        if 'version' not in seed_data and 'seed_version' not in seed_data:
            errors.append("Missing required key: version or seed_version")

        # Validate cycles
        cycles = seed_data.get('cycles', [])
        if not cycles:
            errors.append("No cycles defined in seed JSON")

        for cycle in cycles:
            # Required cycle fields
            if not cycle.get('cycle_code'):
                errors.append(f"Cycle missing cycle_code: {cycle}")
            if not cycle.get('phases'):
                warnings.append(f"Cycle {cycle.get('cycle_code')} has no phases")

            # Validate phases
            for phase in cycle.get('phases', []):
                if not phase.get('phase_code'):
                    errors.append(f"Phase missing phase_code in cycle {cycle.get('cycle_code')}")

                # Validate workstreams
                for workstream in phase.get('workstreams', []):
                    if not workstream.get('workstream_code'):
                        errors.append(f"Workstream missing workstream_code in phase {phase.get('phase_code')}")

                    # Validate task templates
                    for task_template in workstream.get('task_templates', []):
                        if not task_template.get('template_code'):
                            errors.append(f"Task template missing template_code in workstream {workstream.get('workstream_code')}")
                        if not task_template.get('task_name_template'):
                            errors.append(f"Task template {task_template.get('template_code')} missing task_name_template")

                        # Validate steps
                        for step in task_template.get('steps', []):
                            if not step.get('step_code'):
                                errors.append(f"Step missing step_code in template {task_template.get('template_code')}")

        # Determine status
        if errors:
            status = 'FAIL'
        elif warnings:
            status = 'WARN'
        else:
            status = 'PASS'

        return {
            'status': status,
            'warnings': warnings,
            'errors': errors
        }

    def _upsert_templates(self, seed_data, generation_run):
        """
        Store/Update Templates from Seed JSON

        Creates or updates ipai.close.task.template records.
        """
        template_model = self.env['ipai.close.task.template']

        for cycle in seed_data.get('cycles', []):
            cycle_code = cycle.get('cycle_code')

            for phase in cycle.get('phases', []):
                phase_code = phase.get('phase_code')
                phase_name = phase.get('name', phase.get('phase_name'))
                phase_seq = phase.get('sequence', 10)

                for workstream in phase.get('workstreams', []):
                    workstream_code = workstream.get('workstream_code')
                    workstream_name = workstream.get('name', workstream.get('workstream_name'))
                    workstream_seq = workstream.get('sequence', 10)

                    # NEW: Iterate through categories (v1.2.0 hierarchy)
                    for category in workstream.get('categories', []):
                        category_code = category.get('category_code')
                        category_name = category.get('name', category.get('category_name'))
                        category_seq = category.get('sequence', 10)

                        for task_template in category.get('task_templates', []):
                            template_code = task_template.get('template_code')

                            for step in task_template.get('steps', []):
                                step_code = step.get('step_code')
                                step_seq = step.get('sequence', 10)

                                # Compute full template code: TEMPLATE_CODE|STEP_CODE
                                full_template_code = f"{template_code}|{step_code}"

                                # Check if template exists
                                existing = template_model.search([
                                    ('template_code', '=', full_template_code),
                                    ('template_version', '=', seed_data.get('version', '1.0.0'))
                                ], limit=1)

                                template_vals = {
                                    'template_code': full_template_code,
                                    'template_version': seed_data.get('version', '1.0.0'),
                                    'cycle_code': cycle_code,
                                    'phase_code': phase_code,
                                    'phase_name': phase_name,
                                    'phase_seq': phase_seq,
                                    'workstream_code': workstream_code,
                                    'workstream_name': workstream_name,
                                    'workstream_seq': workstream_seq,
                                    'category_code': category_code,
                                    'category_name': category_name,
                                    'category_seq': category_seq,
                                    'template_seq': task_template.get('sequence', 10),
                                    'step_code': step_code,
                                    'step_seq': step_seq,
                                    'task_name_template': step.get('name_template', task_template.get('task_name_template')),
                                    'task_description': task_template.get('description'),
                                    'recurrence_rule': cycle.get('recurrence_rule'),
                                    'duration_days': step.get('duration_days', 1),
                                    'offset_from_period_end': step.get('due', {}).get('offset_business_days', 0),
                                    'responsible_role': step.get('responsible_role'),
                                    'employee_code': step.get('employee_code'),
                                    'wbs_code_template': task_template.get('wbs_code_template'),
                                    'critical_path': task_template.get('critical_path', False),
                                    'phase_type': phase.get('phase_type'),
                                    'is_active': True
                                }

                                if existing:
                                    existing.write(template_vals)
                                else:
                                    template_model.create(template_vals)

        _logger.info(f"Templates upserted for generation run {generation_run.id}")

    def _generate_task_instances(self, cycle_config, cycle_key, period_start, period_end,
                                  project_id, generation_run, dry_run):
        """
        Generate Task Instances from Templates

        Returns:
            dict: {"created": int, "updated": int, "skipped": int}
        """
        task_model = self.env['project.task']
        template_model = self.env['ipai.close.task.template']
        mapping_model = self.env['ipai.close.generated.map']

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Get all active templates for this cycle
        cycle_type = cycle_key.split('|')[0] if '|' in cycle_key else None
        templates = template_model.search([
            ('cycle_code', '=', cycle_type),
            ('is_active', '=', True)
        ])

        for template in templates:
            # Extract template code (remove step suffix)
            # template.template_code format: "CT_PAYROLL_PROCESSING|PREP"
            template_code_base = template.template_code.split('|')[0] if '|' in template.template_code else template.template_code

            # Compute external key: CYCLE_KEY|PHASE_CODE|WORKSTREAM_CODE|CATEGORY_CODE|TEMPLATE_CODE|STEP_CODE
            external_key = f"{cycle_key}|{template.phase_code}|{template.workstream_code}|{template.category_code}|{template_code_base}|{template.step_code}"

            # Check if task already exists
            existing_mapping = mapping_model.search([('external_key', '=', external_key)], limit=1)

            # Render task name from template
            task_name = self._render_task_name(template.task_name_template, period_start, period_end)

            # Compute deadline
            deadline = self._compute_deadline(period_end, template.offset_from_period_end)

            # Resolve assignee
            user_id = self._resolve_assignee(template.employee_code)

            task_vals = {
                'name': task_name,
                'description': template.task_description,
                'project_id': project_id,
                'date_deadline': deadline,
                'user_ids': [(6, 0, [user_id])] if user_id else [],
                'x_cycle_key': cycle_key,
                'x_task_template_code': template.template_code,
                'x_step_code': template.step_code,
                'x_external_key': external_key,
                'x_seed_hash': template.seed_hash,
                'x_obsolete': False
            }

            if dry_run:
                _logger.info(f"[DRY RUN] Would create/update task: {task_name}")
                if existing_mapping:
                    updated_count += 1
                else:
                    created_count += 1
                continue

            # Upsert logic
            if existing_mapping:
                # Update if seed hash changed
                if existing_mapping.task_id.x_seed_hash != template.seed_hash:
                    existing_mapping.task_id.write(task_vals)
                    existing_mapping.write({
                        'operation': 'updated',
                        'seed_hash_at_generation': template.seed_hash
                    })
                    updated_count += 1
                else:
                    # Skip if no changes
                    skipped_count += 1
            else:
                # Create new task
                new_task = task_model.create(task_vals)
                mapping_model.create({
                    'external_key': external_key,
                    'generation_run_id': generation_run.id,
                    'task_id': new_task.id,
                    'template_id': template.id,
                    'operation': 'created',
                    'seed_hash_at_generation': template.seed_hash
                })
                created_count += 1

        return {
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count
        }

    def _mark_obsolete_tasks(self, cycle_key, generation_run):
        """
        Mark Obsolete Tasks

        Tasks with x_cycle_key matching current cycle but NOT in current generation run
        are marked as x_obsolete=True.

        Returns:
            int: Number of tasks marked obsolete
        """
        task_model = self.env['project.task']
        mapping_model = self.env['ipai.close.generated.map']

        # Get all external keys from current generation run
        current_external_keys = mapping_model.search([
            ('generation_run_id', '=', generation_run.id)
        ]).mapped('external_key')

        # Find tasks with same cycle_key but not in current generation
        obsolete_tasks = task_model.search([
            ('x_cycle_key', '=', cycle_key),
            ('x_external_key', 'not in', current_external_keys),
            ('x_obsolete', '=', False)
        ])

        obsolete_tasks.write({'x_obsolete': True})

        return len(obsolete_tasks)

    def _render_task_name(self, template, period_start, period_end):
        """
        Render Task Name from Template

        Placeholders:
            {period}: 2025-12
            {month}: December
            {year}: 2025
            {month_abbr}: Dec
        """
        if isinstance(period_start, str):
            period_start = fields.Date.from_string(period_start)

        return template.format(
            period=period_start.strftime('%Y-%m'),
            month=period_start.strftime('%B'),
            year=period_start.strftime('%Y'),
            month_abbr=period_start.strftime('%b')
        )

    def _compute_deadline(self, period_end, offset_days):
        """
        Compute Task Deadline

        Args:
            period_end (str|date): Period end date
            offset_days (int): Negative = before period end, Positive = after period end

        Returns:
            date: Computed deadline
        """
        if isinstance(period_end, str):
            period_end = fields.Date.from_string(period_end)

        return period_end + timedelta(days=offset_days)

    def _resolve_assignee(self, employee_code):
        """
        Resolve Employee Code to User ID

        Args:
            employee_code (str): Employee code from template (e.g., 'RIM')

        Returns:
            int|bool: User ID if found, False otherwise
        """
        if not employee_code:
            return False

        user = self.env['res.users'].search([('x_employee_code', '=', employee_code)], limit=1)
        return user.id if user else False
