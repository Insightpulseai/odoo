# -*- coding: utf-8 -*-
import json
import logging
import uuid

import requests
from odoo.tools import html2plaintext

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiAskAiChatterRequest(models.Model):
    _name = "ipai.ask_ai_chatter.request"
    _description = "Ask AI Chatter Request"
    _order = "create_date desc"

    uuid = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        default="queued",
        required=True,
        index=True,
    )

    model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)

    question = fields.Text(required=True)
    response = fields.Text()
    error = fields.Text()

    requested_by = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        required=True,
    )
    source_message_id = fields.Many2one("mail.message", string="Trigger Message")

    payload_json = fields.Text(readonly=True)
    response_json = fields.Text(readonly=True)

    @api.model
    def _cfg(self):
        """Get configuration from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "enabled": ICP.get_param("ipai_ask_ai_chatter.enabled", "False") == "True",
            "api_url": ICP.get_param("ipai_ask_ai_chatter.api_url", ""),
            "api_key": ICP.get_param("ipai_ask_ai_chatter.api_key", ""),
            "trigger": ICP.get_param("ipai_ask_ai_chatter.trigger", "@askai"),
            "context_n": int(
                ICP.get_param("ipai_ask_ai_chatter.context_messages", "12")
            ),
            "timeout": int(ICP.get_param("ipai_ask_ai_chatter.timeout_seconds", "30")),
        }

    @api.model
    def create_from_message(self, message, question_text):
        """Create a request from a chatter message and enqueue the job."""
        cfg = self._cfg()
        req = self.create(
            {
                "model": message.model,
                "res_id": message.res_id,
                "question": question_text.strip(),
                "requested_by": self.env.user.id,
                "source_message_id": message.id,
                "state": "queued",
            }
        )
        # Enqueue job via OCA queue_job
        req.with_delay(description=f"Ask AI: {req.model},{req.res_id}")._run_job()
        return req

    def _build_context(self):
        """Build context payload for the external executor."""
        self.ensure_one()
        cfg = self._cfg()
        record = self.env[self.model].browse(self.res_id).sudo()
        msgs = (
            self.env["mail.message"]
            .sudo()
            .search(
                [
                    ("model", "=", self.model),
                    ("res_id", "=", self.res_id),
                    ("message_type", "=", "comment"),
                ],
                order="date desc",
                limit=cfg["context_n"],
            )
        )
        messages = []
        for m in reversed(msgs):
            messages.append(
                {
                    "author": (m.author_id.name or "") if m.author_id else "",
                    "date": fields.Datetime.to_string(m.date) if m.date else "",
                    "body": html2plaintext(m.body or ""),
                }
            )
        return record, messages

    def _post_answer(self, record, answer_text, citations=None):
        """Post the AI answer back to the record's chatter."""
        self.ensure_one()
        body = "<div><b>Ask AI</b></div>"
        body += f"<div>{answer_text}</div>"
        if citations:
            body += "<hr/><div><b>Citations</b></div><ul>"
            for c in citations:
                body += f"<li>{c}</li>"
            body += "</ul>"
        record.message_post(body=body, subtype_xmlid="mail.mt_comment")

    def _run_job(self):
        """Execute the AI request (called by queue_job)."""
        self.ensure_one()
        cfg = self._cfg()

        if not cfg["enabled"]:
            self.write({"state": "error", "error": "Ask AI is disabled in settings."})
            return

        if not cfg["api_url"]:
            self.write({"state": "error", "error": "Ask AI API URL is not configured."})
            return

        self.write({"state": "running", "error": False})

        try:
            record, messages = self._build_context()
            base_url = (
                self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
            )

            payload = {
                "request_id": self.uuid,
                "question": self.question,
                "record": {
                    "model": self.model,
                    "id": self.res_id,
                    "display_name": record.display_name if record else "",
                    "url": (
                        f"{base_url}/web#id={self.res_id}&model={self.model}"
                        if base_url
                        else ""
                    ),
                },
                "context": {"messages": messages},
                "user": {
                    "id": self.requested_by.id,
                    "name": self.requested_by.name,
                    "email": self.requested_by.email,
                },
                "meta": {
                    "db": self.env.cr.dbname,
                    "source_message_id": (
                        self.source_message_id.id if self.source_message_id else None
                    ),
                },
            }

            headers = {"Content-Type": "application/json"}
            if cfg["api_key"]:
                headers["Authorization"] = f"Bearer {cfg['api_key']}"

            self.payload_json = json.dumps(payload, ensure_ascii=False)

            resp = requests.post(
                cfg["api_url"],
                data=self.payload_json,
                headers=headers,
                timeout=cfg["timeout"],
            )
            resp.raise_for_status()
            data = resp.json() if resp.content else {}

            answer = (data.get("answer") or "").strip()
            citations = data.get("citations") or []

            self.response_json = json.dumps(data, ensure_ascii=False)
            self.response = answer
            self.state = "done"

            if record and answer:
                self._post_answer(record, answer, citations=citations)

        except Exception as e:
            _logger.exception("Ask AI request failed: %s", self.uuid)
            self.write({"state": "error", "error": str(e)})
