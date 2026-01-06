# -*- coding: utf-8 -*-
"""
IPAI AI Provider Service.

Provides unified interface for multiple AI providers through Pulser gateway.
"""
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiAiProvider(models.AbstractModel):
    """
    AI Provider Service.

    Routes AI requests to configured providers through Pulser gateway
    or directly to provider APIs.
    """

    _name = "ipai.ai.provider"
    _description = "IPAI AI Provider Service"

    # Provider configurations
    PROVIDERS = {
        "openai": {
            "name": "OpenAI",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        },
        "anthropic": {
            "name": "Anthropic",
            "endpoint": "https://api.anthropic.com/v1/messages",
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "auth_header": "x-api-key",
            "auth_prefix": "",
        },
        "azure": {
            "name": "Azure OpenAI",
            "endpoint": None,  # Configured per-deployment
            "models": ["gpt-4", "gpt-35-turbo"],
            "auth_header": "api-key",
            "auth_prefix": "",
        },
        "pulser": {
            "name": "Pulser Gateway",
            "endpoint": None,  # Configured via system param
            "models": ["auto"],  # Gateway handles model selection
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        },
    }

    @api.model
    def get_config(self, key, default=""):
        """Get configuration value from system parameters."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(f"ipai_ai.{key}", default)
        )

    @api.model
    def get_provider_name(self):
        """Get configured provider name."""
        return self.get_config("default_provider", "openai")

    @api.model
    def get_model_name(self):
        """Get configured model name."""
        return self.get_config("default_model", "gpt-4")

    @api.model
    def get_api_key(self, provider=None):
        """Get API key for provider."""
        provider = provider or self.get_provider_name()
        return self.get_config(f"{provider}_api_key", "")

    @api.model
    def get_endpoint(self, provider=None):
        """Get endpoint for provider."""
        provider = provider or self.get_provider_name()

        # Check for custom endpoint first
        custom = self.get_config(f"{provider}_endpoint", "")
        if custom:
            return custom

        # Use Pulser gateway if configured
        pulser_endpoint = self.get_config("pulser_endpoint", "")
        if pulser_endpoint:
            return pulser_endpoint

        # Fall back to provider default
        provider_config = self.PROVIDERS.get(provider, {})
        return provider_config.get("endpoint", "")

    @api.model
    def generate(self, messages, **kwargs):
        """
        Generate AI response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters:
                - model: Model to use (optional)
                - temperature: Sampling temperature (default: 0.7)
                - max_tokens: Maximum tokens (default: 1000)
                - provider: Provider to use (optional)

        Returns:
            dict: {
                'success': bool,
                'response': str,
                'tokens_used': int,
                'model': str,
                'provider': str,
                'latency': float,
                'error': str (if failed),
                'request_hash': str,
            }
        """
        provider = kwargs.get("provider") or self.get_provider_name()
        model = kwargs.get("model") or self.get_model_name()
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        start_time = time.time()

        # Generate request hash for caching/deduplication
        request_hash = self._hash_request(messages, model)

        try:
            if provider == "pulser":
                result = self._generate_pulser(messages, model, temperature, max_tokens)
            elif provider == "openai":
                result = self._generate_openai(messages, model, temperature, max_tokens)
            elif provider == "anthropic":
                result = self._generate_anthropic(messages, model, temperature, max_tokens)
            elif provider == "azure":
                result = self._generate_azure(messages, model, temperature, max_tokens)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown provider: {provider}",
                }

            result["latency"] = time.time() - start_time
            result["provider"] = provider
            result["request_hash"] = request_hash

            return result

        except Exception as e:
            _logger.error("AI generation error (%s): %s", provider, str(e))
            return {
                "success": False,
                "error": str(e),
                "latency": time.time() - start_time,
                "provider": provider,
                "request_hash": request_hash,
            }

    @api.model
    def _hash_request(self, messages, model):
        """Generate hash for request deduplication."""
        content = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @api.model
    def _generate_pulser(self, messages, model, temperature, max_tokens):
        """Generate via Pulser gateway."""
        import requests

        endpoint = self.get_endpoint("pulser")
        api_key = self.get_api_key("pulser")

        if not endpoint:
            return {"success": False, "error": "Pulser endpoint not configured"}

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("content") or data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "model": data.get("model", model),
            }
        else:
            return {
                "success": False,
                "error": f"Pulser API error: {response.status_code} - {response.text[:200]}",
            }

    @api.model
    def _generate_openai(self, messages, model, temperature, max_tokens):
        """Generate via OpenAI API."""
        import requests

        endpoint = self.get_endpoint("openai") or self.PROVIDERS["openai"]["endpoint"]
        api_key = self.get_api_key("openai")

        if not api_key:
            return {"success": False, "error": "OpenAI API key not configured"}

        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data["choices"][0]["message"]["content"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "model": model,
            }
        else:
            return {
                "success": False,
                "error": f"OpenAI API error: {response.status_code}",
            }

    @api.model
    def _generate_anthropic(self, messages, model, temperature, max_tokens):
        """Generate via Anthropic API."""
        import requests

        endpoint = self.get_endpoint("anthropic") or self.PROVIDERS["anthropic"]["endpoint"]
        api_key = self.get_api_key("anthropic")

        if not api_key:
            return {"success": False, "error": "Anthropic API key not configured"}

        # Convert OpenAI message format to Anthropic format
        system_message = None
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
        }
        if system_message:
            payload["system"] = system_message

        response = requests.post(
            endpoint,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json=payload,
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [{}])
            text = content[0].get("text", "") if content else ""
            return {
                "success": True,
                "response": text,
                "tokens_used": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                "model": model,
            }
        else:
            return {
                "success": False,
                "error": f"Anthropic API error: {response.status_code}",
            }

    @api.model
    def _generate_azure(self, messages, model, temperature, max_tokens):
        """Generate via Azure OpenAI API."""
        import requests

        endpoint = self.get_endpoint("azure")
        api_key = self.get_api_key("azure")

        if not endpoint:
            return {"success": False, "error": "Azure endpoint not configured"}
        if not api_key:
            return {"success": False, "error": "Azure API key not configured"}

        # Azure endpoint includes deployment name
        url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"

        response = requests.post(
            url,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data["choices"][0]["message"]["content"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                "model": f"azure/{model}",
            }
        else:
            return {
                "success": False,
                "error": f"Azure API error: {response.status_code}",
            }

    @api.model
    def complete_text(self, prompt, **kwargs):
        """
        Simple text completion interface.

        Args:
            prompt: Text prompt
            **kwargs: Additional parameters passed to generate()

        Returns:
            str: Generated text or empty string on error
        """
        result = self.generate(
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return result.get("response", "") if result.get("success") else ""

    @api.model
    def chat(self, user_message, system_prompt=None, history=None, **kwargs):
        """
        Chat interface with optional history.

        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            history: List of previous messages
            **kwargs: Additional parameters

        Returns:
            dict: Generation result
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        return self.generate(messages, **kwargs)
