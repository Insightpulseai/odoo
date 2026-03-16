# -*- coding: utf-8 -*-
import json
import logging

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class PlatformAPIController(http.Controller):
    """REST API endpoints for Next.js frontend"""

    @http.route(
        "/api/platform/features",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_features(self):
        """Return published features for landing page"""
        try:
            Feature = request.env["platform.feature"].sudo()
            features = Feature.get_published_features()
            return {"features": features}
        except Exception as e:
            _logger.error(f"Failed to fetch features: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/deployments",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_deployments(self, limit=10):
        """Return recent deployments"""
        try:
            Deployment = request.env["platform.deployment"].sudo()
            deployments = Deployment.get_recent_deployments(limit=limit)
            return {"deployments": deployments}
        except Exception as e:
            _logger.error(f"Failed to fetch deployments: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/deploy",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def trigger_deployment(
        self, branch, environment, commit_hash=None, commit_message=None
    ):
        """Trigger new deployment"""
        try:
            Deployment = request.env["platform.deployment"]

            # Create deployment record
            deployment = Deployment.create(
                {
                    "branch": branch,
                    "environment": environment,
                    "commit_hash": commit_hash,
                    "commit_message": commit_message,
                    "commit_author": request.env.user.name,
                }
            )

            # Trigger via n8n
            deployment.action_trigger_deployment()

            return {
                "deployment_id": deployment.id,
                "status": "queued",
                "message": f"Deployment {deployment.id} triggered successfully",
            }

        except Exception as e:
            _logger.error(f"Failed to trigger deployment: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/logs",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_build_logs(self, deployment_id):
        """Get build logs for a deployment"""
        try:
            Deployment = request.env["platform.deployment"].sudo()
            deployment = Deployment.browse(deployment_id)

            if not deployment.exists():
                return {"error": "Deployment not found"}

            # Parse build log into structured format
            logs = []
            if deployment.build_log:
                for line in deployment.build_log.split("\n"):
                    if not line.strip():
                        continue

                    # Simple log parsing
                    level = "info"
                    if "ERROR" in line.upper():
                        level = "error"
                    elif "WARN" in line.upper():
                        level = "warn"
                    elif "SUCCESS" in line.upper() or "DONE" in line.upper():
                        level = "success"

                    logs.append(
                        {
                            "timestamp": (
                                deployment.started_at.isoformat()
                                if deployment.started_at
                                else ""
                            ),
                            "level": level,
                            "message": line.strip(),
                        }
                    )

            return {"logs": logs}

        except Exception as e:
            _logger.error(f"Failed to fetch logs: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/metrics",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_metrics(self, environment):
        """Get platform metrics"""
        try:
            # TODO: Integrate with actual monitoring system (Prometheus, Grafana, etc.)
            # For now, return mock metrics
            metrics = {
                "cpu_usage": 24,
                "memory_usage": 1.2,
                "response_time": 142,
                "requests_per_minute": 1234,
                "error_rate": 0.01,
            }

            return metrics

        except Exception as e:
            _logger.error(f"Failed to fetch metrics: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/shell/execute",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def execute_shell_command(self, environment, command):
        """Execute command in web shell (restricted)"""
        try:
            # Security: Only allow specific safe commands
            allowed_commands = ["ls", "pwd", "whoami", "date", "uptime"]

            cmd = command.strip().split()[0]
            if cmd not in allowed_commands:
                return {
                    "error": "Command not allowed",
                    "allowed_commands": allowed_commands,
                }

            # TODO: Execute command via SSH or Docker exec
            # For now, return mock output
            return {
                "output": f"$ {command}\nMock output for: {command}",
                "exit_code": 0,
            }

        except Exception as e:
            _logger.error(f"Failed to execute command: {str(e)}")
            return {"error": str(e)}

    @http.route(
        "/api/platform/pricing",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_pricing(self):
        """Get pricing plans from product catalog"""
        try:
            # TODO: Fetch from product.template with 'platform_plan' tag
            plans = [
                {
                    "id": 1,
                    "name": "Starter",
                    "description": "Perfect for small teams",
                    "price": 29,
                    "currency": "USD",
                    "features": ["2 Projects", "5 Deployments/day", "1 GB Storage"],
                    "popular": False,
                },
                {
                    "id": 2,
                    "name": "Professional",
                    "description": "For growing businesses",
                    "price": 99,
                    "currency": "USD",
                    "features": [
                        "10 Projects",
                        "Unlimited Deployments",
                        "10 GB Storage",
                        "Priority Support",
                    ],
                    "popular": True,
                },
                {
                    "id": 3,
                    "name": "Enterprise",
                    "description": "For large organizations",
                    "price": 299,
                    "currency": "USD",
                    "features": [
                        "Unlimited Projects",
                        "Unlimited Deployments",
                        "100 GB Storage",
                        "Dedicated Support",
                        "SLA",
                    ],
                    "popular": False,
                },
            ]

            return {"plans": plans}

        except Exception as e:
            _logger.error(f"Failed to fetch pricing: {str(e)}")
            return {"error": str(e)}
