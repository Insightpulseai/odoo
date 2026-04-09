# -*- coding: utf-8 -*-
"""Bridge service: Odoo → agent-platform for source ingestion.

This service is the ONLY place in Odoo that talks to agent-platform
for source indexing. All extraction, OCR, chunking, embedding, and
retrieval orchestration happens outside Odoo.
"""

import json
import logging
import os
import urllib.error
import urllib.request

from odoo import api, models

_logger = logging.getLogger(__name__)

_AGENT_PLATFORM_TIMEOUT = 120  # seconds — extraction can be slow


class AgentSourceBridge(models.AbstractModel):
    _name = "ipai.ai.agent.source.bridge"
    _description = "Agent Source Bridge to agent-platform"

    @api.model
    def _get_platform_url(self):
        """Resolve agent-platform base URL."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "ipai.agent_platform.url",
                os.environ.get("AGENT_PLATFORM_URL", "http://localhost:8088"),
            )
        )

    @api.model
    def submit_source(self, source):
        """Submit a source to agent-platform for extraction + indexing.

        The platform will call back via /ipai/agent/source/callback
        when processing completes (success or failure).
        """
        base_url = self._get_platform_url()
        url = "%s/api/agent/sources/ingest" % base_url.rstrip("/")

        payload = {
            "source_id": source.id,
            "agent_id": source.agent_id.id,
            "external_agent_id": source.agent_id.external_agent_id or "",
            "source_type": source.source_type,
            "name": source.name,
            "checksum": source.checksum or "",
            "callback_url": self._get_callback_url(),
        }

        # Add type-specific payload
        if source.attachment_id:
            payload["attachment"] = {
                "filename": source.attachment_id.name,
                "mimetype": source.attachment_id.mimetype,
                "size": source.attachment_id.file_size,
                "download_url": "/web/content/%d" % source.attachment_id.id,
            }
        elif source.url:
            payload["url"] = source.url
        elif source.knowledge_ref:
            payload["knowledge_ref"] = source.knowledge_ref

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Add service key if configured
        service_key = os.environ.get("AGENT_PLATFORM_SERVICE_KEY", "")
        if service_key:
            headers["X-Service-Key"] = service_key

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=_AGENT_PLATFORM_TIMEOUT) as resp:
                resp_data = json.loads(resp.read().decode("utf-8", errors="replace"))
                _logger.info(
                    "Source %d submitted to agent-platform: %s",
                    source.id,
                    resp_data.get("status", "unknown"),
                )
                return resp_data
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
            error_msg = "Platform HTTP %d: %s" % (e.code, error_body)
            _logger.warning("Source submit failed: %s", error_msg)
            source.callback_failed(error_msg)
            return {"error": True, "message": error_msg}
        except urllib.error.URLError as e:
            error_msg = "Platform unreachable: %s" % e.reason
            _logger.warning("Source submit failed: %s", error_msg)
            source.callback_failed(error_msg)
            return {"error": True, "message": error_msg}
        except Exception as e:
            error_msg = "Unexpected error: %s" % str(e)
            _logger.exception("Source submit failed")
            source.callback_failed(error_msg)
            return {"error": True, "message": error_msg}

    @api.model
    def _get_callback_url(self):
        """Build the callback URL for agent-platform to call back."""
        base = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url", "http://localhost:8069")
        )
        return "%s/ipai/agent/source/callback" % base.rstrip("/")

    @api.model
    def get_active_source_ids(self, agent_id):
        """Return external source IDs for active indexed sources.

        Used by the chat path to restrict Foundry retrieval
        to only the agent's active sources.
        """
        sources = self.env["ipai.ai.agent.source"]._get_active_indexed_sources(
            agent_id
        )
        return [
            {
                "external_source_id": s.external_source_id,
                "external_index_id": s.external_index_id,
                "name": s.name,
                "source_type": s.source_type,
            }
            for s in sources
            if s.external_source_id
        ]
