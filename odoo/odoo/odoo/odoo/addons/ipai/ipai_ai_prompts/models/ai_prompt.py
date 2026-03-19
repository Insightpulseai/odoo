# -*- coding: utf-8 -*-
from odoo import fields, models


class IpaiAiPrompt(models.Model):
    _name = "ipai.ai.prompt"
    _description = "IPAI AI Default Prompt"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    when_users_need_to = fields.Char(
        string="When users need to",
        help="User-facing description of the trigger context",
    )
    instructions = fields.Text(
        required=True,
        help="The default prompt instructions injected into AI context",
    )
    button_prompt = fields.Char(
        string="Button Label",
        help="Primary action label shown on the prompt button (e.g. Rewrite, Summarize)",
    )

    target_context = fields.Selection(
        selection=[
            ("mail_composer", "Mail/Note Composer"),
            ("record_html", "Record HTML Fields"),
            ("text_selector", "Text Selector"),
            ("chatter", "Chatter"),
            ("file_viewer", "File Viewer"),
            ("ask_ai", "Ask AI"),
            ("voice_transcription", "Voice Transcription"),
            ("knowledge_article", "Knowledge Article"),
            ("website_seo", "Website SEO"),
            ("project_summary", "Project Summary"),
        ],
        default="ask_ai",
        required=True,
        string="Context",
        help="Which Odoo surface triggers this prompt",
    )

    agent_id = fields.Many2one(
        comodel_name="ipai.ai.agent",
        string="Agent",
        help="Agent that handles this prompt. Empty = default agent.",
        ondelete="set null",
    )
    topic_id = fields.Many2one(
        comodel_name="ipai.ai.topic",
        string="Topic",
        help="Optional topic scope for this prompt",
        ondelete="set null",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
