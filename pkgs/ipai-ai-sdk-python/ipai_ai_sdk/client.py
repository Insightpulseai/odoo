"""
InsightPulseAI Platform SDK - AI Client
Phase 5B: SaaS Platform Kit - SDK Creation

Python client for InsightPulseAI AI services.

Example:
    ```python
    from ipai_ai_sdk import AIClient

    client = AIClient(
        supabase_url='https://PROJECT.supabase.co',
        api_key='your-api-key'
    )

    result = client.ask_question('What is RAG?')
    print(result.answer)
    ```
"""

import json
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from .types import (
    AIError,
    AIErrorCode,
    AskQuestionResponse,
    ContextSource,
    HealthCheckResponse,
)


class AIClient:
    """InsightPulseAI AI Client"""

    def __init__(
        self,
        supabase_url: str,
        api_key: str,
        default_org_id: Optional[str] = None,
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        Create AI client instance

        Args:
            supabase_url: Supabase project URL
            api_key: Anon key (frontend) or service role key (backend)
            default_org_id: Default organization UUID
            timeout: Request timeout in seconds (default: 30)
            debug: Enable debug logging (default: False)

        Raises:
            AIError: If configuration is invalid
        """
        # Validate configuration
        if not supabase_url or not supabase_url.strip():
            raise AIError(AIErrorCode.CONFIG_ERROR, "Supabase URL is required")

        if not api_key or not api_key.strip():
            raise AIError(AIErrorCode.CONFIG_ERROR, "API key is required")

        # Validate URL format
        if "supabase.co" not in supabase_url and "localhost" not in supabase_url:
            raise AIError(AIErrorCode.CONFIG_ERROR, "Invalid Supabase URL format")

        self.supabase_url = supabase_url.rstrip("/")
        self.api_key = api_key
        self.default_org_id = default_org_id
        self.timeout = timeout
        self.debug = debug

        self._log("Client initialized", {"supabase_url": self.supabase_url})

    def ask_question(
        self,
        question: str,
        org_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_chunks: int = 5,
    ) -> AskQuestionResponse:
        """
        Ask a question to the AI service

        Args:
            question: Question text
            org_id: Organization UUID (optional, uses default)
            filters: Filter context by metadata (optional)
            max_chunks: Maximum context chunks to retrieve (default: 5)

        Returns:
            AskQuestionResponse: AI response with answer and sources

        Raises:
            AIError: If request fails
        """
        self._log("ask_question called", {"question": question[:100]})

        # Validate question
        if not question or not question.strip():
            raise AIError(AIErrorCode.INVALID_REQUEST, "Question text is required")

        # Build request body
        body = {
            "question": question.strip(),
            "org_id": org_id or self.default_org_id,
            "filters": filters or {},
            "max_chunks": max_chunks,
        }

        # Call Edge Function
        try:
            url = urljoin(self.supabase_url, "/functions/v1/docs-ai-ask")
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=self.timeout,
            )

            # Handle non-OK responses
            if not response.ok:
                raise self._parse_http_error(response)

            # Parse response
            data = response.json()

            result = AskQuestionResponse(
                answer=data["answer"],
                sources=[
                    ContextSource(
                        chunk_id=s["chunk_id"],
                        document_title=s["document_title"],
                        similarity=s["similarity"],
                        content=s.get("content"),
                        metadata=s.get("metadata"),
                    )
                    for s in data["sources"]
                ],
                confidence=data["confidence"],
                question_id=data["question_id"],
                tokens_used=data.get("tokens_used"),
            )

            self._log(
                "ask_question success",
                {
                    "answer_length": len(result.answer),
                    "sources_count": len(result.sources),
                    "confidence": result.confidence,
                },
            )

            return result

        except requests.exceptions.Timeout:
            raise AIError(
                AIErrorCode.NETWORK_ERROR,
                "Request timeout - AI service took too long to respond",
            )

        except requests.exceptions.ConnectionError as e:
            raise AIError(AIErrorCode.NETWORK_ERROR, f"Network error: {str(e)}")

        except requests.exceptions.RequestException as e:
            raise AIError(AIErrorCode.UNKNOWN_ERROR, f"Request error: {str(e)}")

        except (KeyError, ValueError) as e:
            raise AIError(
                AIErrorCode.UNKNOWN_ERROR, f"Invalid response format: {str(e)}"
            )

    def health_check(self) -> HealthCheckResponse:
        """
        Check AI service health and configuration

        Returns:
            HealthCheckResponse: Health check status
        """
        self._log("health_check called")

        try:
            url = urljoin(self.supabase_url, "/functions/v1/docs-ai-ask")
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"question": "health check"},
                timeout=10,  # Shorter timeout for health check
            )

            return HealthCheckResponse(
                configured=True,
                edge_function=response.ok,
                openai_fallback=False,  # Unknown from client side
                edge_function_status=response.status_code,
                test_result=(
                    "Edge Function reachable"
                    if response.ok
                    else f"HTTP {response.status_code}: {response.reason}"
                ),
            )

        except requests.exceptions.Timeout:
            return HealthCheckResponse(
                configured=True,
                edge_function=False,
                openai_fallback=False,
                edge_function_status="UNREACHABLE",
                test_result="Edge Function unreachable - check network or deployment",
            )

        except requests.exceptions.RequestException as e:
            return HealthCheckResponse(
                configured=False,
                edge_function=False,
                openai_fallback=False,
                error=f"Network error: {str(e)}",
            )

    def _parse_http_error(self, response: requests.Response) -> AIError:
        """Parse HTTP error response and create AIError"""
        status_code = response.status_code

        # Map HTTP status to error code
        if status_code == 400:
            code = AIErrorCode.INVALID_REQUEST
            message = "Invalid request parameters"
        elif status_code in (401, 403):
            code = AIErrorCode.AUTH_ERROR
            message = "Authentication failed - check API key"
        elif status_code == 404:
            code = AIErrorCode.SERVICE_UNAVAILABLE
            message = "AI service not found - Edge Function may not be deployed"
        elif status_code == 429:
            code = AIErrorCode.RATE_LIMIT_ERROR
            message = "Rate limit exceeded - try again later"
        elif status_code >= 500:
            code = AIErrorCode.SERVICE_UNAVAILABLE
            message = "AI service temporarily unavailable"
        else:
            code = AIErrorCode.UNKNOWN_ERROR
            message = f"HTTP {status_code}: {response.reason}"

        # Try to parse error details from body
        details = None
        try:
            body = response.text
            if body:
                details = json.loads(body)
                # Supabase Edge Function error format
                if isinstance(details, dict) and "message" in details:
                    message = details["message"]
        except (json.JSONDecodeError, ValueError):
            pass

        return AIError(code, message, status_code, details)

    def _log(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Debug logging"""
        if self.debug:
            print(f"[IPAI AI SDK] {message}", data or "")
