# -*- coding: utf-8 -*-
"""
Pre-built Analytics Views

Optimized SQL views for common business intelligence needs.
These views flatten Odoo's normalized structure for BI tools.
"""
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SupersetAnalyticsView(models.Model):
    _name = 'superset.analytics.view'
    _description = 'Pre-built Analytics View'
    _order = 'category, sequence, name'

    name = fields.Char(string='View Name', required=True)
    technical_name = fields.Char(string='Technical Name', required=True)
    category = fields.Selection([
        ('sales', 'Sales Analytics'),
        ('finance', 'Finance Analytics'),
        ('inventory', 'Inventory Analytics'),
        ('hr', 'HR Analytics'),
        ('project', 'Project Analytics'),
        ('bir', 'BIR Tax Compliance'),
    ], string='Category', required=True)
    
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # SQL Definition
    sql_definition = fields.Text(string='SQL Definition', required=True)
    
    # Dependencies
    required_modules = fields.Char(
        string='Required Modules',
        help='Comma-separated list of modules that must be installed',
    )
    
    # Status
    is_created = fields.Boolean(string='View Created', readonly=True)
    last_refresh = fields.Datetime(string='Last Refresh', readonly=True)

    def action_create_view(self):
        """Create the analytics view in PostgreSQL"""
        self.ensure_one()
        
        view_sql = f"""
            CREATE OR REPLACE VIEW {self.technical_name} AS
            {self.sql_definition}
        """
        
        try:
            self.env.cr.execute(view_sql)
            self.write({
                'is_created': True,
                'last_refresh': fields.Datetime.now(),
            })
            _logger.info('Created analytics view: %s', self.technical_name)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('View Created'),
                    'message': _('Analytics view "%s" created successfully') % self.name,
                    'type': 'success',
                }
            }
        except Exception as e:
            _logger.error('Failed to create analytics view %s: %s', self.technical_name, str(e))
            raise UserError(_('Failed to create view: %s') % str(e))

    def action_drop_view(self):
        """Drop the analytics view"""
        self.ensure_one()
        try:
            self.env.cr.execute(f'DROP VIEW IF EXISTS {self.technical_name} CASCADE')
            self.is_created = False
        except Exception as e:
            _logger.warning('Failed to drop view %s: %s', self.technical_name, str(e))

    @api.model
    def create_all_views(self):
        """Create all active analytics views"""
        views = self.search([('active', '=', True)])
        created = 0
        errors = []
        
        for view in views:
            try:
                view.action_create_view()
                created += 1
            except Exception as e:
                errors.append(f'{view.name}: {str(e)}')
        
        return created, errors


# ============================================================================
# PRE-DEFINED ANALYTICS VIEWS (loaded via XML data)
# ============================================================================

ANALYTICS_VIEWS = {
    # -------------------------------------------------------------------------
    # SALES ANALYTICS
    # -------------------------------------------------------------------------
    'sales_order_analysis': {
        'name': 'Sales Order Analysis',
        'category': 'sales',
        'description': 'Comprehensive sales order metrics with customer and product dimensions',
        'sql': """
SELECT
    so.id AS order_id,
    so.name AS order_ref,
    so.date_order,
    so.state AS order_state,
    so.amount_total,
    so.amount_untaxed,
    so.amount_tax,
    so.currency_id,
    rc.name AS currency,
    
    -- Customer Dimensions
    so.partner_id AS customer_id,
    rp.name AS customer_name,
    rp.city AS customer_city,
    rp.country_id,
    rpc.name AS customer_country,
    
    -- Product Line Details (aggregated)
    COUNT(sol.id) AS line_count,
    SUM(sol.product_uom_qty) AS total_qty,
    
    -- Time Dimensions
    DATE_TRUNC('month', so.date_order) AS order_month,
    DATE_TRUNC('quarter', so.date_order) AS order_quarter,
    DATE_TRUNC('year', so.date_order) AS order_year,
    EXTRACT(DOW FROM so.date_order) AS day_of_week,
    
    -- Company
    so.company_id,
    rcomp.name AS company_name,
    
    -- Audit
    so.create_date,
    so.write_date

FROM sale_order so
LEFT JOIN res_partner rp ON so.partner_id = rp.id
LEFT JOIN res_country rpc ON rp.country_id = rpc.id
LEFT JOIN res_currency rc ON so.currency_id = rc.id
LEFT JOIN res_company rcomp ON so.company_id = rcomp.id
LEFT JOIN sale_order_line sol ON sol.order_id = so.id

WHERE so.state NOT IN ('draft', 'cancel')

GROUP BY 
    so.id, so.name, so.date_order, so.state,
    so.amount_total, so.amount_untaxed, so.amount_tax,
    so.currency_id, rc.name,
    so.partner_id, rp.name, rp.city, rp.country_id, rpc.name,
    so.company_id, rcomp.name,
    so.create_date, so.write_date
"""
    },
    
    # -------------------------------------------------------------------------
    # FINANCE ANALYTICS
    # -------------------------------------------------------------------------
    'account_move_analysis': {
        'name': 'Journal Entry Analysis',
        'category': 'finance',
        'description': 'Account moves (invoices, bills, journal entries) with GL dimensions',
        'sql': """
SELECT
    am.id AS move_id,
    am.name AS move_ref,
    am.date AS accounting_date,
    am.invoice_date,
    am.move_type,
    am.state,
    am.payment_state,
    
    -- Amounts
    am.amount_total,
    am.amount_untaxed,
    am.amount_tax,
    am.amount_residual,
    am.currency_id,
    rc.name AS currency,
    
    -- Partner (Customer/Vendor)
    am.partner_id,
    rp.name AS partner_name,
    CASE 
        WHEN am.move_type IN ('out_invoice', 'out_refund', 'out_receipt') THEN 'Customer'
        WHEN am.move_type IN ('in_invoice', 'in_refund', 'in_receipt') THEN 'Vendor'
        ELSE 'Other'
    END AS partner_type,
    
    -- Journal
    am.journal_id,
    aj.name AS journal_name,
    aj.type AS journal_type,
    
    -- Time Dimensions
    DATE_TRUNC('month', am.date) AS accounting_month,
    DATE_TRUNC('quarter', am.date) AS accounting_quarter,
    DATE_TRUNC('year', am.date) AS fiscal_year,
    
    -- Company
    am.company_id,
    rcomp.name AS company_name,
    
    -- Audit
    am.create_date,
    am.write_date

FROM account_move am
LEFT JOIN res_partner rp ON am.partner_id = rp.id
LEFT JOIN res_currency rc ON am.currency_id = rc.id
LEFT JOIN account_journal aj ON am.journal_id = aj.id
LEFT JOIN res_company rcomp ON am.company_id = rcomp.id

WHERE am.state = 'posted'
"""
    },
    
    'account_move_line_analysis': {
        'name': 'GL Line Item Analysis',
        'category': 'finance',
        'description': 'Detailed general ledger line items with full account dimensions',
        'sql': """
SELECT
    aml.id AS line_id,
    aml.name AS description,
    aml.date,
    aml.debit,
    aml.credit,
    aml.balance,
    aml.amount_currency,
    aml.quantity,
    
    -- Account
    aml.account_id,
    aa.code AS account_code,
    aa.name AS account_name,
    aat.name AS account_type,
    
    -- Partner
    aml.partner_id,
    rp.name AS partner_name,
    
    -- Journal Entry
    aml.move_id,
    am.name AS move_ref,
    am.move_type,
    
    -- Journal
    aml.journal_id,
    aj.name AS journal_name,
    
    -- Analytic
    aml.analytic_distribution,
    
    -- Time Dimensions
    DATE_TRUNC('month', aml.date) AS accounting_month,
    DATE_TRUNC('quarter', aml.date) AS accounting_quarter,
    DATE_TRUNC('year', aml.date) AS fiscal_year,
    
    -- Company
    aml.company_id,
    rcomp.name AS company_name

FROM account_move_line aml
LEFT JOIN account_account aa ON aml.account_id = aa.id
LEFT JOIN account_account_type aat ON aa.account_type = aat.id
LEFT JOIN res_partner rp ON aml.partner_id = rp.id
LEFT JOIN account_move am ON aml.move_id = am.id
LEFT JOIN account_journal aj ON aml.journal_id = aj.id
LEFT JOIN res_company rcomp ON aml.company_id = rcomp.id

WHERE am.state = 'posted'
"""
    },
    
    'trial_balance_view': {
        'name': 'Trial Balance',
        'category': 'finance',
        'description': 'Account balances aggregated by account for trial balance reporting',
        'sql': """
SELECT
    aa.id AS account_id,
    aa.code AS account_code,
    aa.name AS account_name,
    aa.account_type,
    
    -- Balances
    SUM(aml.debit) AS total_debit,
    SUM(aml.credit) AS total_credit,
    SUM(aml.balance) AS balance,
    
    -- Period
    DATE_TRUNC('month', aml.date) AS period_month,
    
    -- Company
    aa.company_id,
    rcomp.name AS company_name

FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
JOIN account_move am ON aml.move_id = am.id
JOIN res_company rcomp ON aa.company_id = rcomp.id

WHERE am.state = 'posted'

GROUP BY 
    aa.id, aa.code, aa.name, aa.account_type,
    DATE_TRUNC('month', aml.date),
    aa.company_id, rcomp.name
"""
    },
    
    # -------------------------------------------------------------------------
    # BIR TAX COMPLIANCE
    # -------------------------------------------------------------------------
    'bir_ewt_analysis': {
        'name': 'BIR EWT Analysis (1601-EQ)',
        'category': 'bir',
        'description': 'Expanded Withholding Tax analysis for BIR 1601-EQ compliance',
        'sql': """
SELECT
    am.id AS move_id,
    am.name AS document_ref,
    am.date AS transaction_date,
    am.invoice_date,
    
    -- Vendor/Payee
    rp.id AS payee_id,
    rp.name AS payee_name,
    rp.vat AS payee_tin,
    
    -- Tax Details
    aml.name AS tax_description,
    aml.debit AS ewt_amount,
    aa.code AS account_code,
    
    -- Tax Type Classification
    CASE 
        WHEN aa.code LIKE '2130%' THEN 'Professional Fees'
        WHEN aa.code LIKE '2131%' THEN 'Rentals'
        WHEN aa.code LIKE '2132%' THEN 'Services'
        ELSE 'Other'
    END AS ewt_category,
    
    -- Gross Amount (base for withholding)
    ABS(aml.balance) / NULLIF(at.amount, 0) * 100 AS gross_amount,
    at.amount AS tax_rate,
    
    -- Period
    DATE_TRUNC('month', am.date) AS tax_month,
    DATE_TRUNC('quarter', am.date) AS tax_quarter,
    
    -- Company
    am.company_id

FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
JOIN account_account aa ON aml.account_id = aa.id
LEFT JOIN res_partner rp ON am.partner_id = rp.id
LEFT JOIN account_tax at ON aml.tax_line_id = at.id

WHERE am.state = 'posted'
  AND am.move_type IN ('in_invoice', 'in_refund')
  AND aa.code LIKE '213%'  -- Withholding tax accounts
"""
    },
    
    'bir_vat_analysis': {
        'name': 'BIR VAT Analysis (2550Q)',
        'category': 'bir',
        'description': 'VAT input/output analysis for BIR 2550Q quarterly filing',
        'sql': """
SELECT
    am.id AS move_id,
    am.name AS document_ref,
    am.date AS transaction_date,
    
    -- Party
    rp.name AS party_name,
    rp.vat AS party_tin,
    
    -- VAT Classification
    CASE 
        WHEN am.move_type IN ('out_invoice', 'out_refund') THEN 'Output VAT'
        WHEN am.move_type IN ('in_invoice', 'in_refund') THEN 'Input VAT'
    END AS vat_type,
    
    -- Amounts
    am.amount_untaxed AS vatable_amount,
    am.amount_tax AS vat_amount,
    am.amount_total AS total_amount,
    
    -- VAT Rate
    CASE 
        WHEN am.amount_untaxed > 0 
        THEN ROUND((am.amount_tax / am.amount_untaxed * 100)::numeric, 2)
        ELSE 0 
    END AS vat_rate,
    
    -- Period
    DATE_TRUNC('month', am.date) AS vat_month,
    DATE_TRUNC('quarter', am.date) AS vat_quarter,
    
    -- Company
    am.company_id

FROM account_move am
LEFT JOIN res_partner rp ON am.partner_id = rp.id

WHERE am.state = 'posted'
  AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
  AND am.amount_tax != 0
"""
    },
    
    # -------------------------------------------------------------------------
    # INVENTORY ANALYTICS
    # -------------------------------------------------------------------------
    'stock_valuation_analysis': {
        'name': 'Stock Valuation Analysis',
        'category': 'inventory',
        'description': 'Current stock levels with valuation by location and product',
        'sql': """
SELECT
    sq.id AS quant_id,
    sq.quantity,
    sq.reserved_quantity,
    sq.quantity - sq.reserved_quantity AS available_qty,
    
    -- Product
    sq.product_id,
    pt.name AS product_name,
    pp.default_code AS sku,
    pc.name AS product_category,
    
    -- Valuation
    COALESCE(pt.standard_price, 0) AS unit_cost,
    sq.quantity * COALESCE(pt.standard_price, 0) AS total_value,
    
    -- Location
    sq.location_id,
    sl.name AS location_name,
    sl.usage AS location_type,
    sw.name AS warehouse_name,
    
    -- Company
    sq.company_id

FROM stock_quant sq
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pt.categ_id = pc.id
JOIN stock_location sl ON sq.location_id = sl.id
LEFT JOIN stock_warehouse sw ON sl.warehouse_id = sw.id

WHERE sl.usage = 'internal'
  AND sq.quantity > 0
"""
    },
    
    # -------------------------------------------------------------------------
    # PROJECT ANALYTICS
    # -------------------------------------------------------------------------
    'project_task_analysis': {
        'name': 'Project Task Analysis',
        'category': 'project',
        'description': 'Project tasks with time tracking and status metrics',
        'sql': """
SELECT
    pt.id AS task_id,
    pt.name AS task_name,
    pt.date_deadline,
    pt.priority,
    
    -- Stage
    pts.name AS stage_name,
    pts.fold AS is_folded,
    
    -- Project
    pt.project_id,
    pp.name AS project_name,
    
    -- Assignee
    pt.user_ids,
    
    -- Time Tracking
    pt.planned_hours,
    pt.effective_hours,
    pt.remaining_hours,
    pt.progress,
    
    -- Status Derived
    CASE 
        WHEN pts.fold = true THEN 'Completed'
        WHEN pt.date_deadline < CURRENT_DATE THEN 'Overdue'
        WHEN pt.date_deadline = CURRENT_DATE THEN 'Due Today'
        ELSE 'On Track'
    END AS status,
    
    -- Company
    pt.company_id

FROM project_task pt
JOIN project_project pp ON pt.project_id = pp.id
LEFT JOIN project_task_type pts ON pt.stage_id = pts.id

WHERE pt.active = true
"""
    },
    
    # -------------------------------------------------------------------------
    # HR ANALYTICS
    # -------------------------------------------------------------------------
    'employee_analysis': {
        'name': 'Employee Analysis',
        'category': 'hr',
        'description': 'Employee demographics and organizational structure',
        'sql': """
SELECT
    he.id AS employee_id,
    he.name AS employee_name,
    he.work_email,
    he.job_title,
    
    -- Department
    hd.name AS department_name,
    
    -- Manager
    hem.name AS manager_name,
    
    -- Job
    hj.name AS job_position,
    
    -- Status
    he.active,
    
    -- Company
    he.company_id

FROM hr_employee he
LEFT JOIN hr_department hd ON he.department_id = hd.id
LEFT JOIN hr_employee hem ON he.parent_id = hem.id
LEFT JOIN hr_job hj ON he.job_id = hj.id

WHERE he.active = true
"""
    },
}
