from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# --- FINANCE TEAM DIRECTORY ---
class FinanceTeam(models.Model):
    _name = 'finance.team'
    _description = 'Finance Team Directory'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, help="e.g., CKVC, RIM")
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')

    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.code}] {rec.name}"
            result.append((rec.id, name))
        return result

# --- FINANCE TASK / LOGFRAME ---
class FinancePPMTask(models.Model):
    _name = 'finance.ppm.task'
    _description = 'Finance LogFrame & Closing Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'date_deadline, sequence, id'  # Updated sort order to prioritize dates

    # --- Identification ---
    name = fields.Char(string='Task Name', required=True, tracking=True)
    complete_name = fields.Char(string='Full Path', compute='_compute_complete_name', store=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # --- Hierarchy ---
    parent_id = fields.Many2one('finance.ppm.task', string='Parent Phase', index=True, ondelete='cascade')
    child_ids = fields.One2many('finance.ppm.task', 'parent_id', string='Sub-Items')
    parent_path = fields.Char(index=True)

    # --- Details ---
    description = fields.Html(string="Description / Instructions")
    logframe_level = fields.Selection([('phase', 'Phase'), ('task', 'Task')], default='task')

    # --- ROLES ---
    role_id = fields.Many2one('finance.team', string='Preparer', tracking=True)
    reviewer_id = fields.Many2one('finance.team', string='Reviewer', tracking=True)
    approver_id = fields.Many2one('finance.team', string='Approver', tracking=True)

    # --- DATES ---
    # New Field: Specific Calendar Deadline (for Tax Calendar)
    date_deadline = fields.Date(string='Deadline Date', tracking=True)
    # Existing Field: Relative Deadline (for recurring Month-end)
    deadline_offset = fields.Integer(string='Deadline (Day +/-)', help="Days relative to Month-End")

    # --- Workflow ---
    state = fields.Selection([
        ('draft', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'For Review'),
        ('approval', 'For Approval'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, group_expand='_expand_states')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = '%s / %s' % (record.parent_id.complete_name, record.name)
            else:
                record.complete_name = record.name

    @api.constrains('parent_id')
    def _check_hierarchy_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive WBS tasks.'))

    # --- Action Buttons ---
    def action_start_task(self):
        self.state = 'in_progress'

    def action_review_task(self):
        self.state = 'review'

    def action_approve_task(self):
        self.state = 'approval'

    def action_complete_task(self):
        self.state = 'done'

    def action_reset_draft(self):
        self.state = 'draft'

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
