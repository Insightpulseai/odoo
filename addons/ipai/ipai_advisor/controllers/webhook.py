# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AdvisorWebhook(http.Controller):
    """Webhook controller for external signal ingestion (n8n, GitHub, etc.)."""

    @http.route(
        "/api/advisor/ingest",
        type="json",
        auth="api_key",
        methods=["POST"],
        csrf=False,
    )
    def ingest_recommendations(self, **kwargs):
        """
        Ingest recommendations from external sources.

        Expected payload:
        {
            "recommendations": [
                {
                    "category": "reliability",
                    "severity": "high",
                    "title": "Pod restart loop detected",
                    "description": "...",
                    "resource_type": "k8s.pod",
                    "resource_ref": "namespace/pod-name",
                    "source": "k8s",
                    "evidence": {...},
                    "impact_score": 75
                }
            ]
        }

        Returns:
        {
            "ok": true,
            "created": 3,
            "updated": 1
        }
        """
        try:
            data = request.jsonrequest
            recommendations = data.get("recommendations", [])

            if not recommendations:
                return {"ok": False, "error": "No recommendations provided"}

            Recommendation = request.env["advisor.recommendation"].sudo()
            created = 0
            updated = 0

            for rec_data in recommendations:
                try:
                    rec = Recommendation.create_from_signal(rec_data)
                    if rec:
                        created += 1
                except Exception as e:
                    _logger.warning(f"Failed to create recommendation: {e}")
                    continue

            # Trigger score recomputation
            request.env["advisor.score"].sudo().compute_scores()

            return {
                "ok": True,
                "created": created,
                "updated": updated,
            }

        except Exception as e:
            _logger.exception("Error in advisor ingest webhook")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/api/advisor/scores",
        type="json",
        auth="api_key",
        methods=["GET"],
        csrf=False,
    )
    def get_scores(self, **kwargs):
        """
        Get latest scores for all categories.

        Returns:
        {
            "ok": true,
            "scores": [
                {"category": "cost", "score": 85, "open_count": 3, ...},
                ...
            ]
        }
        """
        try:
            Score = request.env["advisor.score"].sudo()
            scores = Score.get_latest_scores()

            return {
                "ok": True,
                "scores": scores,
            }

        except Exception as e:
            _logger.exception("Error getting advisor scores")
            return {"ok": False, "error": str(e)}

    @http.route(
        "/api/advisor/recompute",
        type="json",
        auth="api_key",
        methods=["POST"],
        csrf=False,
    )
    def recompute_scores(self, **kwargs):
        """
        Trigger score recomputation for all categories.
        Typically called by a cron job via n8n.
        """
        try:
            request.env["advisor.score"].sudo().compute_scores()
            return {"ok": True, "message": "Scores recomputed"}

        except Exception as e:
            _logger.exception("Error recomputing scores")
            return {"ok": False, "error": str(e)}
