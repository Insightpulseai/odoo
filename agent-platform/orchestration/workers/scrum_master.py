"""Scrum Master specialist worker.

Handles: standup, velocity, retro, drift
Per: agents/skills/scrum_master/SKILL.md
Role: specialist_worker (invoked_by: [pulser_supervisor])
"""

import logging

logger = logging.getLogger(__name__)


def handle(request: dict) -> dict:
    """Handle a scrum master task dispatched by the supervisor."""
    from agent_platform.orchestration.supervisor.server import build_result_envelope

    task_type = request.get("task_type", "unknown")
    message = request["input_contract"].get("message", "")

    # Stub: return structured response per skill
    # In production: calls ADO REST via MCP + Foundry gpt-4.1
    handlers = {
        "standup": _handle_standup,
        "velocity": _handle_velocity,
        "retro": _handle_retro,
        "drift": _handle_drift,
    }

    handler = handlers.get(task_type, _handle_unknown)
    payload = handler(message, request)

    return build_result_envelope(
        request_id=request["request_id"],
        workflow_id=request["workflow_id"],
        step_id=f"worker.scrum_master.{task_type}",
        agent_id="pulser_scrum_master",
        status="success",
        payload=payload,
    )


def _handle_standup(message: str, request: dict) -> dict:
    return {
        "type": "standup",
        "digest_markdown": "## Daily Standup\n\n> Stub — ADO REST + Foundry rendering ships with full MCP wiring.",
        "blockers": [],
        "completed_yesterday": [],
        "in_progress_today": [],
    }


def _handle_velocity(message: str, request: dict) -> dict:
    return {
        "type": "velocity",
        "trend_markdown": "## Velocity Trend\n\n> Stub — ADO Analytics OData + DORA metrics pending.",
        "chart_data": {"labels": [], "committed": [], "completed": []},
    }


def _handle_retro(message: str, request: dict) -> dict:
    return {
        "type": "retro",
        "synthesis_markdown": "## Retro Synthesis\n\n> Stub — Foundry gpt-4.1 synthesis pending.",
        "wins": [],
        "drags": [],
        "proposed_action_items": [],
    }


def _handle_drift(message: str, request: dict) -> dict:
    return {
        "type": "drift",
        "summary_markdown": "## Doctrine Drift Scan\n\n> Stub — WI scan for deprecated refs pending.",
        "findings": [],
    }


def _handle_unknown(message: str, request: dict) -> dict:
    return {"type": "unknown", "message": f"Scrum Master received unrecognized task: {message[:100]}"}
