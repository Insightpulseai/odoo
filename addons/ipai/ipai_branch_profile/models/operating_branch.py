# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class OperatingBranch(models.Model):
    _name = 'operating.branch'
    _description = 'Operating Branch'
    _rec_name = 'name'
    _order = 'is_head_office desc, code'

    # --- Default methods ---

    # --- Field declarations ---
    name = fields.Char(
        string='Branch Name',
        required=True,
        help='Display name of the operating branch (e.g. "Pasig Head Office").',
    )
    code = fields.Char(
        string='Branch Code',
        required=True,
        help='Internal short code (e.g. "PASIG-HO").',
    )
    tin = fields.Char(
        string='TIN',
        required=True,
        help='Taxpayer Identification Number without branch code (e.g. "215-308-716").',
    )
    branch_code = fields.Char(
        string='BIR Branch Code',
        required=True,
        help='BIR-assigned branch code suffix (e.g. "00000" for head office).',
    )
    full_tin_branch = fields.Char(
        string='Full TIN-Branch',
        compute='_compute_full_tin_branch',
        store=True,
        help='Computed: TIN + branch code (e.g. "215-308-716-00000").',
    )
    rdo_code = fields.Char(
        string='RDO Code',
        help='Revenue District Office code (e.g. "044").',
    )
    rdo_name = fields.Char(
        string='RDO Name',
        help='Full name of the Revenue District Office.',
    )
    registered_address = fields.Text(
        string='Registered Address',
        required=True,
        help='Address as registered on the BIR Certificate of Registration.',
    )
    trade_name = fields.Char(
        string='Trade Name',
        help='Doing-business-as name (e.g. "TBWA\\SMP").',
    )
    line_of_business = fields.Char(
        string='Line of Business',
        help='Primary line of business registered with BIR.',
    )
    bir_registered_name = fields.Char(
        string='BIR Registered Name',
        help='Official registered name on the Certificate of Registration.',
    )
    is_head_office = fields.Boolean(
        string='Head Office',
        default=False,
        help='Mark as the head office branch (branch code 00000).',
    )
    cor_issue_date = fields.Date(
        string='COR Issue Date',
        help='Date the Certificate of Registration (BIR Form 2303) was issued.',
    )
    cor_ocn = fields.Char(
        string='COR OCN',
        help='OCN (Original Control Number) from the Certificate of Registration.',
    )
    bir_form_2303_attachment_id = fields.Many2one(
        'ir.attachment',
        string='BIR Form 2303',
        help='Scanned copy of BIR Form 2303 (Certificate of Registration).',
    )
    registration_seal_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Registration Seal',
        help='Scanned copy of the BIR registration seal / Ask for Receipt sticker.',
    )
    vat_registered = fields.Boolean(
        string='VAT Registered',
        default=True,
        help='Whether this branch is VAT-registered.',
    )
    active_for_invoicing = fields.Boolean(
        string='Active for Invoicing',
        default=True,
        help='Branch can issue sales invoices.',
    )
    active_for_expenses = fields.Boolean(
        string='Active for Expenses',
        default=True,
        help='Branch can book vendor expenses.',
    )
    active_for_withholding = fields.Boolean(
        string='Active for Withholding',
        default=True,
        help='Branch can withhold and remit taxes.',
    )
    active_for_vat = fields.Boolean(
        string='Active for VAT',
        default=True,
        help='Branch is active for VAT filing.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # --- SQL constraints ---
    _sql_constraints = [
        (
            'code_company_uniq',
            'unique(code, company_id)',
            'Branch code must be unique per company.',
        ),
        (
            'branch_code_company_uniq',
            'unique(branch_code, company_id)',
            'BIR branch code must be unique per company.',
        ),
    ]

    # --- Compute methods ---

    @api.depends('tin', 'branch_code')
    def _compute_full_tin_branch(self):
        for rec in self:
            if rec.tin and rec.branch_code:
                rec.full_tin_branch = '%s-%s' % (rec.tin, rec.branch_code)
            else:
                rec.full_tin_branch = False

    # --- Display methods ---

    def name_get(self):
        result = []
        for rec in self:
            display = '[%s] %s' % (rec.code, rec.name)
            if rec.full_tin_branch:
                display = '%s (%s)' % (display, rec.full_tin_branch)
            result.append((rec.id, display))
        return result
