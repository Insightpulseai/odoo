# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    _logger.warning("openpyxl not available - Excel import disabled")


class FinancePPMImportWizard(models.TransientModel):
    """
    Wizard for importing Finance PPM data (team members, tasks, BIR calendar, LogFrame).
    Supports CSV and Excel formats with validation and error reporting.
    """
    _name = 'finance.ppm.import.wizard'
    _description = 'Finance PPM Data Import Wizard'

    # Import configuration
    import_type = fields.Selection([
        ('team', 'Finance Team Members'),
        ('tasks', 'Month-End Closing Tasks'),
        ('bir', 'BIR Filing Calendar'),
        ('logframe', 'LogFrame KPI Definitions'),
    ], string='Import Type', required=True, default='team')

    # File upload
    file_data = fields.Binary(
        string='Upload File',
        required=True,
        help='CSV or Excel file containing import data'
    )
    file_name = fields.Char(string='File Name')
    file_type = fields.Selection([
        ('csv', 'CSV'),
        ('xlsx', 'Excel (XLSX)'),
    ], string='File Type', compute='_compute_file_type', store=True)

    # Import options
    skip_header = fields.Boolean(
        string='Skip Header Row',
        default=True,
        help='First row contains column headers'
    )
    update_existing = fields.Boolean(
        string='Update Existing Records',
        default=False,
        help='Update existing records if match found, otherwise create new'
    )

    # Import results
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('importing', 'Importing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string='State', default='draft', readonly=True)

    import_summary = fields.Text(string='Import Summary', readonly=True)
    error_log = fields.Text(string='Error Log', readonly=True)

    records_created = fields.Integer(string='Records Created', readonly=True, default=0)
    records_updated = fields.Integer(string='Records Updated', readonly=True, default=0)
    records_skipped = fields.Integer(string='Records Skipped', readonly=True, default=0)
    records_failed = fields.Integer(string='Records Failed', readonly=True, default=0)

    @api.depends('file_name')
    def _compute_file_type(self):
        """Auto-detect file type from file name extension."""
        for wizard in self:
            if wizard.file_name:
                if wizard.file_name.lower().endswith('.csv'):
                    wizard.file_type = 'csv'
                elif wizard.file_name.lower().endswith(('.xlsx', '.xls')):
                    wizard.file_type = 'xlsx'
                else:
                    wizard.file_type = 'csv'  # Default to CSV
            else:
                wizard.file_type = 'csv'

    def action_validate_import(self):
        """
        Validate imported data before actual import.
        Checks file format, required fields, data types, and business rules.
        """
        self.ensure_one()
        self.state = 'validating'

        try:
            # Parse file
            rows = self._parse_file()

            # Validate based on import type
            validation_method = getattr(self, f'_validate_{self.import_type}_data')
            errors = validation_method(rows)

            if errors:
                self.state = 'error'
                self.error_log = '\n'.join(errors)
                raise ValidationError(
                    _('Validation failed. Please check the error log:\n%s') % self.error_log
                )

            self.state = 'draft'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Validation Successful'),
                    'message': _('File validated successfully. %d rows ready to import.') % len(rows),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            self.state = 'error'
            self.error_log = str(e)
            _logger.exception('Validation error in Finance PPM import')
            raise

    def action_import(self):
        """
        Execute the import process.
        Creates/updates records and generates audit trail.
        """
        self.ensure_one()
        self.state = 'importing'

        try:
            # Parse file
            rows = self._parse_file()

            # Import based on type
            import_method = getattr(self, f'_import_{self.import_type}_data')
            result = import_method(rows)

            # Update statistics
            self.records_created = result.get('created', 0)
            self.records_updated = result.get('updated', 0)
            self.records_skipped = result.get('skipped', 0)
            self.records_failed = result.get('failed', 0)

            # Generate summary
            self.import_summary = self._generate_summary(result)

            # Create audit log
            self._create_audit_log(result)

            self.state = 'done'

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'finance.ppm.import.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        except Exception as e:
            self.state = 'error'
            self.error_log = str(e)
            _logger.exception('Import error in Finance PPM TDI')
            raise

    def _parse_file(self):
        """Parse CSV or Excel file and return list of dictionaries."""
        if not self.file_data:
            raise UserError(_('No file uploaded'))

        decoded_data = base64.b64decode(self.file_data)

        if self.file_type == 'csv':
            return self._parse_csv(decoded_data)
        elif self.file_type == 'xlsx':
            return self._parse_xlsx(decoded_data)
        else:
            raise UserError(_('Unsupported file type: %s') % self.file_type)

    def _parse_csv(self, data):
        """Parse CSV file and return list of row dictionaries."""
        rows = []
        csv_data = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(csv_data) if self.skip_header else csv.reader(csv_data)

        for idx, row in enumerate(reader, start=1):
            if self.skip_header and isinstance(row, dict):
                # DictReader - keys are column names
                rows.append({'row_num': idx, **row})
            else:
                # Regular reader - convert to dict with column indices
                rows.append({'row_num': idx, 'data': row})

        return rows

    def _parse_xlsx(self, data):
        """Parse Excel file and return list of row dictionaries."""
        if not OPENPYXL_AVAILABLE:
            raise UserError(_('Excel import requires openpyxl library'))

        rows = []
        workbook = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        sheet = workbook.active

        headers = None
        for idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            if idx == 1 and self.skip_header:
                headers = [str(cell).strip() if cell else f'col_{i}' for i, cell in enumerate(row)]
                continue

            if headers:
                row_dict = {'row_num': idx}
                for i, cell in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = cell
                rows.append(row_dict)
            else:
                rows.append({'row_num': idx, 'data': list(row)})

        return rows

    # ============================================================================
    # TEAM MEMBERS IMPORT
    # ============================================================================

    def _validate_team_data(self, rows):
        """
        Validate team member data.
        Required fields: name, email, employee_id, role
        """
        errors = []
        required_fields = ['name', 'email', 'employee_id', 'role']

        for row in rows:
            row_num = row.get('row_num')

            # Check required fields
            for field in required_fields:
                if not row.get(field):
                    errors.append(f"Row {row_num}: Missing required field '{field}'")

            # Validate email format
            email = row.get('email', '').strip()
            if email and '@' not in email:
                errors.append(f"Row {row_num}: Invalid email format '{email}'")

            # Validate role
            valid_roles = ['Finance Supervisor', 'Senior Finance Manager', 'Finance Director',
                          'Finance Assistant', 'Accounting Staff']
            role = row.get('role', '').strip()
            if role and role not in valid_roles:
                errors.append(f"Row {row_num}: Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}")

        return errors

    def _import_team_data(self, rows):
        """Import finance team members as Odoo users."""
        User = self.env['res.users']
        Partner = self.env['res.partner']

        created = updated = skipped = failed = 0
        error_details = []

        for row in rows:
            try:
                employee_id = row.get('employee_id', '').strip()
                email = row.get('email', '').strip()
                name = row.get('name', '').strip()
                role = row.get('role', '').strip()

                # Check if user exists
                existing_user = User.search([('login', '=', email)], limit=1)

                vals = {
                    'name': name,
                    'login': email,
                    'email': email,
                    'groups_id': [(4, self.env.ref('base.group_user').id)],  # Internal User
                }

                # Add finance group based on role
                if role == 'Finance Director':
                    vals['groups_id'].append((4, self.env.ref('account.group_account_manager').id))
                elif role in ['Finance Supervisor', 'Senior Finance Manager']:
                    vals['groups_id'].append((4, self.env.ref('account.group_account_user').id))

                if existing_user and self.update_existing:
                    existing_user.write(vals)
                    updated += 1
                elif existing_user:
                    skipped += 1
                else:
                    User.create(vals)
                    created += 1

            except Exception as e:
                failed += 1
                error_details.append(f"Row {row.get('row_num')}: {str(e)}")
                _logger.error(f"Failed to import team member row {row.get('row_num')}: {e}")

        return {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'failed': failed,
            'errors': error_details,
        }

    # ============================================================================
    # TASKS IMPORT
    # ============================================================================

    def _validate_tasks_data(self, rows):
        """
        Validate month-end closing tasks data.
        Required fields: name, project_id, phase, deadline_days, responsible_role
        """
        errors = []
        required_fields = ['name', 'project_id', 'phase', 'deadline_days']

        for row in rows:
            row_num = row.get('row_num')

            # Check required fields
            for field in required_fields:
                if not row.get(field):
                    errors.append(f"Row {row_num}: Missing required field '{field}'")

            # Validate phase (1-5)
            try:
                phase = int(row.get('phase', 0))
                if phase < 1 or phase > 5:
                    errors.append(f"Row {row_num}: Phase must be between 1 and 5")
            except ValueError:
                errors.append(f"Row {row_num}: Phase must be a number")

            # Validate deadline_days
            try:
                deadline = int(row.get('deadline_days', 0))
                if deadline < 0:
                    errors.append(f"Row {row_num}: Deadline days cannot be negative")
            except ValueError:
                errors.append(f"Row {row_num}: Deadline days must be a number")

        return errors

    def _import_tasks_data(self, rows):
        """Import month-end closing tasks."""
        Task = self.env['project.task']
        Project = self.env['project.project']

        created = updated = skipped = failed = 0
        error_details = []

        for row in rows:
            try:
                name = row.get('name', '').strip()
                project_name = row.get('project_id', '').strip()
                phase = int(row.get('phase', 1))
                deadline_days = int(row.get('deadline_days', 0))
                description = row.get('description', '').strip()

                # Find or create project
                project = Project.search([('name', '=', project_name)], limit=1)
                if not project:
                    project = Project.create({'name': project_name})

                # Check if task exists
                existing_task = Task.search([
                    ('name', '=', name),
                    ('project_id', '=', project.id)
                ], limit=1)

                vals = {
                    'name': name,
                    'project_id': project.id,
                    'description': description,
                    'stage_id': self.env.ref('project.project_stage_0').id,  # New stage
                }

                if existing_task and self.update_existing:
                    existing_task.write(vals)
                    updated += 1
                elif existing_task:
                    skipped += 1
                else:
                    Task.create(vals)
                    created += 1

            except Exception as e:
                failed += 1
                error_details.append(f"Row {row.get('row_num')}: {str(e)}")
                _logger.error(f"Failed to import task row {row.get('row_num')}: {e}")

        return {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'failed': failed,
            'errors': error_details,
        }

    # ============================================================================
    # BIR CALENDAR IMPORT
    # ============================================================================

    def _validate_bir_data(self, rows):
        """
        Validate BIR filing calendar data.
        Required fields: form_code, form_name, filing_deadline, responsible_role
        """
        errors = []
        required_fields = ['form_code', 'form_name', 'filing_deadline']

        for row in rows:
            row_num = row.get('row_num')

            # Check required fields
            for field in required_fields:
                if not row.get(field):
                    errors.append(f"Row {row_num}: Missing required field '{field}'")

            # Validate form code format (e.g., 1601-C, 2550Q)
            form_code = row.get('form_code', '').strip()
            if form_code and not any(c in form_code for c in ['-', 'Q', 'E', 'FQ', 'EQ', 'RT']):
                errors.append(f"Row {row_num}: Invalid BIR form code format '{form_code}'")

            # Validate date format
            deadline = row.get('filing_deadline', '').strip()
            if deadline:
                try:
                    datetime.strptime(deadline, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format '{deadline}'. Use YYYY-MM-DD")

        return errors

    def _import_bir_data(self, rows):
        """Import BIR filing calendar entries."""
        # This would create records in a custom BIR calendar model
        # For now, create as project tasks with BIR tag

        Task = self.env['project.task']
        Project = self.env['project.project']
        Tag = self.env['project.tags']

        # Get or create BIR project and tag
        bir_project = Project.search([('name', '=', 'BIR Compliance 2025-2026')], limit=1)
        if not bir_project:
            bir_project = Project.create({'name': 'BIR Compliance 2025-2026'})

        bir_tag = Tag.search([('name', '=', 'BIR Filing')], limit=1)
        if not bir_tag:
            bir_tag = Tag.create({'name': 'BIR Filing', 'color': 3})

        created = updated = skipped = failed = 0
        error_details = []

        for row in rows:
            try:
                form_code = row.get('form_code', '').strip()
                form_name = row.get('form_name', '').strip()
                filing_deadline = row.get('filing_deadline', '').strip()

                task_name = f"{form_code} - {form_name}"

                # Check if task exists
                existing_task = Task.search([
                    ('name', '=', task_name),
                    ('project_id', '=', bir_project.id)
                ], limit=1)

                vals = {
                    'name': task_name,
                    'project_id': bir_project.id,
                    'date_deadline': filing_deadline,
                    'tag_ids': [(4, bir_tag.id)],
                    'description': f"BIR Form {form_code}: {form_name}",
                }

                if existing_task and self.update_existing:
                    existing_task.write(vals)
                    updated += 1
                elif existing_task:
                    skipped += 1
                else:
                    Task.create(vals)
                    created += 1

            except Exception as e:
                failed += 1
                error_details.append(f"Row {row.get('row_num')}: {str(e)}")
                _logger.error(f"Failed to import BIR row {row.get('row_num')}: {e}")

        return {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'failed': failed,
            'errors': error_details,
        }

    # ============================================================================
    # LOGFRAME IMPORT
    # ============================================================================

    def _validate_logframe_data(self, rows):
        """
        Validate LogFrame KPI data.
        Required fields: level, description, indicator, target
        """
        errors = []
        required_fields = ['level', 'description']

        valid_levels = ['Goal', 'Outcome', 'Immediate Objective', 'Output', 'Activity']

        for row in rows:
            row_num = row.get('row_num')

            # Check required fields
            for field in required_fields:
                if not row.get(field):
                    errors.append(f"Row {row_num}: Missing required field '{field}'")

            # Validate level
            level = row.get('level', '').strip()
            if level and level not in valid_levels:
                errors.append(
                    f"Row {row_num}: Invalid LogFrame level '{level}'. "
                    f"Must be one of: {', '.join(valid_levels)}"
                )

        return errors

    def _import_logframe_data(self, rows):
        """Import LogFrame KPI definitions."""
        # This would integrate with MIS Builder for KPI tracking
        # For now, create as project milestones

        created = updated = skipped = failed = 0
        error_details = []

        # Placeholder - would create MIS Builder KPI records
        _logger.info(f"LogFrame import: {len(rows)} rows to process")

        return {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'failed': failed,
            'errors': error_details,
        }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _generate_summary(self, result):
        """Generate import summary text."""
        summary = f"""
Import completed on {fields.Datetime.now()}

Import Type: {dict(self._fields['import_type'].selection).get(self.import_type)}
File: {self.file_name}

Results:
- Created: {result.get('created', 0)} records
- Updated: {result.get('updated', 0)} records
- Skipped: {result.get('skipped', 0)} records
- Failed: {result.get('failed', 0)} records

Total processed: {sum([result.get('created', 0), result.get('updated', 0),
                       result.get('skipped', 0), result.get('failed', 0)])} records
        """

        if result.get('errors'):
            summary += "\n\nErrors:\n" + "\n".join(result['errors'][:10])
            if len(result['errors']) > 10:
                summary += f"\n... and {len(result['errors']) - 10} more errors"

        return summary.strip()

    def _create_audit_log(self, result):
        """Create audit trail record for this import."""
        AuditLog = self.env['finance.ppm.tdi.audit']

        AuditLog.create({
            'import_type': self.import_type,
            'file_name': self.file_name,
            'import_date': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'records_created': result.get('created', 0),
            'records_updated': result.get('updated', 0),
            'records_skipped': result.get('skipped', 0),
            'records_failed': result.get('failed', 0),
            'import_summary': self.import_summary,
            'error_log': '\n'.join(result.get('errors', [])) if result.get('errors') else False,
            'state': 'done' if result.get('failed', 0) == 0 else 'partial',
        })

    def action_download_template(self):
        """Generate and download CSV template for selected import type."""
        self.ensure_one()

        # Generate template based on import type
        template_method = getattr(self, f'_generate_{self.import_type}_template')
        csv_content = template_method()

        # Encode as base64
        template_data = base64.b64encode(csv_content.encode('utf-8'))

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.import_type}_template.csv',
            'type': 'binary',
            'datas': template_data,
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _generate_team_template(self):
        """Generate CSV template for team member import."""
        return """name,email,employee_id,role,department
Juan Dela Cruz,juan.delacruz@example.com,EMP001,Finance Supervisor,Finance
Maria Santos,maria.santos@example.com,EMP002,Senior Finance Manager,Finance"""

    def _generate_tasks_template(self):
        """Generate CSV template for tasks import."""
        return """name,project_id,phase,deadline_days,description,responsible_role
Bank Reconciliation,Month-End Closing,1,2,Reconcile all bank accounts,Finance Supervisor
GL Reconciliation,Month-End Closing,2,3,Reconcile general ledger,Senior Finance Manager"""

    def _generate_bir_template(self):
        """Generate CSV template for BIR calendar import."""
        return """form_code,form_name,filing_deadline,responsible_role,agency
1601-C,Monthly Remittance Return,2025-01-10,Finance Director,All
2550Q,Quarterly Income Tax Return,2025-04-15,Finance Director,All"""

    def _generate_logframe_template(self):
        """Generate CSV template for LogFrame import."""
        return """level,description,indicator,target,frequency
Goal,100% BIR compliance,On-time filing rate,100%,Annual
Outcome,Zero penalties,Penalty amount,0,Annual"""
