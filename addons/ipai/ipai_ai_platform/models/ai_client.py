"""AI Platform HTTP Client - Odoo Backend Integration

Phase 5A: SaaS Platform Kit - AI × Odoo Integration

Provides HTTP client for calling AI services from Odoo backend workflows.

Fallback Strategy:
- Primary: Supabase Edge Function (docs-ai-ask) when available
- Fallback: Direct OpenAI API calls when Edge Function unavailable

Usage:
    # Simple question
    result = env['ai.client'].ask_question("What is RAG?")

    # With context filters
    result = env['ai.client'].ask_question(
        "How to setup billing?",
        context_filters={'category': 'billing'}
    )

Configuration:
    System Parameters:
    - ipai.supabase.url: https://PROJECT.supabase.co
    - ipai.supabase.service_role_key: Service role key
    - ipai.org.id: Organization UUID for multi-tenant scoping
    - ipai.openai.api_key: OpenAI API key (fallback)
"""

import json
import logging
from datetime import datetime

import requests
from odoo.exceptions import UserError

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class AIClient(models.AbstractModel):
    """AI Platform HTTP Client for backend AI operations"""

    _name = "ai.client"
    _description = "AI Platform HTTP Client"

    def _get_supabase_config(self):
        """Fetch Supabase configuration from system parameters

        Returns:
            dict: {
                'url': Supabase project URL,
                'key': Service role key,
                'org_id': Default organization UUID
            }

        Raises:
            UserError: If required configuration is missing
        """
        ICP = self.env["ir.config_parameter"].sudo()
        config = {
            "url": ICP.get_param("ipai.supabase.url"),
            "key": ICP.get_param("ipai.supabase.service_role_key"),
            "org_id": ICP.get_param("ipai.org.id"),
            "openai_key": ICP.get_param("ipai.openai.api_key"),
        }

        # Validate required fields
        if not config["url"]:
            raise UserError(
                _(
                    "Supabase URL not configured. "
                    "Set 'ipai.supabase.url' in Settings → Technical → System Parameters"
                )
            )

        # Edge Function requires service role key
        if not config["key"] and not config["openai_key"]:
            raise UserError(
                _(
                    "Neither Supabase service role key nor OpenAI API key configured. "
                    "Set 'ipai.supabase.service_role_key' or 'ipai.openai.api_key' "
                    "in Settings → Technical → System Parameters"
                )
            )

        return config

    def ask_question(self, question, context_filters=None, max_chunks=5, org_id=None):
        """Ask a question to the AI service

        Args:
            question (str): Question text
            context_filters (dict, optional): Filter context by metadata
            max_chunks (int): Maximum context chunks to retrieve
            org_id (str, optional): Organization UUID for scoping

        Returns:
            dict: {
                'answer': str,
                'sources': list of dicts,
                'confidence': float,
                'question_id': str (if Edge Function used)
            }

        Raises:
            UserError: If service unavailable or configuration invalid
        """
        config = self._get_supabase_config()
        org_id = org_id or config["org_id"]

        # Try Edge Function first (if service role key exists)
        if config["key"]:
            try:
                return self._ask_via_edge_function(
                    question, context_filters, max_chunks, org_id, config
                )
            except requests.exceptions.RequestException as e:
                _logger.warning(
                    "Edge Function unavailable, falling back to OpenAI API: %s", str(e)
                )

        # Fallback to direct OpenAI API
        if config["openai_key"]:
            return self._ask_via_openai(question, config)

        raise UserError(
            _(
                "AI service unavailable. "
                "Configure Supabase Edge Function or OpenAI API key."
            )
        )

    def _ask_via_edge_function(
        self, question, context_filters, max_chunks, org_id, config
    ):
        """Call Supabase Edge Function (docs-ai-ask)

        Args:
            question (str): Question text
            context_filters (dict): Filter context by metadata
            max_chunks (int): Maximum context chunks
            org_id (str): Organization UUID
            config (dict): Supabase configuration

        Returns:
            dict: AI response with answer, sources, confidence

        Raises:
            requests.exceptions.RequestException: If Edge Function call fails
        """
        response = requests.post(
            f"{config['url']}/functions/v1/docs-ai-ask",
            headers={
                "Authorization": f"Bearer {config['key']}",
                "Content-Type": "application/json",
            },
            json={
                "question": question,
                "org_id": org_id,
                "filters": context_filters or {},
                "max_chunks": max_chunks,
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        # Log to audit trail
        self._log_artifact("ai_ask_edge", question, result)

        return result

    def _ask_via_openai(self, question, config):
        """Fallback to direct OpenAI API call

        Args:
            question (str): Question text
            config (dict): Configuration with 'openai_key'

        Returns:
            dict: {
                'answer': str,
                'sources': [],
                'confidence': 1.0
            }

        Raises:
            UserError: If OpenAI API call fails
        """
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config['openai_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are InsightPulseAI assistant. "
                                "Provide concise, accurate answers. "
                                "If uncertain, acknowledge limitations."
                            ),
                        },
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            result = {
                "answer": data["choices"][0]["message"]["content"],
                "sources": [],
                "confidence": 1.0,
            }

            # Log to audit trail
            self._log_artifact("ai_ask_openai", question, result)

            return result

        except requests.exceptions.RequestException as e:
            raise UserError(_("OpenAI API unavailable: %s") % str(e))

    def _log_artifact(self, operation, input_data, output_data):
        """Persist AI operation to cms_artifacts table (if exists)

        Args:
            operation (str): Operation type (ai_ask_edge, ai_ask_openai)
            input_data (str): Input question
            output_data (dict): AI response

        Note:
            Gracefully skips if cms.artifact model doesn't exist
        """
        # Check if cms.artifact model exists (Phase 1 migration)
        if "cms.artifact" not in self.env:
            _logger.debug(
                "cms.artifact model not found, skipping audit trail for: %s", operation
            )
            return

        try:
            config = self._get_supabase_config()
            self.env["cms.artifact"].sudo().create(
                {
                    "org_id": config.get("org_id"),
                    "artifact_type": "ai_operation",
                    "metadata": json.dumps(
                        {
                            "operation": operation,
                            "input": input_data,
                            "output": output_data,
                            "timestamp": datetime.now().isoformat(),
                            "user_id": self.env.user.id,
                            "user_name": self.env.user.name,
                        },
                        indent=2,
                    ),
                }
            )
            _logger.info(
                "AI operation logged: %s for user %s", operation, self.env.user.name
            )
        except Exception as e:
            _logger.warning("Failed to log AI artifact: %s", str(e), exc_info=True)

    @api.model
    def health_check(self):
        """Verify AI service configuration and connectivity

        Returns:
            dict: {
                'configured': bool,
                'edge_function': bool,
                'openai_fallback': bool,
                'org_id': str,
                'test_result': str
            }
        """
        try:
            config = self._get_supabase_config()

            health = {
                "configured": True,
                "edge_function": bool(config.get("key")),
                "openai_fallback": bool(config.get("openai_key")),
                "org_id": config.get("org_id") or "NOT_SET",
            }

            # Test Edge Function if configured
            if health["edge_function"]:
                try:
                    response = requests.post(
                        f"{config['url']}/functions/v1/docs-ai-ask",
                        headers={
                            "Authorization": f"Bearer {config['key']}",
                            "Content-Type": "application/json",
                        },
                        json={"question": "health check"},
                        timeout=10,
                    )
                    health["edge_function_status"] = response.status_code
                    health["test_result"] = "Edge Function reachable"
                except requests.exceptions.RequestException as e:
                    health["edge_function_status"] = "UNREACHABLE"
                    health["test_result"] = f"Edge Function error: {str(e)[:100]}"
            else:
                health["test_result"] = (
                    "Using OpenAI fallback (Edge Function not configured)"
                )

            return health

        except UserError as e:
            return {"configured": False, "error": str(e)}
