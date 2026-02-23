{
    "name": "IPAI AI Copilot (Discuss Bot)",
    "version": "19.0.1.0.0",
    "summary": "Path A: AI chat via Odoo Discuss — no OWL widget. "
               "Posts in #ai-copilot are answered by an Ollama-backed bot. "
               "Inference backend: ai_oca_native_generate_ollama.",
    "description": """
IPAI AI Copilot (Discuss)
==========================

Implements 'Path A' AI chat: an internal-users-only Discuss channel
(#ai-copilot) backed by the already-installed OCA Ollama connector.

Architecture:
  User posts in #ai-copilot  →  discuss.channel._message_post_after_hook
  → ollama.Client (same config params as OCA AI module)
  → Bot user posts response back into channel

Governance:
  - OCA AI module provides inference backend (no custom inference logic here)
  - This module is a thin integration bridge (ipai_* SSOT rule)
  - Prompts logged to ops.platform_events via Supabase Edge Function (async)
  - Secrets: only Ollama connection URL stored in ir.config_parameter (no keys)

Configuration:
  Required ir.config_parameter values (set by OCA module install or manually):
    ai_oca_native_generate_ollama.connection   — Ollama base URL
    ai_oca_native_generate_ollama.model        — model name (e.g. llama3.2)
    ai_oca_native_generate_ollama.headers      — optional JSON dict

  This module adds:
    ipai_ai_copilot.channel_xmlid              — XML ID of the copilot channel
    """,
    "category": "Discuss",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "depends": [
        "mail",
        "ai_oca_native_generate_ollama",
    ],
    "data": [
        "data/res_partner_bot.xml",
        "data/mail_channel_ai.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {"python": ["ollama"]},
}
