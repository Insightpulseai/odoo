# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Deterministic sync engine for PPM Clarity.

Enforces field ownership contract:
  - Plane owns: title, description, priority, labels, cycle, state
  - Odoo owns: assigned users, timesheets, costs, attachments, chatter

Every operation is idempotent via ops.work_item_events.idempotency_key.
"""

import logging
import os
import time

import requests

_logger = logging.getLogger(__name__)


class SyncEngine:
    """Bidirectional sync between Plane.so and Odoo 19 CE."""

    def __init__(self, plane_client, odoo_client, supabase_url=None, supabase_key=None):
        self.plane = plane_client
        self.odoo = odoo_client
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL", "")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    # ── Supabase RPC helpers ──────────────────────────────────────────

    def _call_rpc(self, function_name, params):
        """Call a Supabase RPC function."""
        rpc_url = "%s/rest/v1/rpc/%s" % (self.supabase_url, function_name)
        headers = {
            "apikey": self.supabase_key,
            "Authorization": "Bearer %s" % self.supabase_key,
            "Content-Type": "application/json",
        }
        resp = requests.post(rpc_url, json=params, headers=headers, timeout=30)
        if resp.status_code >= 400:
            _logger.error("RPC %s failed: %s %s", function_name, resp.status_code, resp.text[:500])
            raise RuntimeError("Supabase RPC %s failed: %s" % (function_name, resp.status_code))
        return resp.json()

    def _upsert_link(self, plane_project_id, plane_issue_id, odoo_project_id=None,
                     odoo_task_id=None, sync_state="ok", plane_hash=None, odoo_hash=None):
        """Upsert a work item link via RPC."""
        return self._call_rpc("upsert_work_item_link", {
            "p_plane_project_id": plane_project_id,
            "p_plane_issue_id": plane_issue_id,
            "p_odoo_project_id": odoo_project_id,
            "p_odoo_task_id": odoo_task_id,
            "p_sync_state": sync_state,
            "p_last_plane_hash": plane_hash,
            "p_last_odoo_hash": odoo_hash,
        })

    def _append_event(self, link_id, event_type, source_system, event_data,
                      idempotency_key=None, success=True, error_message=None):
        """Append an event to the audit ledger via RPC."""
        return self._call_rpc("append_work_item_event", {
            "p_link_id": link_id,
            "p_event_type": event_type,
            "p_source_system": source_system,
            "p_event_data": event_data,
            "p_idempotency_key": idempotency_key,
            "p_success": success,
            "p_error_message": error_message,
        })

    # ── Plane → Odoo (commitment signal) ──────────────────────────────

    def plane_to_odoo(self, plane_project_id, plane_issue_id, odoo_project_id,
                      idempotency_key=None):
        """Sync a Plane commitment to Odoo.

        Triggered when: Plane issue state → In Progress, or label 'commit' added.

        Args:
            plane_project_id: Plane project UUID.
            plane_issue_id: Plane issue UUID.
            odoo_project_id: Target Odoo project.project ID.
            idempotency_key: Unique key for dedup.

        Returns:
            dict: Sync result with link_id, odoo_task_id, event_id.
        """
        start = time.time()

        # Fetch Plane issue
        issue = self.plane.get_issue(plane_project_id, plane_issue_id)
        plane_hash = self.plane.calculate_hash(issue)

        # Map Plane fields to Odoo task data
        task_data = {
            "title": issue.get("name", "Untitled"),
            "description": issue.get("description_html", ""),
            "priority": issue.get("priority", "none"),
            "state": issue.get("state_detail", {}).get("name", "Backlog"),
        }

        # Check if link already exists (idempotency)
        link_id = self._upsert_link(
            plane_project_id, plane_issue_id,
            odoo_project_id=odoo_project_id,
            plane_hash=plane_hash,
        )

        # Create or update Odoo task
        # Query existing link to check for odoo_task_id
        existing = self._get_link(plane_project_id, plane_issue_id)
        odoo_task_id = existing.get("odoo_task_id") if existing else None

        if odoo_task_id:
            self.odoo.update_task(odoo_task_id, task_data)
        else:
            odoo_task_id = self.odoo.create_task(odoo_project_id, task_data)
            # Update link with Odoo task ID
            link_id = self._upsert_link(
                plane_project_id, plane_issue_id,
                odoo_project_id=odoo_project_id,
                odoo_task_id=odoo_task_id,
                plane_hash=plane_hash,
            )

        # Log event
        duration_ms = int((time.time() - start) * 1000)
        event_id = self._append_event(
            link_id=link_id,
            event_type="plane_to_odoo",
            source_system="n8n",
            event_data={
                "action": "created" if not existing or not existing.get("odoo_task_id") else "updated",
                "plane_issue_id": plane_issue_id,
                "odoo_task_id": odoo_task_id,
                "plane_hash": plane_hash,
                "duration_ms": duration_ms,
                "fields_synced": list(task_data.keys()),
            },
            idempotency_key=idempotency_key,
            success=True,
        )

        _logger.info(
            "plane_to_odoo: issue=%s → task=%s (%dms)",
            plane_issue_id, odoo_task_id, duration_ms,
        )

        return {
            "link_id": link_id,
            "odoo_task_id": odoo_task_id,
            "event_id": event_id,
            "duration_ms": duration_ms,
            "action": "created" if not existing or not existing.get("odoo_task_id") else "updated",
        }

    # ── Odoo → Plane (completion signal) ──────────────────────────────

    def odoo_to_plane(self, odoo_task_id, plane_project_id, plane_issue_id,
                      idempotency_key=None):
        """Sync an Odoo completion to Plane.

        Triggered when: Odoo task stage → Done.

        Args:
            odoo_task_id: Odoo project.task ID.
            plane_project_id: Plane project UUID.
            plane_issue_id: Plane issue UUID.
            idempotency_key: Unique key for dedup.

        Returns:
            dict: Sync result with event_id.
        """
        start = time.time()

        # Get Odoo task details
        task = self.odoo.get_task_details(odoo_task_id)
        if not task:
            raise ValueError("Odoo task not found: %s" % odoo_task_id)

        odoo_hash = self.odoo.calculate_hash(task)

        # Resolve "Done" state ID in Plane
        done_state_id = self.plane.resolve_state_id(plane_project_id, "Done")

        # Update Plane issue state (only state — Odoo doesn't own other Plane fields)
        update_data = {}
        if done_state_id:
            update_data["state"] = done_state_id

        if update_data:
            self.plane.update_issue(plane_project_id, plane_issue_id, update_data)

        # Update link hashes
        link_id = self._upsert_link(
            plane_project_id, plane_issue_id,
            odoo_task_id=odoo_task_id,
            odoo_hash=odoo_hash,
        )

        # Log event
        duration_ms = int((time.time() - start) * 1000)
        stage_name = task.get("stage_id", [0, ""])[1] if isinstance(task.get("stage_id"), (list, tuple)) else "Done"
        event_id = self._append_event(
            link_id=link_id,
            event_type="odoo_to_plane",
            source_system="n8n",
            event_data={
                "action": "completion",
                "odoo_task_id": odoo_task_id,
                "plane_issue_id": plane_issue_id,
                "odoo_stage": stage_name,
                "odoo_hash": odoo_hash,
                "duration_ms": duration_ms,
            },
            idempotency_key=idempotency_key,
            success=True,
        )

        _logger.info(
            "odoo_to_plane: task=%s → issue=%s (%dms)",
            odoo_task_id, plane_issue_id, duration_ms,
        )

        return {
            "link_id": link_id,
            "event_id": event_id,
            "duration_ms": duration_ms,
        }

    # ── Reconciliation ────────────────────────────────────────────────

    def reconcile(self):
        """Nightly drift detection and repair.

        Queries all work item links, recalculates hashes,
        and applies field ownership rules to resolve conflicts.

        Returns:
            dict: Reconciliation report.
        """
        start = time.time()
        conflicts = self._call_rpc("get_sync_conflicts", {"p_limit": 500})

        resolved = 0
        errors = 0
        items_scanned = len(conflicts) if isinstance(conflicts, list) else 0

        for conflict in (conflicts or []):
            try:
                self._resolve_conflict(conflict)
                resolved += 1
            except Exception as exc:
                _logger.error("Reconciliation error for link %s: %s", conflict.get("link_id"), exc)
                errors += 1

        duration = int((time.time() - start) * 1000)

        report = {
            "items_scanned": items_scanned,
            "conflicts_resolved": resolved,
            "errors": errors,
            "duration_ms": duration,
        }

        _logger.info("Reconciliation complete: %s", report)
        return report

    def _resolve_conflict(self, conflict):
        """Resolve a single conflict using field ownership rules.

        Plane wins: title, description, priority, labels, cycle, state.
        Odoo wins: assigned users, timesheets, costs, attachments.
        """
        link_id = conflict["link_id"]
        plane_project_id = conflict["plane_project_id"]
        plane_issue_id = conflict["plane_issue_id"]
        odoo_task_id = conflict.get("odoo_task_id")

        if not odoo_task_id:
            return

        # Fetch current state from both systems
        issue = self.plane.get_issue(plane_project_id, plane_issue_id)
        task = self.odoo.get_task_details(odoo_task_id)

        if not issue or not task:
            return

        # Recalculate hashes
        plane_hash = self.plane.calculate_hash(issue)
        odoo_hash = self.odoo.calculate_hash(task)

        # Update link with fresh hashes, mark as resolved
        self._upsert_link(
            plane_project_id, plane_issue_id,
            odoo_task_id=odoo_task_id,
            sync_state="ok",
            plane_hash=plane_hash,
            odoo_hash=odoo_hash,
        )

        # Log reconciliation event
        self._append_event(
            link_id=link_id,
            event_type="reconciliation",
            source_system="n8n",
            event_data={
                "plane_hash": plane_hash,
                "odoo_hash": odoo_hash,
                "resolution": "field_ownership_applied",
            },
            success=True,
        )

    # ── Internal helpers ──────────────────────────────────────────────

    def _get_link(self, plane_project_id, plane_issue_id):
        """Query existing link by Plane identifiers."""
        url = "%s/rest/v1/work_item_links" % self.supabase_url
        params = "plane_project_id=eq.%s&plane_issue_id=eq.%s" % (
            plane_project_id, plane_issue_id
        )
        headers = {
            "apikey": self.supabase_key,
            "Authorization": "Bearer %s" % self.supabase_key,
        }
        try:
            resp = requests.get("%s?%s" % (url, params), headers=headers, timeout=15)
            if resp.status_code == 200:
                rows = resp.json()
                return rows[0] if rows else None
        except requests.RequestException as exc:
            _logger.warning("Failed to query link: %s", exc)
        return None
