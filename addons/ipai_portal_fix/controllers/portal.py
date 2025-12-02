# -*- coding: utf-8 -*-
"""
Portal Controller Fix for Website-Free Instances
Ensures 'website' context is always available to prevent KeyError.
"""

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

from odoo import http


class CustomerPortalWebsiteSafe(CustomerPortal):
    """
    Inherited CustomerPortal controller that ensures 'website' context
    is always present, even when Website module is not installed.
    """

    def _prepare_portal_layout_values(self):
        """
        Override to inject 'website' context if missing.

        This prevents KeyError: 'website' in portal templates that
        expect the website variable to exist.
        """
        values = super()._prepare_portal_layout_values()

        # Check if 'website' is missing and Website module is installed
        if "website" not in values:
            # Try to get current website if Website module is installed
            website_module = (
                request.env["ir.module.module"]
                .sudo()
                .search(
                    [("name", "=", "website"), ("state", "=", "installed")], limit=1
                )
            )

            if website_module:
                # Website module installed - get current website
                try:
                    current_website = request.env["website"].get_current_website()
                    values["website"] = current_website
                except Exception:
                    # Fallback: set to False to prevent KeyError
                    values["website"] = False
            else:
                # Website module not installed - set to False
                values["website"] = False

        return values

    def _prepare_home_portal_values(self, counters):
        """
        Override to inject 'website' context for home portal.
        """
        values = super()._prepare_home_portal_values(counters)

        # Ensure 'website' is present
        if "website" not in values:
            values["website"] = False

        return values
