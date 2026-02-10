"""
InsightPulseAI Platform SDK - Python
Phase 5B: SaaS Platform Kit - SDK Creation
"""

from .client import AIClient
from .types import (
    AskQuestionResponse,
    ContextSource,
    HealthCheckResponse,
    AIError,
    AIErrorCode,
)

__version__ = "0.1.0"
__all__ = [
    "AIClient",
    "AskQuestionResponse",
    "ContextSource",
    "HealthCheckResponse",
    "AIError",
    "AIErrorCode",
]
