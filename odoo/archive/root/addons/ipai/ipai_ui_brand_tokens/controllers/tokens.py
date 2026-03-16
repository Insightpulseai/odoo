# -*- coding: utf-8 -*-
"""
Brand Tokens JSON API Controller
================================

Exposes brand tokens as JSON for consumption by external apps (React, etc.)

Endpoints:
- GET /ipai/ui/tokens.json        - Current company tokens
- GET /ipai/ui/tokens.json?company_id=X  - Specific company tokens
"""
import json
from odoo import http
from odoo.http import request, Response


class BrandTokensController(http.Controller):

    @http.route(
        "/ipai/ui/tokens.json",
        type="http",
        auth="public",
        methods=["GET"],
        cors="*",
    )
    def get_tokens_json(self, company_id=None, **kwargs):
        """
        Return brand tokens as JSON.

        Query params:
            company_id (int): Optional company ID. Defaults to current company
                              or first company if no session.

        Returns:
            JSON response with brand tokens in canonical format.

        CORS: Enabled for cross-origin React app consumption.
        """
        try:
            # Determine company
            if company_id:
                company = request.env["res.company"].sudo().browse(int(company_id))
                if not company.exists():
                    return Response(
                        json.dumps({"error": "Company not found"}),
                        status=404,
                        content_type="application/json",
                    )
            else:
                # Use current company from session, or first company
                if request.env.company:
                    company = request.env.company.sudo()
                else:
                    company = request.env["res.company"].sudo().search([], limit=1)

            if not company:
                return Response(
                    json.dumps({"error": "No company configured"}),
                    status=404,
                    content_type="application/json",
                )

            # Get tokens
            tokens = company.get_brand_tokens_dict()

            # Return JSON with CORS headers
            response = Response(
                json.dumps(tokens, indent=2),
                status=200,
                content_type="application/json",
            )
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Cache-Control"] = "public, max-age=300"  # 5 min cache

            return response

        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                content_type="application/json",
            )

    @http.route(
        "/ipai/ui/tokens.css",
        type="http",
        auth="public",
        methods=["GET"],
    )
    def get_tokens_css(self, company_id=None, **kwargs):
        """
        Return brand tokens as CSS custom properties.

        Useful for direct injection or dynamic loading.
        """
        try:
            # Determine company
            if company_id:
                company = request.env["res.company"].sudo().browse(int(company_id))
            else:
                if request.env.company:
                    company = request.env.company.sudo()
                else:
                    company = request.env["res.company"].sudo().search([], limit=1)

            if not company:
                return Response(
                    "/* No company configured */",
                    status=404,
                    content_type="text/css",
                )

            css_vars = company.get_brand_tokens_css_vars()
            css_content = f""":root {{
  /* IPAI Brand Tokens (from company: {company.name}) */
  {css_vars}
}}
"""
            response = Response(
                css_content,
                status=200,
                content_type="text/css",
            )
            response.headers["Cache-Control"] = "public, max-age=300"
            return response

        except Exception as e:
            return Response(
                f"/* Error: {e} */",
                status=500,
                content_type="text/css",
            )
