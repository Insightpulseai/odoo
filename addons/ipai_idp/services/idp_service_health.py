# -*- coding: utf-8 -*-
"""
IDP Health Service.

Provides health check functionality for liveness, readiness, and deep health.
"""
import logging
import time

import requests
from odoo import api, models

_logger = logging.getLogger(__name__)


class IdpServiceHealth(models.AbstractModel):
    """
    IDP Health Check Service.

    Provides health endpoints for:
    - Liveness: Is the process alive?
    - Readiness: Can we accept traffic?
    - Health: Are all dependencies working?

    Attributes:
        _name: idp.service.health
        _description: IDP Health Service
    """

    _name = "idp.service.health"
    _description = "IDP Health Service"

    @api.model
    def check_liveness(self):
        """
        Liveness check - is the process alive?

        This should be extremely lightweight and never block.
        Used by Kubernetes livenessProbe.

        Returns:
            dict: {'status': 'alive'}
        """
        return {"status": "alive"}

    @api.model
    def check_readiness(self):
        """
        Readiness check - can we accept traffic?

        Checks database connectivity and basic model access.
        Used by Kubernetes readinessProbe.

        Returns:
            dict: {
                'status': 'ready'|'not_ready',
                'db': bool,
                'model_access': bool
            }
        """
        db_ok = self._check_db()
        model_ok = self._check_model_access()

        status = "ready" if (db_ok and model_ok) else "not_ready"

        return {
            "status": status,
            "db": db_ok,
            "model_access": model_ok,
        }

    @api.model
    def check_health(self):
        """
        Deep health check - are all dependencies working?

        Checks:
        - Database connectivity
        - Model access
        - OCR API availability
        - LLM API availability
        - Active model versions exist

        Used by monitoring systems and dashboards.

        Returns:
            dict: {
                'status': 'ok'|'degraded'|'unhealthy',
                'checks': {...},
                'timestamp': datetime
            }
        """
        checks = {}
        start_time = time.time()

        # Database check
        checks["db"] = self._check_db()

        # Model access check
        checks["model_access"] = self._check_model_access()

        # OCR API check
        checks["ocr_api"] = self._check_ocr_api()

        # LLM API check
        checks["llm_api"] = self._check_llm_api()

        # Model versions check
        checks["model_versions"] = self._check_model_versions()

        # Queue health (pending documents)
        checks["queue"] = self._check_queue_health()

        # Determine overall status
        critical_checks = ["db", "model_access"]
        important_checks = ["ocr_api", "llm_api", "model_versions"]

        critical_ok = all(checks.get(c, False) for c in critical_checks)
        important_ok = all(checks.get(c, False) for c in important_checks)

        if critical_ok and important_ok:
            status = "ok"
        elif critical_ok:
            status = "degraded"
        else:
            status = "unhealthy"

        total_time = int((time.time() - start_time) * 1000)

        return {
            "status": status,
            "checks": checks,
            "check_time_ms": total_time,
        }

    @api.model
    def _check_db(self):
        """Check database connectivity."""
        try:
            self.env.cr.execute("SELECT 1")
            return True
        except Exception as e:
            _logger.warning("DB health check failed: %s", e)
            return False

    @api.model
    def _check_model_access(self):
        """Check if core models are accessible."""
        try:
            # Try to access core IDP models
            self.env["idp.document"].search_count([])
            self.env["idp.extraction"].search_count([])
            return True
        except Exception as e:
            _logger.warning("Model access check failed: %s", e)
            return False

    @api.model
    def _check_ocr_api(self):
        """Check OCR API availability."""
        params = self.env["ir.config_parameter"].sudo()
        api_url = params.get_param("ipai_idp.ocr_api_url")

        if not api_url:
            return False

        try:
            # Try a simple health check endpoint
            health_url = api_url.rstrip("/") + "/health"
            response = requests.get(health_url, timeout=5)
            return response.status_code in (200, 404)  # 404 means API exists
        except requests.RequestException:
            # Try the base URL
            try:
                response = requests.head(api_url, timeout=5)
                return response.status_code < 500
            except requests.RequestException as e:
                _logger.warning("OCR API check failed: %s", e)
                return False

    @api.model
    def _check_llm_api(self):
        """Check LLM API availability."""
        params = self.env["ir.config_parameter"].sudo()
        api_url = params.get_param("ipai_idp.llm_api_url")

        if not api_url:
            return False

        try:
            # Just check if the endpoint is reachable
            response = requests.head(api_url, timeout=5)
            return response.status_code < 500
        except requests.RequestException as e:
            _logger.warning("LLM API check failed: %s", e)
            return False

    @api.model
    def _check_model_versions(self):
        """Check if active model versions exist."""
        try:
            count = self.env["idp.model.version"].search_count([("active", "=", True)])
            return count > 0
        except Exception as e:
            _logger.warning("Model versions check failed: %s", e)
            return False

    @api.model
    def _check_queue_health(self):
        """
        Check queue health (stuck documents).

        Returns True if no documents have been stuck in processing for too long.
        """
        try:
            from datetime import timedelta

            from odoo import fields

            # Check for documents stuck in processing for more than 10 minutes
            stuck_threshold = fields.Datetime.now() - timedelta(minutes=10)
            stuck_count = self.env["idp.document"].search_count(
                [
                    ("status", "=", "processing"),
                    ("write_date", "<", stuck_threshold),
                ]
            )
            return stuck_count == 0
        except Exception as e:
            _logger.warning("Queue health check failed: %s", e)
            return True  # Don't fail on optional check

    @api.model
    def get_metrics(self):
        """
        Get IDP processing metrics for monitoring.

        Returns:
            dict: Processing statistics
        """
        try:
            Document = self.env["idp.document"]
            Extraction = self.env["idp.extraction"]

            # Document counts by status
            status_counts = {}
            for status in [
                "queued",
                "processing",
                "extracted",
                "approved",
                "review_needed",
                "error",
            ]:
                status_counts[status] = Document.search_count(
                    [("status", "=", status)]
                )

            # Extraction metrics
            total_extractions = Extraction.search_count([])

            # Calculate success rate
            success_extractions = Extraction.search_count(
                [("validation_status", "=", "pass")]
            )
            success_rate = (
                (success_extractions / total_extractions * 100)
                if total_extractions > 0
                else 0
            )

            # Average confidence
            self.env.cr.execute(
                """
                SELECT AVG(confidence) FROM idp_extraction WHERE confidence > 0
            """
            )
            avg_confidence = self.env.cr.fetchone()[0] or 0

            # Auto-approval rate
            auto_approved = Document.search_count([("status", "=", "approved")])
            total_completed = Document.search_count(
                [("status", "in", ["approved", "reviewed", "exported"])]
            )
            auto_approval_rate = (
                (auto_approved / total_completed * 100) if total_completed > 0 else 0
            )

            return {
                "documents": {
                    "by_status": status_counts,
                    "total": sum(status_counts.values()),
                },
                "extractions": {
                    "total": total_extractions,
                    "success_rate": round(success_rate, 2),
                    "avg_confidence": round(avg_confidence, 3),
                },
                "processing": {
                    "auto_approval_rate": round(auto_approval_rate, 2),
                    "pending_review": status_counts.get("review_needed", 0),
                },
            }
        except Exception as e:
            _logger.exception("Failed to get metrics")
            return {"error": str(e)}
