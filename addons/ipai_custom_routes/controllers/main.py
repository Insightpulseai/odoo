# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CustomRoutes(http.Controller):
    """
    Custom routes for clean URLs matching official Odoo behavior.
    """

    @http.route('/odoo/discuss', type='http', auth='user', website=True)
    def discuss(self):
        """Redirect to Discuss app."""
        return request.redirect('/odoo?menu_id=%s' % request.env.ref('mail.menu_root_discuss').id)

    @http.route('/odoo/calendar', type='http', auth='user', website=True)
    def calendar(self):
        """Redirect to Calendar app."""
        return request.redirect('/odoo/calendar.event')

    @http.route('/odoo/project', type='http', auth='user', website=True)
    def project(self):
        """Redirect to Project app."""
        return request.redirect('/odoo/project.project')

    @http.route('/odoo/expenses', type='http', auth='user', website=True)
    def expenses(self):
        """Redirect to Expenses app."""
        return request.redirect('/odoo/hr.expense')
