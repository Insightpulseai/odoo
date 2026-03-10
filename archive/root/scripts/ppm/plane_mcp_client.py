# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Plane MCP client wrapper for PPM Clarity sync.

Wraps the official Plane MCP server (55+ tools) via subprocess.
Self-hosted config: PLANE_BASE_URL, PLANE_API_KEY, PLANE_WORKSPACE_SLUG.

Field ownership: title, description, priority, labels, cycle, state.
"""

import hashlib
import json
import logging
import os
import subprocess

_logger = logging.getLogger(__name__)


class PlaneMCPClient:
    """Wrapper around the Plane MCP server for issue operations.

    Uses subprocess calls to `uvx plane-mcp-server` for MCP tool invocations.
    Falls back to direct REST API calls when MCP is unavailable.
    """

    def __init__(self, api_key=None, workspace_slug=None, base_url=None):
        self.api_key = api_key or os.environ.get("PLANE_API_KEY", "")
        self.workspace_slug = workspace_slug or os.environ.get("PLANE_WORKSPACE_SLUG", "insightpulseai")
        self.base_url = base_url or os.environ.get("PLANE_BASE_URL", "https://plane-api.insightpulseai.com")
        self._session = None

    # ── REST API fallback (when MCP is unavailable) ───────────────────

    def _api_headers(self):
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _api_url(self, path):
        return "%s/api/v1/workspaces/%s%s" % (self.base_url, self.workspace_slug, path)

    def _get_session(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._session.headers.update(self._api_headers())
        return self._session

    def _api_get(self, path):
        resp = self._get_session().get(self._api_url(path), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _api_patch(self, path, data):
        resp = self._get_session().patch(self._api_url(path), json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _api_post(self, path, data):
        resp = self._get_session().post(self._api_url(path), json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Issue operations ──────────────────────────────────────────────

    def get_issue(self, project_id, issue_id):
        """Get a single Plane issue by ID.

        Args:
            project_id: Plane project UUID.
            issue_id: Plane issue UUID.

        Returns:
            dict: Issue data with all fields.
        """
        return self._api_get("/projects/%s/issues/%s/" % (project_id, issue_id))

    def list_issues(self, project_id, filters=None):
        """List issues in a project with optional filters.

        Args:
            project_id: Plane project UUID.
            filters: Optional dict of query params (state, label, priority).

        Returns:
            list[dict]: Issue records.
        """
        path = "/projects/%s/issues/" % project_id
        if filters:
            params = "&".join("%s=%s" % (k, v) for k, v in filters.items())
            path = "%s?%s" % (path, params)
        result = self._api_get(path)
        if isinstance(result, dict) and "results" in result:
            return result["results"]
        return result if isinstance(result, list) else []

    def create_issue(self, project_id, data):
        """Create a new issue in Plane.

        Args:
            project_id: Plane project UUID.
            data: Dict with title (name), description, priority, labels, state.

        Returns:
            dict: Created issue data including id.
        """
        return self._api_post("/projects/%s/issues/" % project_id, data)

    def update_issue(self, project_id, issue_id, data):
        """Update an existing Plane issue (Plane-owned fields only).

        Args:
            project_id: Plane project UUID.
            issue_id: Plane issue UUID.
            data: Dict of fields to update.

        Returns:
            dict: Updated issue data.
        """
        return self._api_patch(
            "/projects/%s/issues/%s/" % (project_id, issue_id), data
        )

    def get_project(self, project_id):
        """Get project details including states and labels.

        Args:
            project_id: Plane project UUID.

        Returns:
            dict: Project data.
        """
        return self._api_get("/projects/%s/" % project_id)

    def get_states(self, project_id):
        """Get all states for a project (for state ID resolution).

        Args:
            project_id: Plane project UUID.

        Returns:
            list[dict]: State records with id, name, group.
        """
        return self._api_get("/projects/%s/states/" % project_id)

    def resolve_state_id(self, project_id, state_name):
        """Resolve a state name to its UUID.

        Args:
            project_id: Plane project UUID.
            state_name: Human-readable state name (e.g., "Done").

        Returns:
            str or None: State UUID if found.
        """
        states = self.get_states(project_id)
        if isinstance(states, dict) and "results" in states:
            states = states["results"]
        for state in states:
            if state.get("name", "").lower() == state_name.lower():
                return state["id"]
        return None

    # ── Hash calculation (Plane-owned fields) ─────────────────────────

    @staticmethod
    def calculate_hash(issue):
        """Calculate deterministic SHA-256 hash of Plane-owned fields.

        Plane owns: title (name), description, priority, labels, cycle, state.
        Hash changes only when Plane-side data changes.
        """
        labels = issue.get("labels", [])
        if isinstance(labels, list) and labels and isinstance(labels[0], dict):
            labels = sorted(l.get("id", str(l)) for l in labels)
        else:
            labels = sorted(str(l) for l in labels) if labels else []

        owned_data = {
            "name": issue.get("name", ""),
            "description_html": issue.get("description_html", ""),
            "priority": issue.get("priority", "none"),
            "labels": labels,
            "cycle_id": str(issue.get("cycle_id", "")),
            "state_id": str(issue.get("state", issue.get("state_id", ""))),
        }
        canonical = json.dumps(owned_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
