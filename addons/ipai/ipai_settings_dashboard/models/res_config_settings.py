# -*- coding: utf-8 -*-
"""
Unified AI Provider Settings for IPAI.

Consolidates configuration for:
- Kapa RAG (knowledge base retrieval)
- OpenAI / ChatGPT (GPT-4, GPT-4o)
- Google Gemini (Gemini Pro, Vision)
- Ollama (local LLMs)
"""
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # =========================================================================
    # Default Provider Selection
    # =========================================================================
    ipai_default_provider = fields.Selection(
        selection=[
            ("kapa", "Kapa RAG (Knowledge Base)"),
            ("openai", "OpenAI / ChatGPT"),
            ("gemini", "Google Gemini"),
            ("ollama", "Ollama (Local)"),
        ],
        string="Default AI Provider",
        default="openai",
        config_parameter="ipai.default_provider",
        help="Select the default AI provider for all IPAI features",
    )

    # =========================================================================
    # Kapa RAG Configuration
    # =========================================================================
    ipai_kapa_enabled = fields.Boolean(
        string="Enable Kapa RAG",
        config_parameter="ipai.kapa.enabled",
        default=False,
    )
    ipai_kapa_base_url = fields.Char(
        string="Kapa API URL",
        config_parameter="ipai.kapa.base_url",
        default="https://api.kapa.ai",
        help="Base URL for Kapa RAG API",
    )
    ipai_kapa_api_key = fields.Char(
        string="Kapa API Key",
        config_parameter="ipai.kapa.api_key",
        help="Your Kapa API key for authentication",
    )
    ipai_kapa_project_id = fields.Char(
        string="Kapa Project ID",
        config_parameter="ipai.kapa.project_id",
        help="Your Kapa project/knowledge base identifier",
    )
    ipai_kapa_model = fields.Selection(
        selection=[
            ("gpt-4", "GPT-4 (via Kapa)"),
            ("gpt-4-turbo", "GPT-4 Turbo (via Kapa)"),
            ("claude-3", "Claude 3 (via Kapa)"),
        ],
        string="Kapa Backend Model",
        default="gpt-4-turbo",
        config_parameter="ipai.kapa.model",
        help="LLM model used by Kapa for RAG responses",
    )
    ipai_kapa_max_sources = fields.Integer(
        string="Max Sources per Query",
        default=5,
        config_parameter="ipai.kapa.max_sources",
        help="Maximum number of knowledge base sources to retrieve",
    )

    # =========================================================================
    # OpenAI / ChatGPT Configuration
    # =========================================================================
    ipai_openai_enabled = fields.Boolean(
        string="Enable OpenAI",
        config_parameter="ipai.openai.enabled",
        default=False,
    )
    ipai_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter="ipai.openai.api_key",
        help="Your OpenAI API key (starts with sk-)",
    )
    ipai_openai_org_id = fields.Char(
        string="OpenAI Organization ID",
        config_parameter="ipai.openai.org_id",
        help="Optional: OpenAI organization ID for billing",
    )
    ipai_openai_model = fields.Selection(
        selection=[
            ("gpt-4o", "GPT-4o (Latest)"),
            ("gpt-4o-mini", "GPT-4o Mini (Fast)"),
            ("gpt-4-turbo", "GPT-4 Turbo"),
            ("gpt-4", "GPT-4"),
            ("gpt-3.5-turbo", "GPT-3.5 Turbo (Economy)"),
        ],
        string="OpenAI Model",
        default="gpt-4o",
        config_parameter="ipai.openai.model",
    )
    ipai_openai_temperature = fields.Float(
        string="Temperature",
        default=0.7,
        config_parameter="ipai.openai.temperature",
        help="0.0 = deterministic, 1.0 = creative (default: 0.7)",
    )
    ipai_openai_max_tokens = fields.Integer(
        string="Max Tokens",
        default=4096,
        config_parameter="ipai.openai.max_tokens",
        help="Maximum tokens in response",
    )

    # =========================================================================
    # Google Gemini Configuration
    # =========================================================================
    ipai_gemini_enabled = fields.Boolean(
        string="Enable Gemini",
        config_parameter="ipai.gemini.enabled",
        default=False,
    )
    ipai_gemini_api_key = fields.Char(
        string="Gemini API Key",
        config_parameter="ipai.gemini.api_key",
        help="Your Google AI Studio API key",
    )
    ipai_gemini_model = fields.Selection(
        selection=[
            ("gemini-1.5-pro", "Gemini 1.5 Pro (Latest)"),
            ("gemini-1.5-flash", "Gemini 1.5 Flash (Fast)"),
            ("gemini-1.0-pro", "Gemini 1.0 Pro"),
            ("gemini-1.0-pro-vision", "Gemini 1.0 Pro Vision"),
        ],
        string="Gemini Model",
        default="gemini-1.5-pro",
        config_parameter="ipai.gemini.model",
    )
    ipai_gemini_temperature = fields.Float(
        string="Temperature",
        default=0.7,
        config_parameter="ipai.gemini.temperature",
    )
    ipai_gemini_max_tokens = fields.Integer(
        string="Max Output Tokens",
        default=8192,
        config_parameter="ipai.gemini.max_tokens",
    )

    # =========================================================================
    # Ollama (Local) Configuration
    # =========================================================================
    ipai_ollama_enabled = fields.Boolean(
        string="Enable Ollama",
        config_parameter="ipai.ollama.enabled",
        default=False,
    )
    ipai_ollama_base_url = fields.Char(
        string="Ollama Server URL",
        default="http://localhost:11434",
        config_parameter="ipai.ollama.base_url",
        help="URL of your local Ollama server",
    )
    ipai_ollama_model = fields.Char(
        string="Ollama Model",
        default="llama3.1",
        config_parameter="ipai.ollama.model",
        help="Model name (e.g., llama3.1, mistral, codellama)",
    )

    # =========================================================================
    # Email / Notification Settings
    # =========================================================================
    ipai_email_notifications = fields.Boolean(
        string="AI Email Notifications",
        config_parameter="ipai.email.notifications",
        default=True,
        help="Send email notifications for AI task completions",
    )
    ipai_email_digest_frequency = fields.Selection(
        selection=[
            ("realtime", "Real-time"),
            ("hourly", "Hourly Digest"),
            ("daily", "Daily Digest"),
        ],
        string="Notification Frequency",
        default="realtime",
        config_parameter="ipai.email.digest_frequency",
    )

    # =========================================================================
    # RAG / Knowledge Base Settings
    # =========================================================================
    ipai_rag_enabled = fields.Boolean(
        string="Enable RAG Features",
        config_parameter="ipai.rag.enabled",
        default=True,
        help="Enable retrieval-augmented generation for context-aware responses",
    )
    ipai_rag_chunk_size = fields.Integer(
        string="RAG Chunk Size",
        default=1000,
        config_parameter="ipai.rag.chunk_size",
        help="Text chunk size for document indexing",
    )
    ipai_rag_overlap = fields.Integer(
        string="RAG Chunk Overlap",
        default=200,
        config_parameter="ipai.rag.overlap",
        help="Overlap between chunks for context continuity",
    )
    ipai_rag_top_k = fields.Integer(
        string="RAG Top-K Results",
        default=5,
        config_parameter="ipai.rag.top_k",
        help="Number of relevant chunks to retrieve",
    )

    # =========================================================================
    # Actions
    # =========================================================================
    def action_test_openai_connection(self):
        """Test OpenAI API connectivity."""
        self.ensure_one()
        return self.env["ipai.ai.provider.service"].test_provider("openai")

    def action_test_gemini_connection(self):
        """Test Gemini API connectivity."""
        self.ensure_one()
        return self.env["ipai.ai.provider.service"].test_provider("gemini")

    def action_test_kapa_connection(self):
        """Test Kapa RAG API connectivity."""
        self.ensure_one()
        return self.env["ipai.ai.provider.service"].test_provider("kapa")

    def action_test_ollama_connection(self):
        """Test Ollama local server connectivity."""
        self.ensure_one()
        return self.env["ipai.ai.provider.service"].test_provider("ollama")

    def action_open_email_servers(self):
        """Open email server configuration."""
        return {
            "type": "ir.actions.act_window",
            "name": "Outgoing Mail Servers",
            "res_model": "ir.mail_server",
            "view_mode": "list,form",
            "target": "current",
        }

    def action_sync_providers(self):
        """Sync settings to ipai.ai.provider records."""
        self.ensure_one()
        Provider = self.env["ipai.ai.provider"]
        company = self.env.company

        # Sync each enabled provider
        providers_config = [
            ("openai", "OpenAI ChatGPT", self.ipai_openai_enabled),
            ("gemini", "Google Gemini", self.ipai_gemini_enabled),
            ("kapa", "Kapa RAG", self.ipai_kapa_enabled),
            ("ollama", "Ollama Local", self.ipai_ollama_enabled),
        ]

        for ptype, name, enabled in providers_config:
            existing = Provider.search([
                ("company_id", "=", company.id),
                ("provider_type", "=", ptype),
            ], limit=1)

            if enabled and not existing:
                Provider.create({
                    "name": name,
                    "provider_type": ptype,
                    "company_id": company.id,
                    "is_default": ptype == self.ipai_default_provider,
                })
            elif existing:
                existing.write({
                    "active": enabled,
                    "is_default": ptype == self.ipai_default_provider,
                })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Providers Synced",
                "message": "AI provider records updated successfully.",
                "type": "success",
                "sticky": False,
            },
        }
