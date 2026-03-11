"""Plane.so API client for PPM Clarity integration.

This module provides a Python client for interacting with the Plane.so API
to manage work items, calculate field ownership hashes, and synchronize with Odoo.
"""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import httpx


class PlaneClient:
    """Client for Plane.so API with X-API-Key authentication.

    Field Ownership (Plane-owned):
    - title (name)
    - description (description_html)
    - priority
    - labels (label_ids)
    - cycle (cycle_id)
    - state (state_id)
    - estimate (estimate_point)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace_slug: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Plane client.

        Args:
            api_key: Plane API key (defaults to PLANE_API_KEY env var)
            workspace_slug: Plane workspace slug (defaults to PLANE_WORKSPACE_SLUG env var)
            base_url: Plane API base URL (defaults to PLANE_BASE_URL env var or https://api.plane.so)
        """
        self.api_key = api_key or os.getenv("PLANE_API_KEY")
        self.workspace_slug = workspace_slug or os.getenv("PLANE_WORKSPACE_SLUG")
        self.base_url = (
            base_url or os.getenv("PLANE_BASE_URL") or "https://api.plane.so"
        )

        if not self.api_key:
            raise ValueError("PLANE_API_KEY not provided and not found in environment")
        if not self.workspace_slug:
            raise ValueError(
                "PLANE_WORKSPACE_SLUG not provided and not found in environment"
            )

        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """Make GET request to Plane API."""
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_slug}/{endpoint}"
        response = httpx.get(url, headers=self.headers, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """Make POST request to Plane API."""
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_slug}/{endpoint}"
        response = httpx.post(url, headers=self.headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """Make PATCH request to Plane API."""
        url = f"{self.base_url}/api/v1/workspaces/{self.workspace_slug}/{endpoint}"
        response = httpx.patch(url, headers=self.headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def get_project(self, project_id: str) -> Dict:
        """Get Plane project by ID.

        Args:
            project_id: Plane project ID

        Returns:
            Project object with metadata
        """
        return self._get(f"projects/{project_id}")

    def list_issues(
        self, project_id: str, state: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """List issues in a Plane project.

        Args:
            project_id: Plane project ID
            state: Optional state filter (e.g., "Planned", "In Progress")
            limit: Maximum number of issues to return

        Returns:
            List of issue objects
        """
        params = {"limit": limit}
        if state:
            params["state"] = state

        return self._get(f"projects/{project_id}/issues", params=params)

    def get_issue(self, project_id: str, issue_id: str) -> Dict:
        """Get single issue by ID.

        Args:
            project_id: Plane project ID
            issue_id: Plane issue ID

        Returns:
            Issue object with full details
        """
        return self._get(f"projects/{project_id}/issues/{issue_id}")

    def create_issue(self, project_id: str, data: Dict[str, Any]) -> Dict:
        """Create new issue in Plane project.

        Args:
            project_id: Plane project ID
            data: Issue data (name, description_html, priority, etc.)

        Returns:
            Created issue object
        """
        return self._post(f"projects/{project_id}/issues", data)

    def update_issue(
        self, project_id: str, issue_id: str, data: Dict[str, Any]
    ) -> Dict:
        """Update existing issue (facts-only writeback from Odoo).

        Args:
            project_id: Plane project ID
            issue_id: Plane issue ID
            data: Update data (only facts like state change)

        Returns:
            Updated issue object
        """
        return self._patch(f"projects/{project_id}/issues/{issue_id}", data)

    def create_comment(
        self, project_id: str, issue_id: str, comment: str
    ) -> Dict:
        """Add comment to Plane issue (for Odoo metrics writeback).

        Args:
            project_id: Plane project ID
            issue_id: Plane issue ID
            comment: Comment text (supports Markdown)

        Returns:
            Created comment object
        """
        return self._post(
            f"projects/{project_id}/issues/{issue_id}/comments",
            {"comment_html": comment},
        )

    def calculate_hash(self, issue: Dict) -> str:
        """Calculate deterministic hash of Plane-owned fields.

        This hash is used to detect drift between Plane and Odoo.
        Only Plane-owned fields are included to avoid false positives
        from Odoo-owned field changes.

        Args:
            issue: Plane issue object

        Returns:
            SHA256 hex digest of canonical JSON representation
        """
        canonical_fields = {
            "title": issue.get("name", ""),
            "description": issue.get("description_html", ""),
            "priority": issue.get("priority", ""),
            "labels": sorted(
                [
                    label["id"] if isinstance(label, dict) else label
                    for label in issue.get("label_ids", [])
                ]
            ),
            "cycle": issue.get("cycle_id"),
            "state": issue.get("state_id"),
            "estimate": issue.get("estimate_point"),
        }
        # Deterministic JSON serialization (sorted keys, no whitespace)
        canonical_json = json.dumps(canonical_fields, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode()).hexdigest()
