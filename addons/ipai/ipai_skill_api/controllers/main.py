# -*- coding: utf-8 -*-
"""
REST API controllers for IPAI Agent Skills.

Provides JSON-RPC style endpoints for external agent surfaces.
Uses standard Odoo http.Controller for maximum compatibility.
When OCA base_rest is available, services/ can provide richer endpoints.
"""

import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class SkillAPIController(http.Controller):
    """REST API for agent skills and runs."""

    # -------------------------------------------------------------------------
    # Skills Endpoints
    # -------------------------------------------------------------------------

    @http.route(
        "/api/v1/skills",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def list_skills(self, **kwargs):
        """
        GET /api/v1/skills

        List all active skills with their metadata.

        Query params:
            - limit (int): Max results (default 100)
            - offset (int): Pagination offset
            - search (str): Filter by name/description

        Returns:
            JSON array of skill objects
        """
        limit = int(kwargs.get("limit", 100))
        offset = int(kwargs.get("offset", 0))
        search = kwargs.get("search", "")

        domain = [("is_active", "=", True)]
        if search:
            domain.append("|")
            domain.append(("name", "ilike", search))
            domain.append(("description", "ilike", search))

        Skill = request.env["ipai.agent.skill"].sudo()
        skills = Skill.search(domain, limit=limit, offset=offset)
        total = Skill.search_count(domain)

        result = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "skills": [self._skill_to_dict(s) for s in skills],
        }
        return self._json_response(result)

    @http.route(
        "/api/v1/skills/<string:skill_key>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_skill(self, skill_key, **kwargs):
        """
        GET /api/v1/skills/{key}

        Get skill details by key.

        Returns:
            Skill object with full details including workflow and tools
        """
        Skill = request.env["ipai.agent.skill"].sudo()
        skill = Skill.search(
            [("key", "=", skill_key), ("is_active", "=", True)], limit=1
        )

        if not skill:
            return self._json_error("Skill not found", 404)

        result = self._skill_to_dict(skill, full=True)
        return self._json_response(result)

    # -------------------------------------------------------------------------
    # Runs Endpoints
    # -------------------------------------------------------------------------

    @http.route(
        "/api/v1/runs",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def create_run(self, **kwargs):
        """
        POST /api/v1/runs

        Create a new run for a skill.

        Body (JSON):
            - skill_key (str): Required skill key
            - input_text (str): Optional user prompt
            - input_json (dict): Optional structured input
            - execute (bool): If true, execute immediately (default false)
            - external_ref (str): Optional external correlation ID

        Returns:
            Created run object
        """
        try:
            data = json.loads(request.httprequest.data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._json_error("Invalid JSON body", 400)

        skill_key = data.get("skill_key")
        if not skill_key:
            return self._json_error("skill_key is required", 400)

        Skill = request.env["ipai.agent.skill"].sudo()
        skill = Skill.search(
            [("key", "=", skill_key), ("is_active", "=", True)], limit=1
        )
        if not skill:
            return self._json_error(f"Skill not found: {skill_key}", 404)

        Run = request.env["ipai.agent.run"].sudo()
        run_vals = {
            "skill_id": skill.id,
            "input_text": data.get("input_text", ""),
            "input_json": json.dumps(data.get("input_json", {})),
        }

        # Add external_ref if model supports it
        if "external_ref" in Run._fields and data.get("external_ref"):
            run_vals["external_ref"] = data.get("external_ref")

        run = Run.create(run_vals)

        # Execute immediately if requested
        if data.get("execute"):
            try:
                run.action_execute()
            except Exception as e:
                _logger.exception("Run execution failed: %s", run.id)
                # Run already logged error, just continue

        result = self._run_to_dict(run)
        return self._json_response(result, status=201)

    @http.route(
        "/api/v1/runs/<int:run_id>",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_run(self, run_id, **kwargs):
        """
        GET /api/v1/runs/{id}

        Get run status and details.

        Returns:
            Run object with status, trace, and output
        """
        Run = request.env["ipai.agent.run"].sudo()
        run = Run.browse(run_id)

        if not run.exists():
            return self._json_error("Run not found", 404)

        result = self._run_to_dict(run, full=True)
        return self._json_response(result)

    @http.route(
        "/api/v1/runs/<int:run_id>/execute",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def execute_run(self, run_id, **kwargs):
        """
        POST /api/v1/runs/{id}/execute

        Execute a run that is in draft or failed state.

        Returns:
            Updated run object
        """
        Run = request.env["ipai.agent.run"].sudo()
        run = Run.browse(run_id)

        if not run.exists():
            return self._json_error("Run not found", 404)

        if run.state not in ("draft", "failed"):
            return self._json_error(
                f"Run cannot be executed in state: {run.state}", 400
            )

        try:
            run.action_execute()
        except Exception as e:
            _logger.exception("Run execution failed: %s", run.id)
            # Run already logged error

        result = self._run_to_dict(run, full=True)
        return self._json_response(result)

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------

    @http.route(
        "/api/v1/health",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def health_check(self, **kwargs):
        """
        GET /api/v1/health

        Health check endpoint (no auth required).
        """
        return self._json_response(
            {
                "status": "ok",
                "service": "ipai_skill_api",
                "version": "1.0.0",
            }
        )

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _skill_to_dict(self, skill, full=False):
        """Convert skill record to dict."""
        result = {
            "id": skill.id,
            "key": skill.key,
            "name": skill.name,
            "version": skill.version,
            "description": skill.description or "",
            "is_active": skill.is_active,
            "run_count": skill.run_count,
        }

        if full:
            result.update(
                {
                    "intents": skill.get_intents_list(),
                    "guardrails": skill.get_guardrails_list(),
                    "workflow": skill.get_workflow_tools(),
                    "tools": [
                        {"id": t.id, "key": t.key, "name": t.name}
                        for t in skill.tool_ids
                    ],
                    "knowledge_sources": [
                        {"id": k.id, "name": k.name} for k in skill.knowledge_ids
                    ],
                }
            )

        return result

    def _run_to_dict(self, run, full=False):
        """Convert run record to dict."""
        result = {
            "id": run.id,
            "name": run.name,
            "state": run.state,
            "skill_key": run.skill_key,
            "created_at": run.create_date.isoformat() if run.create_date else None,
        }

        if full:
            result.update(
                {
                    "input_text": run.input_text or "",
                    "input_json": run.get_input_dict(),
                    "output_text": run.output_text or "",
                    "output_json": run.get_output_dict(),
                    "error_text": run.error_text or "",
                    "trace": run.get_trace_list(),
                    "started_at": (
                        run.started_at.isoformat() if run.started_at else None
                    ),
                    "completed_at": (
                        run.completed_at.isoformat() if run.completed_at else None
                    ),
                    "duration_seconds": run.duration_seconds,
                }
            )

        return result

    def _json_response(self, data, status=200):
        """Return JSON response."""
        return Response(
            json.dumps(data, ensure_ascii=False, default=str),
            status=status,
            headers=[("Content-Type", "application/json")],
        )

    def _json_error(self, message, status=400):
        """Return JSON error response."""
        return self._json_response({"error": message}, status=status)
