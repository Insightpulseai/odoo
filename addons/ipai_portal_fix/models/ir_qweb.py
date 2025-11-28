# -*- coding: utf-8 -*-
"""
IR QWeb Extension for Portal Fix

This module extends the ir.qweb model to inject a default 'website' context
variable when rendering QWeb templates. This prevents KeyError: 'website'
errors in portal.frontend_layout and other templates that expect this variable.
"""

from odoo import models
from odoo.http import request


class IrQweb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _prepare_frontend_context(self, values):
        """
        Prepare the frontend context with a safe website fallback.

        Ensures the 'website' key exists in the rendering context to prevent
        KeyError exceptions in templates that expect this variable.
        """
        if values is None:
            values = {}

        # ALWAYS inject 'website' key if missing - even as False
        # This prevents KeyError when templates try to access website variable
        if 'website' not in values:
            values['website'] = self._get_safe_website()

        # Also ensure main_object has a safe fallback
        if 'main_object' not in values:
            values['main_object'] = self.env['ir.ui.view']  # Empty recordset

        # Ensure edit_in_backend has a default
        if 'edit_in_backend' not in values:
            values['edit_in_backend'] = False

        # Ensure html_data dict exists for template updates
        if 'html_data' not in values:
            values['html_data'] = {}

        return values

    def _get_safe_website(self):
        """
        Get a safe website record for the context.

        Returns:
            - The current website if available
            - The first website found
            - An empty website recordset as fallback
            - False if website module is not installed (safe for template checks)
        """
        try:
            # Check if website module is installed
            if 'website.website' not in self.env.registry:
                return False  # Safe falsy value for template checks

            Website = self.env['website.website'].sudo()

            # Try to get website from request
            if request and hasattr(request, 'website') and request.website:
                return request.website

            # Try get_current_website method
            if hasattr(Website, 'get_current_website'):
                website = Website.get_current_website()
                if website:
                    return website

            # Return first website or empty recordset
            return Website.search([], limit=1) or Website

        except Exception:
            # If anything fails, return False (safe for template checks)
            return False

    def _render(self, template, values=None, **options):
        """
        Override _render to inject website context before rendering.

        This ensures that templates like portal.frontend_layout always have
        access to the 'website' variable, preventing KeyError exceptions.
        """
        # Prepare context with website fallback
        values = self._prepare_frontend_context(values or {})

        return super()._render(template, values, **options)
