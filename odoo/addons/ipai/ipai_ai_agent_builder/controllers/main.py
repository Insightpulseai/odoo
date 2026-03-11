# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiAiAgentController(http.Controller):
    """REST API endpoints for AI Agent operations."""

    @http.route(
        "/ipai/ai/v1/agent/<int:agent_id>/chat",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def agent_chat(self, agent_id, message, context=None, **kwargs):
        """Process a chat message with the specified agent.

        Args:
            agent_id: ID of the agent to chat with
            message: User's message
            context: Optional context dictionary

        Returns:
            dict with run_id, response, tool_calls, sources
        """
        agent = request.env["ipai.ai.agent"].browse(agent_id)
        if not agent.exists():
            return {"error": "Agent not found", "code": 404}
        if not agent.active:
            return {"error": "Agent is not active", "code": 400}

        try:
            result = agent.chat(message, context=context or {})
            return result
        except Exception as e:
            _logger.exception(f"Error in agent chat: {agent_id}")
            return {"error": str(e), "code": 500}

    @http.route(
        "/ipai/ai/v1/agent/<int:agent_id>/runs",
        type="json",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def agent_runs(self, agent_id, limit=10, **kwargs):
        """Get recent runs for the specified agent.

        Args:
            agent_id: ID of the agent
            limit: Maximum number of runs to return

        Returns:
            list of run summaries
        """
        agent = request.env["ipai.ai.agent"].browse(agent_id)
        if not agent.exists():
            return {"error": "Agent not found", "code": 404}

        runs = request.env["ipai.ai.run"].get_recent_runs(
            agent_id=agent_id,
            limit=limit,
        )
        return [
            {
                "id": run.id,
                "input": run.input[:100] if run.input else None,
                "output": run.output[:100] if run.output else None,
                "provider": run.provider,
                "model": run.model,
                "latency_ms": run.latency_ms,
                "created_at": run.create_date.isoformat() if run.create_date else None,
            }
            for run in runs
        ]

    @http.route(
        "/ipai/ai/v1/source/<int:source_id>/ingest",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def source_ingest(self, source_id, **kwargs):
        """Trigger ingestion for a source.

        Args:
            source_id: ID of the source to ingest

        Returns:
            dict with status and chunk count
        """
        source = request.env["ipai.ai.source"].browse(source_id)
        if not source.exists():
            return {"error": "Source not found", "code": 404}

        try:
            source.action_ingest()
            return {
                "status": source.ingest_status,
                "chunk_count": len(source.chunk_ids),
            }
        except Exception as e:
            _logger.exception(f"Error ingesting source: {source_id}")
            return {"error": str(e), "code": 500}

    @http.route(
        "/ipai/ai/v1/tool/<string:tool_key>/invoke",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def tool_invoke(self, tool_key, input_data, dry_run=False, **kwargs):
        """Invoke a tool directly (internal use).

        Args:
            tool_key: Unique key of the tool
            input_data: Input parameters for the tool
            dry_run: Whether to execute in dry-run mode

        Returns:
            dict with status and output
        """
        tool = request.env["ipai.ai.tool"].search([("key", "=", tool_key)], limit=1)
        if not tool:
            return {"error": "Tool not found", "code": 404}

        if not tool.check_permission():
            return {"error": "Permission denied", "code": 403}

        try:
            result = tool.execute(
                request.env,
                input_data,
                dry_run=dry_run,
            )
            return {
                "status": "dry_run" if dry_run else "success",
                "output": result,
            }
        except Exception as e:
            _logger.exception(f"Error invoking tool: {tool_key}")
            return {"error": str(e), "code": 500}

    @http.route(
        "/ipai/ai/v1/agents",
        type="json",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def list_agents(self, **kwargs):
        """List all active agents.

        Returns:
            list of agent summaries
        """
        agents = request.env["ipai.ai.agent"].search([("active", "=", True)])
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "provider": agent.provider,
                "model": agent.model,
                "style": agent.style,
                "topic_count": len(agent.topic_ids),
                "source_count": len(agent.source_ids),
                "run_count": agent.run_count,
            }
            for agent in agents
        ]

    @http.route(
        "/ipai/ai/v1/tools",
        type="json",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def list_tools(self, **kwargs):
        """List all active tools.

        Returns:
            list of tool summaries
        """
        tools = request.env["ipai.ai.tool"].search([("active", "=", True)])
        return [
            {
                "key": tool.key,
                "name": tool.name,
                "description": tool.description,
                "dry_run_supported": tool.dry_run_supported,
                "has_permission": tool.check_permission(),
            }
            for tool in tools
        ]
