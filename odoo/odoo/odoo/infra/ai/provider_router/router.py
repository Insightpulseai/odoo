"""
AI Provider Router - Main routing logic

Provides unified interface to multiple LLM providers with automatic failover.
"""

import os
import time
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prevent logging of sensitive data
class SecureFormatter(logging.Formatter):
    """Formatter that redacts API keys from log messages"""
    REDACT_PATTERNS = ['api_key', 'API_KEY', 'token', 'TOKEN', 'password', 'PASSWORD']

    def format(self, record):
        msg = super().format(record)
        for pattern in self.REDACT_PATTERNS:
            if pattern in msg:
                msg = msg.replace(pattern, '***REDACTED***')
        return msg

logger.handlers[0].setFormatter(SecureFormatter())


class Provider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class AIError(Exception):
    """Base exception for AI provider errors"""
    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ProviderRouter:
    """
    Multi-provider AI router with automatic failover and retry logic.

    Environment Variables:
        IPAI_AI_PROVIDER: Primary provider (openai, gemini, anthropic, ollama)
        AI_PROVIDER_PRIMARY: Override primary provider
        AI_PROVIDER_SECONDARY: Secondary failover provider
        AI_PROVIDER_TERTIARY: Tertiary failover provider
        AI_PROVIDER_RETRY_ATTEMPTS: Retry attempts per provider (default: 3)
        AI_PROVIDER_RETRY_DELAY: Delay between retries in seconds (default: 2)

        # OpenAI
        IPAI_LLM_API_KEY: OpenAI API key
        IPAI_LLM_BASE_URL: OpenAI base URL (default: https://api.openai.com/v1)
        IPAI_LLM_MODEL: Default model (default: gpt-4o-mini)
        IPAI_LLM_TEMPERATURE: Temperature (default: 0.2)
        IPAI_LLM_MAX_TOKENS: Max tokens (default: 4096)
        IPAI_LLM_TIMEOUT: Request timeout (default: 30)

        # Gemini
        GEMINI_API_KEY: Google Gemini API key
        GEMINI_MODEL: Model name (default: gemini-1.5-flash)
        GEMINI_API_BASE_URL: Base URL

        # Anthropic
        ANTHROPIC_API_KEY: Anthropic API key
        ANTHROPIC_MODEL: Model name (default: claude-3-5-sonnet-20241022)
        ANTHROPIC_API_BASE_URL: Base URL

        # Ollama
        OLLAMA_BASE_URL: Ollama base URL (default: http://localhost:11434)
        OLLAMA_MODEL: Model name (default: llama3.1:8b)
    """

    def __init__(self):
        self.primary_provider = self._get_primary_provider()
        self.secondary_provider = self._get_secondary_provider()
        self.tertiary_provider = self._get_tertiary_provider()
        self.retry_attempts = int(os.getenv('AI_PROVIDER_RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.getenv('AI_PROVIDER_RETRY_DELAY', '2'))

        logger.info(f"Initialized AI Provider Router: primary={self.primary_provider}, "
                   f"secondary={self.secondary_provider}, tertiary={self.tertiary_provider}")

    def _get_primary_provider(self) -> Provider:
        """Get primary provider from environment"""
        provider_str = os.getenv('AI_PROVIDER_PRIMARY') or \
                      os.getenv('IPAI_AI_PROVIDER') or \
                      'openai'
        return Provider(provider_str.lower())

    def _get_secondary_provider(self) -> Optional[Provider]:
        """Get secondary failover provider"""
        provider_str = os.getenv('AI_PROVIDER_SECONDARY')
        return Provider(provider_str.lower()) if provider_str else None

    def _get_tertiary_provider(self) -> Optional[Provider]:
        """Get tertiary failover provider"""
        provider_str = os.getenv('AI_PROVIDER_TERTIARY')
        return Provider(provider_str.lower()) if provider_str else None

    def call_ai(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        meta: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Call AI provider with automatic failover.

        Args:
            prompt: The prompt to send to the AI
            model: Override default model for provider
            temperature: Override default temperature (0.0-2.0)
            max_tokens: Override default max tokens
            json_mode: Request structured JSON output
            meta: Additional metadata for the request

        Returns:
            AIResponse with content, model, provider, tokens, latency, metadata

        Raises:
            AIError: If all providers fail
        """
        providers = [p for p in [self.primary_provider, self.secondary_provider, self.tertiary_provider] if p]

        last_error = None
        for provider in providers:
            try:
                logger.info(f"Attempting provider: {provider.value}")
                return self._call_provider(
                    provider=provider,
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                    meta=meta or {}
                )
            except AIError as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                last_error = e
                continue

        # All providers failed
        raise AIError(
            f"All providers failed. Last error: {last_error}",
            provider="all",
            original_error=last_error
        )

    def _call_provider(
        self,
        provider: Provider,
        prompt: str,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool,
        meta: Dict[str, Any]
    ) -> AIResponse:
        """Call specific provider with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                start_time = time.time()

                if provider == Provider.OPENAI:
                    response = self._call_openai(prompt, model, temperature, max_tokens, json_mode)
                elif provider == Provider.GEMINI:
                    response = self._call_gemini(prompt, model, temperature, max_tokens, json_mode)
                elif provider == Provider.ANTHROPIC:
                    response = self._call_anthropic(prompt, model, temperature, max_tokens, json_mode)
                elif provider == Provider.OLLAMA:
                    response = self._call_ollama(prompt, model, temperature, max_tokens, json_mode)
                else:
                    raise AIError(f"Unsupported provider: {provider}", provider=provider.value)

                latency_ms = int((time.time() - start_time) * 1000)

                return AIResponse(
                    content=response['content'],
                    model=response['model'],
                    provider=provider.value,
                    tokens_used=response.get('tokens', 0),
                    latency_ms=latency_ms,
                    metadata={**meta, **response.get('metadata', {})}
                )

            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for {provider.value}, retrying in {self.retry_delay}s")
                    time.sleep(self.retry_delay)
                else:
                    raise AIError(f"Max retries exceeded: {str(e)}", provider=provider.value, original_error=e)

    def _call_openai(
        self,
        prompt: str,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            import openai
        except ImportError:
            raise AIError("openai package not installed. Run: pip install openai", provider="openai")

        api_key = os.getenv('IPAI_LLM_API_KEY')
        if not api_key:
            raise AIError("IPAI_LLM_API_KEY not set", provider="openai")

        base_url = os.getenv('IPAI_LLM_BASE_URL', 'https://api.openai.com/v1')
        model = model or os.getenv('IPAI_LLM_MODEL', 'gpt-4o-mini')
        temperature = temperature if temperature is not None else float(os.getenv('IPAI_LLM_TEMPERATURE', '0.2'))
        max_tokens = max_tokens or int(os.getenv('IPAI_LLM_MAX_TOKENS', '4096'))
        timeout = int(os.getenv('IPAI_LLM_TIMEOUT', '30'))

        client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

        kwargs = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': temperature,
            'max_tokens': max_tokens,
        }

        if json_mode:
            kwargs['response_format'] = {'type': 'json_object'}

        response = client.chat.completions.create(**kwargs)

        return {
            'content': response.choices[0].message.content,
            'model': response.model,
            'tokens': response.usage.total_tokens if response.usage else 0,
            'metadata': {
                'finish_reason': response.choices[0].finish_reason,
                'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'completion_tokens': response.usage.completion_tokens if response.usage else 0,
            }
        }

    def _call_gemini(
        self,
        prompt: str,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise AIError("google-generativeai package not installed. Run: pip install google-generativeai", provider="gemini")

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise AIError("GEMINI_API_KEY not set", provider="gemini")

        genai.configure(api_key=api_key)

        model_name = model or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        temperature = temperature if temperature is not None else float(os.getenv('IPAI_LLM_TEMPERATURE', '0.2'))
        max_tokens = max_tokens or int(os.getenv('IPAI_LLM_MAX_TOKENS', '4096'))

        generation_config = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
        }

        if json_mode:
            generation_config['response_mime_type'] = 'application/json'

        model_instance = genai.GenerativeModel(model_name, generation_config=generation_config)
        response = model_instance.generate_content(prompt)

        return {
            'content': response.text,
            'model': model_name,
            'tokens': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
            'metadata': {
                'finish_reason': response.candidates[0].finish_reason if response.candidates else None,
                'prompt_tokens': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                'completion_tokens': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
            }
        }

    def _call_anthropic(
        self,
        prompt: str,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        try:
            import anthropic
        except ImportError:
            raise AIError("anthropic package not installed. Run: pip install anthropic", provider="anthropic")

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise AIError("ANTHROPIC_API_KEY not set", provider="anthropic")

        model_name = model or os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        temperature = temperature if temperature is not None else float(os.getenv('IPAI_LLM_TEMPERATURE', '0.2'))
        max_tokens = max_tokens or int(os.getenv('IPAI_LLM_MAX_TOKENS', '4096'))

        client = anthropic.Anthropic(api_key=api_key)

        system_message = ""
        if json_mode:
            system_message = "You must respond with valid JSON only. Do not include any text outside the JSON structure."

        response = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else anthropic.NOT_GIVEN,
            messages=[{'role': 'user', 'content': prompt}]
        )

        return {
            'content': response.content[0].text,
            'model': response.model,
            'tokens': response.usage.input_tokens + response.usage.output_tokens,
            'metadata': {
                'finish_reason': response.stop_reason,
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
            }
        }

    def _call_ollama(
        self,
        prompt: str,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call Ollama (local) API"""
        try:
            import requests
        except ImportError:
            raise AIError("requests package not installed. Run: pip install requests", provider="ollama")

        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model_name = model or os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        temperature = temperature if temperature is not None else float(os.getenv('IPAI_LLM_TEMPERATURE', '0.2'))

        url = f"{base_url}/api/generate"
        payload = {
            'model': model_name,
            'prompt': prompt,
            'temperature': temperature,
            'stream': False,
        }

        if json_mode:
            payload['format'] = 'json'

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        return {
            'content': data['response'],
            'model': model_name,
            'tokens': data.get('eval_count', 0) + data.get('prompt_eval_count', 0),
            'metadata': {
                'finish_reason': 'stop',
                'prompt_tokens': data.get('prompt_eval_count', 0),
                'completion_tokens': data.get('eval_count', 0),
            }
        }


# Module-level convenience function
_router = None

def call_ai(
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    json_mode: bool = False,
    meta: Optional[Dict[str, Any]] = None
) -> AIResponse:
    """
    Convenience function for calling AI with automatic provider routing.

    This is the recommended entry point for simple usage.

    Example:
        >>> from provider_router import call_ai
        >>> response = call_ai("What is 2+2?")
        >>> print(response.content)
        "4"

        >>> # With JSON mode
        >>> response = call_ai(
        ...     "List 3 programming languages as JSON",
        ...     json_mode=True
        ... )
        >>> print(response.content)
        {"languages": ["Python", "JavaScript", "Go"]}
    """
    global _router
    if _router is None:
        _router = ProviderRouter()

    return _router.call_ai(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=json_mode,
        meta=meta
    )
