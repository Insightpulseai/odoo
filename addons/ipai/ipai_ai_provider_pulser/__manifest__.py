# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Provider - Pulser Gateway",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "AI provider adapter for Pulser/self-hosted AI gateway",
    "description": """
IPAI AI Provider - Pulser Gateway
=================================

Implements a custom AI provider adapter for routing AI requests through
the Pulser gateway or self-hosted AI infrastructure.

Features:
---------
* **Multi-Provider Routing**: Route to OpenAI, Anthropic, Azure, or custom endpoints
* **Request Transformation**: Maps Odoo AI payloads to provider-specific formats
* **Response Handling**: Normalizes responses from different providers
* **Rate Limiting**: Configurable rate limits per provider
* **Fallback Chains**: Automatic fallback to secondary providers

Configuration:
--------------
Set the following system parameters:
- ipai_ai.pulser_endpoint: Gateway URL
- ipai_ai.pulser_api_key: API key for authentication
- ipai_ai.default_provider: Default AI provider (openai, anthropic, azure)
- ipai_ai.default_model: Default model to use

Integration:
------------
Works with OCA/ai bridge modules and IPAI Ask AI for seamless AI integration.

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ai_provider_pulser",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_agent_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/provider_views.xml",
        "data/provider_config.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
