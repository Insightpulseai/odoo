"""
AI Provider Router - Multi-provider LLM abstraction layer

Supports OpenAI, Google Gemini, Anthropic Claude, and Ollama with automatic
failover, retry logic, and structured output modes.
"""

from .router import ProviderRouter, call_ai, AIResponse, AIError

__all__ = ['ProviderRouter', 'call_ai', 'AIResponse', 'AIError']
__version__ = '1.0.0'
