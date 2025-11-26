# -*- coding: utf-8 -*-
"""
IR HTTP Extension for Portal Fix

This module extends ir.http to ensure website context is properly available
for all HTTP requests. Works together with ir_qweb.py for comprehensive fix.
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_default_website(cls):
        """
        Get a safe default website value for the request context.

        Returns:
            - The current website if available
            - The first website found
            - False if website module not installed
        """
        if not request:
            return False

        try:
            # Check if website module is installed
            if 'website.website' not in request.env.registry:
                return False

            # Try to get the current website from the request
            if hasattr(request, 'website') and request.website:
                return request.website

            # Otherwise get the default website
            Website = request.env['website.website'].sudo()

            # Try get_current_website method
            if hasattr(Website, 'get_current_website'):
                website = Website.get_current_website()
                if website:
                    return website

            # Fallback to first website or empty recordset
            return Website.search([], limit=1) or False

        except Exception:
            return False
