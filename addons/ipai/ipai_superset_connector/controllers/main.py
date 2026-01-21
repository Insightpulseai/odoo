# -*- coding: utf-8 -*-
"""
Superset Embed Controller.

Provides endpoints for:
- Guest token issuance (authenticated Odoo users)
- Dashboard listing (based on user permissions)
"""
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError

from ..services.superset_client import (
    get_superset_client_from_params,
    SupersetClientError,
)

_logger = logging.getLogger(__name__)


class SupersetEmbedController(http.Controller):
    """Controller for Superset dashboard embedding."""

    @http.route(
        "/ipai/superset/guest_token/<int:dashboard_id>",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def get_guest_token(self, dashboard_id, **kwargs):
        """
        Get a Superset guest token for embedding a dashboard.

        Args:
            dashboard_id: Superset dashboard ID

        Returns:
            JSON dict with:
            - token: Guest token string
            - superset_url: Base URL for embedding
            - dashboard_id: Echoed dashboard ID

        Raises:
            AccessDenied: If user lacks permission for dashboard
            UserError: If Superset API fails
        """
        env = request.env
        user = env.user

        # Verify user has access to this dashboard
        Dashboard = env["ipai.superset.dashboard"].sudo()
        dashboard = Dashboard.search(
            [
                ("superset_dashboard_id", "=", str(dashboard_id)),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not dashboard:
            raise AccessDenied(f"Dashboard {dashboard_id} not found or inactive")

        # Check group-based access
        if dashboard.allowed_group_ids:
            user_groups = user.groups_id
            allowed = any(g in user_groups for g in dashboard.allowed_group_ids)
            if not allowed:
                _logger.warning(
                    "User %s denied access to dashboard %s",
                    user.login,
                    dashboard_id,
                )
                raise AccessDenied("You do not have permission to view this dashboard")

        # Build user info for guest token
        user_info = {
            "username": f"odoo_{user.id}",
            "first_name": user.name or "Odoo",
            "last_name": "User",
        }

        # Build RLS rules based on dashboard config
        rls_rules = self._build_rls_rules(dashboard, user)

        try:
            client = get_superset_client_from_params(env)
            token = client.get_guest_token(
                dashboard_id=str(dashboard_id),
                user_info=user_info,
                rls_rules=rls_rules,
            )

            # Log audit entry
            self._log_audit(dashboard, user, rls_rules)

            # Get Superset base URL
            ICP = env["ir.config_parameter"].sudo()
            superset_url = ICP.get_param("ipai_superset.base_url", "")

            return {
                "token": token,
                "superset_url": superset_url,
                "dashboard_id": dashboard_id,
            }

        except SupersetClientError as e:
            _logger.error("Guest token request failed: %s", e)
            raise UserError(f"Failed to get dashboard token: {e}") from e

    def _build_rls_rules(self, dashboard, user):
        """
        Build RLS rules based on dashboard configuration and user context.

        Args:
            dashboard: ipai.superset.dashboard record
            user: res.users record

        Returns:
            List of RLS rule dicts [{"clause": "..."}]
        """
        rls_rules = []

        # Company-based RLS
        if dashboard.rls_by_company and user.company_id:
            rls_rules.append({"clause": f"company_id = {user.company_id.id}"})

        # User-based RLS
        if dashboard.rls_by_user:
            rls_rules.append({"clause": f"user_id = {user.id}"})

        # Custom RLS clause from dashboard config
        if dashboard.rls_custom_clause:
            # Substitute placeholders
            clause = dashboard.rls_custom_clause
            clause = clause.replace("${company_id}", str(user.company_id.id or 0))
            clause = clause.replace("${user_id}", str(user.id))
            clause = clause.replace("${user_login}", user.login or "")
            rls_rules.append({"clause": clause})

        return rls_rules

    def _log_audit(self, dashboard, user, rls_rules):
        """Create audit log entry for token issuance."""
        try:
            request.env["ipai.superset.audit"].sudo().create(
                {
                    "dashboard_id": dashboard.id,
                    "user_id": user.id,
                    "company_id": user.company_id.id if user.company_id else False,
                    "rls_summary": str(rls_rules) if rls_rules else "None",
                }
            )
        except Exception as e:
            # Don't fail token issuance on audit error
            _logger.warning("Failed to create audit log: %s", e)

    @http.route(
        "/ipai/superset/dashboards",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def list_dashboards(self, **kwargs):
        """
        List dashboards accessible to the current user.

        Returns:
            List of dashboard dicts with id, name, description
        """
        env = request.env
        user = env.user

        Dashboard = env["ipai.superset.dashboard"].sudo()
        dashboards = Dashboard.search([("active", "=", True)])

        result = []
        for dash in dashboards:
            # Check group access
            if dash.allowed_group_ids:
                user_groups = user.groups_id
                if not any(g in user_groups for g in dash.allowed_group_ids):
                    continue

            result.append(
                {
                    "id": dash.superset_dashboard_id,
                    "name": dash.name,
                    "description": dash.description or "",
                    "odoo_record_id": dash.id,
                }
            )

        return result

    @http.route(
        "/ipai/superset/health",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def health_check(self, **kwargs):
        """
        Check Superset API connectivity.

        Returns:
            Dict with status and version info
        """
        try:
            client = get_superset_client_from_params(request.env)
            version_info = client.health_check()
            return {
                "status": "ok",
                "superset_version": version_info,
            }
        except SupersetClientError as e:
            return {
                "status": "error",
                "error": str(e),
            }
