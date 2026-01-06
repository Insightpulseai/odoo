# -*- coding: utf-8 -*-
"""
Supabase-backed KB retriever for RAG pipeline.

Expected Supabase RPCs:
- kb.search_chunks(tenant_ref text, query_embedding vector, limit int) -> rows
- kb.search_chunks_text(tenant_ref text, query text, limit int) -> rows (fallback)
"""
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None


@dataclass
class EvidenceChunk:
    """Represents a retrieved evidence chunk."""
    id: Any
    title: Optional[str]
    url: Optional[str]
    content: str
    score: float


class KBRetriever:
    """
    Supabase-backed KB retriever.

    Environment variables:
    - IPAI_SUPABASE_URL: Supabase project URL
    - IPAI_SUPABASE_SERVICE_ROLE_KEY or IPAI_SUPABASE_ANON_KEY: API key
    - IPAI_KB_RPC_EMBEDDING: RPC name for vector search (default: kb.search_chunks)
    - IPAI_KB_RPC_TEXT: RPC name for text search fallback (default: kb.search_chunks_text)
    - IPAI_EMBEDDINGS_PROVIDER: 'openai' to enable embedding computation
    - IPAI_EMBEDDINGS_MODEL: Embedding model name (default: text-embedding-3-small)
    """

    def __init__(self, supabase_url: str, supabase_key: str, rpc_embedding: str, rpc_text: str):
        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_key = supabase_key
        self.rpc_embedding = rpc_embedding
        self.rpc_text = rpc_text

    @classmethod
    def from_env(cls) -> "KBRetriever":
        """Create retriever from environment variables."""
        url = os.environ.get("IPAI_SUPABASE_URL", "").strip()
        key = (
            os.environ.get("IPAI_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("IPAI_SUPABASE_ANON_KEY")
            or ""
        ).strip()
        rpc_embedding = os.environ.get("IPAI_KB_RPC_EMBEDDING", "kb.search_chunks")
        rpc_text = os.environ.get("IPAI_KB_RPC_TEXT", "kb.search_chunks_text")

        if not url or not key:
            _logger.warning("Missing IPAI_SUPABASE_URL or key env vars - retrieval disabled")
            return cls("", "", rpc_embedding, rpc_text)

        return cls(url, key, rpc_embedding, rpc_text)

    def retrieve(self, tenant_ref: str, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Returns list[dict] with: id, title, url, content, score
        """
        if not self.supabase_url or not self.supabase_key:
            _logger.info("Supabase not configured, returning empty evidence")
            return []

        # Try vector search first if embeddings are enabled
        embed = self._maybe_embed(query)
        if embed is not None:
            rows = self._call_rpc(
                self.rpc_embedding,
                {"tenant_ref": tenant_ref, "query_embedding": embed, "limit": limit}
            )
        else:
            # Fall back to text search
            rows = self._call_rpc(
                self.rpc_text,
                {"tenant_ref": tenant_ref, "query": query, "limit": limit}
            )

        out = []
        for r in rows or []:
            out.append({
                "id": r.get("id"),
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content") or "",
                "score": float(r.get("score") or 0.0),
            })
        return out

    def _call_rpc(self, rpc_name: str, payload: Dict[str, Any]) -> Any:
        """Call a Supabase RPC function."""
        if not requests:
            raise RuntimeError("Python package 'requests' is required for KB retrieval.")

        # Handle namespaced RPC names (kb.search_chunks -> rpc/kb.search_chunks)
        endpoint = f"{self.supabase_url}/rest/v1/rpc/{rpc_name}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=20)
            if resp.status_code >= 300:
                _logger.warning("Supabase RPC error %s: %s", resp.status_code, resp.text[:500])
                return []
            return resp.json()
        except Exception as e:
            _logger.warning("Supabase RPC call failed: %s", e)
            return []

    def _maybe_embed(self, text: str) -> Optional[List[float]]:
        """Compute embedding if configured, otherwise return None to use text search."""
        provider = (os.environ.get("IPAI_EMBEDDINGS_PROVIDER") or "").strip().lower()
        if provider != "openai":
            return None

        if not requests:
            raise RuntimeError("Python package 'requests' is required for embeddings.")

        base_url = (
            os.environ.get("IPAI_EMBEDDINGS_BASE_URL")
            or os.environ.get("IPAI_LLM_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        api_key = (
            os.environ.get("IPAI_EMBEDDINGS_API_KEY")
            or os.environ.get("IPAI_LLM_API_KEY")
            or ""
        ).strip()
        model = (os.environ.get("IPAI_EMBEDDINGS_MODEL") or "text-embedding-3-small").strip()

        if not api_key:
            return None

        endpoint = f"{base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {"model": model, "input": text}

        try:
            resp = requests.post(endpoint, headers=headers, data=json.dumps(body), timeout=30)
            if resp.status_code >= 300:
                _logger.warning("Embedding API error %s: %s", resp.status_code, resp.text[:300])
                return None
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            _logger.warning("Embedding call failed: %s", e)
            return None
