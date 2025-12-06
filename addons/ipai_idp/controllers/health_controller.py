# -*- coding: utf-8 -*-
"""
IDP Health Check Controller.

Provides HTTP endpoints for health, liveness, and readiness checks.
"""
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IdpHealthController(http.Controller):
    """
    IDP Health Check HTTP Controller.

    Endpoints:
        /ipai/idp/livez - Liveness probe
        /ipai/idp/readyz - Readiness probe
        /ipai/idp/healthz - Deep health check
        /ipai/idp/metrics - Processing metrics
    """

    @http.route("/ipai/idp/livez", type="http", auth="none", csrf=False)
    def livez(self):
        """
        Liveness probe endpoint.

        Returns 200 if the process is alive.
        Used by Kubernetes livenessProbe.
        Very lightweight - never blocks on network.

        Returns:
            HTTP Response with JSON body
        """
        try:
            result = request.env["idp.service.health"].sudo().check_liveness()
            return request.make_response(
                json.dumps(result),
                headers=[
                    ("Content-Type", "application/json"),
                ],
            )
        except Exception as e:
            _logger.exception("Liveness check failed")
            return request.make_response(
                json.dumps({"status": "error", "error": str(e)}),
                headers=[("Content-Type", "application/json")],
                status=500,
            )

    @http.route("/ipai/idp/readyz", type="http", auth="none", csrf=False)
    def readyz(self):
        """
        Readiness probe endpoint.

        Returns 200 if the service can accept traffic.
        Returns 503 if not ready.
        Used by Kubernetes readinessProbe.

        Returns:
            HTTP Response with JSON body
        """
        try:
            result = request.env["idp.service.health"].sudo().check_readiness()
            status_code = 200 if result.get("status") == "ready" else 503

            return request.make_response(
                json.dumps(result),
                headers=[("Content-Type", "application/json")],
                status=status_code,
            )
        except Exception as e:
            _logger.exception("Readiness check failed")
            return request.make_response(
                json.dumps({"status": "not_ready", "error": str(e)}),
                headers=[("Content-Type", "application/json")],
                status=503,
            )

    @http.route("/ipai/idp/healthz", type="http", auth="none", csrf=False)
    def healthz(self):
        """
        Deep health check endpoint.

        Returns detailed status of all dependencies.
        Used by monitoring systems.

        Returns:
            HTTP Response with JSON body
        """
        try:
            result = request.env["idp.service.health"].sudo().check_health()

            if result.get("status") == "ok":
                status_code = 200
            elif result.get("status") == "degraded":
                status_code = 200  # Still operational
            else:
                status_code = 503

            return request.make_response(
                json.dumps(result),
                headers=[("Content-Type", "application/json")],
                status=status_code,
            )
        except Exception as e:
            _logger.exception("Health check failed")
            return request.make_response(
                json.dumps({"status": "unhealthy", "error": str(e)}),
                headers=[("Content-Type", "application/json")],
                status=503,
            )

    @http.route("/ipai/idp/metrics", type="json", auth="user")
    def metrics(self):
        """
        Get IDP processing metrics.

        Requires authentication.
        Returns processing statistics for dashboards.

        Returns:
            dict: Metrics data
        """
        try:
            return request.env["idp.service.health"].sudo().get_metrics()
        except Exception as e:
            _logger.exception("Metrics endpoint failed")
            return {"error": str(e)}
