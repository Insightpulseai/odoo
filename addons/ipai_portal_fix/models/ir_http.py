# -*- coding: utf-8 -*-
"""
IR HTTP Extension for Portal Fix

This module extends the ir.http model to inject a default 'website' context
variable when rendering QWeb templates. This prevents KeyError: 'website'
errors in portal.frontend_layout and other templates that expect this variable.
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_default_website_context(cls):
        """
        Get a safe default website context value.

        Returns the current website record if available, or an empty
        recordset as a safe fallback that won't break template rendering.
        """
        if not request:
            return None

        try:
            # Check if website module is installed and accessible
            if 'website.website' in request.env.registry:
                # Try to get the current website from the request
                if hasattr(request, 'website') and request.website:
                    return request.website
                # Otherwise get the default website
                Website = request.env['website.website'].sudo()
                website = Website.get_current_website()
                if website:
                    return website
                # Fallback to first website or empty recordset
                return Website.search([], limit=1) or Website
        except Exception:
            pass

        return None

    @classmethod
    def _get_website_context_fallback(cls):
        """
        Create a minimal mock website object for templates that expect one.

        This returns a simple object with common website attributes set to
        safe default values, preventing KeyError while allowing templates
        to render.
        """
        class WebsiteFallback:
            """Minimal mock website for template context fallback."""
            id = False
            name = ''
            domain = ''
            company_id = False
            default_lang_id = False
            language_ids = []

            def __bool__(self):
                return False

            def __iter__(self):
                return iter([])

            def __len__(self):
                return 0

            @property
            def sudo(self):
                return lambda: self

            def exists(self):
                return False

        return WebsiteFallback()
