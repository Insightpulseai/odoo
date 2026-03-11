"""
InsightPulseAI Platform SDK - Type Definitions
Phase 5B: SaaS Platform Kit - SDK Creation
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AIErrorCode(str, Enum):
    """SDK error types"""

    CONFIG_ERROR = "CONFIG_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class AIError(Exception):
    """SDK error class"""

    def __init__(
        self,
        code: AIErrorCode,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable"""
        return self.code in [
            AIErrorCode.NETWORK_ERROR,
            AIErrorCode.SERVICE_UNAVAILABLE,
            AIErrorCode.RATE_LIMIT_ERROR,
        ]


@dataclass
class ContextSource:
    """Context source metadata"""

    chunk_id: str
    document_title: str
    similarity: float
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AskQuestionResponse:
    """AI question response"""

    answer: str
    sources: List[ContextSource]
    confidence: float
    question_id: str
    tokens_used: Optional[int] = None


@dataclass
class HealthCheckResponse:
    """Health check response"""

    configured: bool
    edge_function: bool
    openai_fallback: bool
    org_id: Optional[str] = None
    test_result: Optional[str] = None
    edge_function_status: Optional[Any] = None
    error: Optional[str] = None
