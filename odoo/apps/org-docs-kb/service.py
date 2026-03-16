"""
Organization-Wide Documentation RAG Service

FastAPI service for retrieval-augmented generation over internal org docs.
Uses Azure AI Search for vector retrieval and Azure OpenAI for generation.
Designed to run as an Azure Container App.

Endpoints:
  GET  /health              — Health check
  POST /search              — Full-text + semantic search across org docs
  POST /answer              — Grounded answer generation with citations
  POST /search/spec         — Search spec bundles
  POST /search/architecture — Search architecture docs
  GET  /sources             — List indexed source families
  GET  /freshness           — Report index freshness
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from fastapi import FastAPI, HTTPException
from openai import AzureOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Configuration from environment ---
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY", "")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "org-docs")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
EMBEDDING_DEPLOYMENT = os.environ.get(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"
)
CHAT_DEPLOYMENT = os.environ.get(
    "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"
)

# Document type taxonomy
DOC_TYPES = [
    "architecture",
    "contract",
    "spec",
    "runbook",
    "config",
    "reference",
    "guide",
    "policy",
]

# Source families
SOURCE_FAMILIES = [
    "repo-docs",
    "spec-bundles",
    "architecture-docs",
    "runbooks",
    "policy-docs",
]

# --- Clients (initialized at startup) ---
search_client: SearchClient | None = None
openai_client: AzureOpenAI | None = None
_startup_time: datetime | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup."""
    global search_client, openai_client, _startup_time

    _startup_time = datetime.now(timezone.utc)

    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY:
        search_client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(AZURE_SEARCH_API_KEY),
        )

    if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
        openai_client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-06-01",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

    logger.info("Org docs service started: index=%s", INDEX_NAME)
    yield
    logger.info("Org docs service shutting down")


app = FastAPI(
    title="Org Docs RAG",
    description="Organization-wide documentation search and retrieval",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Request/Response Models ---


class SearchFilters(BaseModel):
    doc_type: Optional[str] = Field(
        default=None,
        description="Filter by document type",
    )
    source: Optional[str] = Field(
        default=None,
        description="Filter by source family",
    )
    owner: Optional[str] = Field(
        default=None,
        description="Filter by document owner",
    )


class SearchRequest(BaseModel):
    query: str
    filters: SearchFilters = Field(default_factory=SearchFilters)
    limit: int = Field(default=5, le=20, ge=1)


class SearchResult(BaseModel):
    title: str
    content: str
    path: str
    score: float
    doc_type: str
    source: str
    heading_chain: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    count: int
    index: str


class AnswerFilters(BaseModel):
    doc_type: Optional[str] = None


class AnswerRequest(BaseModel):
    question: str
    filters: AnswerFilters = Field(default_factory=AnswerFilters)
    limit: int = Field(default=5, le=20, ge=1)


class CitationItem(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    path: str
    heading_chain: str
    content_excerpt: str = Field(max_length=200)
    score: float
    source: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    confidence_band: str  # high, medium, low, none
    ambiguity_flag: bool
    ambiguity_reason: Optional[str] = None


class SpecSearchRequest(BaseModel):
    query: str
    bundle: Optional[str] = None
    limit: int = Field(default=5, le=20, ge=1)


class ArchitectureSearchRequest(BaseModel):
    query: str
    limit: int = Field(default=5, le=20, ge=1)


class SourceInfo(BaseModel):
    source: str
    doc_count: int


class SourcesResponse(BaseModel):
    sources: list[SourceInfo]
    total: int


class FreshnessResponse(BaseModel):
    index: str
    last_refresh: Optional[str] = None
    doc_count: int
    stale_count: int
    status: str


# --- Helper functions ---


def _embed_query(text: str) -> list[float]:
    """Embed a query string using Azure OpenAI."""
    if openai_client is None:
        raise HTTPException(503, "OpenAI client not configured")

    response = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_DEPLOYMENT,
    )
    return response.data[0].embedding


def _compute_confidence_band(results: list[SearchResult]) -> str:
    """Compute confidence band from result scores.

    - high:   top score >= 0.85 AND at least 2 results above 0.7
    - medium: top score >= 0.7
    - low:    top score >= 0.5
    - none:   top score < 0.5 OR no results
    """
    if not results:
        return "none"

    top_score = results[0].score
    above_07 = sum(1 for r in results if r.score >= 0.7)

    if top_score >= 0.85 and above_07 >= 2:
        return "high"
    elif top_score >= 0.7:
        return "medium"
    elif top_score >= 0.5:
        return "low"
    else:
        return "none"


def _detect_ambiguity(results: list[SearchResult]) -> tuple[bool, Optional[str]]:
    """Detect ambiguity in top results.

    Ambiguity is flagged when top 2 results have contradicting content
    (different doc_type or source with similar scores).
    """
    if len(results) < 2:
        return False, None

    top = results[0]
    second = results[1]

    # Similar scores (within 10% of each other)
    if top.score > 0 and second.score / top.score >= 0.9:
        if top.doc_type != second.doc_type:
            return True, (
                "Top results have different doc types: "
                "'%s' vs '%s' with similar scores (%.2f vs %.2f)"
                % (top.doc_type, second.doc_type, top.score, second.score)
            )
        if top.source != second.source:
            return True, (
                "Top results come from different sources: "
                "'%s' vs '%s' with similar scores (%.2f vs %.2f)"
                % (top.source, second.source, top.score, second.score)
            )

    return False, None


def _build_filter_expr(
    doc_type: Optional[str] = None,
    source: Optional[str] = None,
    owner: Optional[str] = None,
) -> Optional[str]:
    """Build Azure AI Search OData filter expression."""
    parts = []
    if doc_type:
        parts.append("doc_type eq '%s'" % doc_type)
    if source:
        parts.append("source eq '%s'" % source)
    if owner:
        parts.append("owner eq '%s'" % owner)
    return " and ".join(parts) if parts else None


def _search_index(
    query: str,
    limit: int,
    filter_expr: Optional[str] = None,
) -> list[SearchResult]:
    """Execute hybrid search against Azure AI Search index."""
    if search_client is None:
        raise HTTPException(503, "Search client not configured")

    vector = _embed_query(query)

    vector_query = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=limit,
        fields="content_vector",
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=filter_expr,
        select=[
            "chunk_id",
            "doc_id",
            "title",
            "content",
            "path",
            "heading_chain",
            "doc_type",
            "source",
            "owner",
        ],
        top=limit,
    )

    items = []
    for r in results:
        items.append(
            SearchResult(
                title=r.get("title", ""),
                content=(r.get("content", "") or "")[:500],
                path=r.get("path", ""),
                score=r.get("@search.score", 0),
                doc_type=r.get("doc_type", "reference"),
                source=r.get("source", "repo-docs"),
                heading_chain=r.get("heading_chain", ""),
            )
        )

    return items


# --- Endpoints ---


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "org-docs-kb",
        "index": INDEX_NAME,
        "search_connected": search_client is not None,
        "openai_connected": openai_client is not None,
    }


@app.post("/search", response_model=SearchResponse)
async def search_org_docs(req: SearchRequest):
    """Search the org-wide documentation knowledge base."""
    filter_expr = _build_filter_expr(
        doc_type=req.filters.doc_type,
        source=req.filters.source,
        owner=req.filters.owner,
    )

    results = _search_index(req.query, req.limit, filter_expr)

    return SearchResponse(
        results=results,
        count=len(results),
        index=INDEX_NAME,
    )


@app.post("/answer", response_model=AnswerResponse)
async def answer_with_citations(req: AnswerRequest):
    """Answer a question using grounded retrieval with citations."""
    if search_client is None or openai_client is None:
        raise HTTPException(503, "Service not fully configured")

    filter_expr = _build_filter_expr(doc_type=req.filters.doc_type)
    results = _search_index(req.question, req.limit, filter_expr)

    confidence_band = _compute_confidence_band(results)
    ambiguity_flag, ambiguity_reason = _detect_ambiguity(results)

    if not results:
        return AnswerResponse(
            answer="No relevant documentation found for this question.",
            citations=[],
            confidence_band="none",
            ambiguity_flag=False,
            ambiguity_reason=None,
        )

    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(results):
        context_parts.append(
            "[Source %d: %s | %s | type=%s]\n%s"
            % (i + 1, chunk.path, chunk.heading_chain, chunk.doc_type, chunk.content)
        )
    context = "\n\n---\n\n".join(context_parts)

    # Generate answer with citations
    system_prompt = (
        "You are an internal documentation expert for InsightPulse AI. "
        "Answer questions using ONLY the provided documentation sources. "
        "Always cite your sources using [Source N] notation. "
        "If the sources don't contain the answer, say so clearly. "
        "Be concise, accurate, and actionable. "
        "When sources conflict, note the discrepancy."
    )

    response = openai_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Sources:\n\n%s\n\nQuestion: %s" % (context, req.question),
            },
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content

    citations = []
    for r in results[:5]:
        citations.append(
            CitationItem(
                chunk_id=r.path.replace("/", "_").replace(".", "_"),
                doc_id=r.path,
                title=r.title,
                path=r.path,
                heading_chain=r.heading_chain,
                content_excerpt=r.content[:200],
                score=r.score,
                source=r.source,
            )
        )

    return AnswerResponse(
        answer=answer,
        citations=citations,
        confidence_band=confidence_band,
        ambiguity_flag=ambiguity_flag,
        ambiguity_reason=ambiguity_reason,
    )


@app.post("/search/spec", response_model=SearchResponse)
async def search_spec_bundles(req: SpecSearchRequest):
    """Search spec bundles specifically."""
    parts = ["source eq 'spec-bundles'"]
    if req.bundle:
        parts.append(
            "path ge 'spec/%s' and path lt 'spec/%s~'" % (req.bundle, req.bundle)
        )
    filter_expr = " and ".join(parts)

    results = _search_index(req.query, req.limit, filter_expr)

    return SearchResponse(
        results=results,
        count=len(results),
        index=INDEX_NAME,
    )


@app.post("/search/architecture", response_model=SearchResponse)
async def search_architecture_docs(req: ArchitectureSearchRequest):
    """Search architecture documentation specifically."""
    filter_expr = "doc_type eq 'architecture'"

    results = _search_index(req.query, req.limit, filter_expr)

    return SearchResponse(
        results=results,
        count=len(results),
        index=INDEX_NAME,
    )


@app.get("/sources", response_model=SourcesResponse)
async def list_sources():
    """List indexed source families and their doc counts."""
    if search_client is None:
        raise HTTPException(503, "Search client not configured")

    sources = []
    total = 0

    for source_name in SOURCE_FAMILIES:
        try:
            filter_expr = "source eq '%s'" % source_name
            results = search_client.search(
                search_text="*",
                filter=filter_expr,
                top=0,
                include_total_count=True,
            )
            count = results.get_count() or 0
            sources.append(SourceInfo(source=source_name, doc_count=count))
            total += count
        except Exception:
            logger.warning("Failed to count docs for source: %s", source_name)
            sources.append(SourceInfo(source=source_name, doc_count=0))

    return SourcesResponse(sources=sources, total=total)


@app.get("/freshness", response_model=FreshnessResponse)
async def report_freshness():
    """Report index freshness (last refresh, doc count, stale count)."""
    if search_client is None:
        return FreshnessResponse(
            index=INDEX_NAME,
            last_refresh=None,
            doc_count=0,
            stale_count=0,
            status="disconnected",
        )

    try:
        # Get total document count
        results = search_client.search(
            search_text="*",
            top=0,
            include_total_count=True,
        )
        doc_count = results.get_count() or 0

        # Get stale documents (indexed_at older than 7 days)
        stale_filter = (
            "indexed_at lt %s"
            % (
                datetime.now(timezone.utc)
                .replace(day=datetime.now(timezone.utc).day - 7)
                .strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        )
        try:
            stale_results = search_client.search(
                search_text="*",
                filter=stale_filter,
                top=0,
                include_total_count=True,
            )
            stale_count = stale_results.get_count() or 0
        except Exception:
            # indexed_at field may not exist yet
            stale_count = 0

        # Determine status
        if doc_count == 0:
            status = "empty"
        elif stale_count > doc_count * 0.5:
            status = "stale"
        else:
            status = "fresh"

        return FreshnessResponse(
            index=INDEX_NAME,
            last_refresh=(
                _startup_time.isoformat() if _startup_time else None
            ),
            doc_count=doc_count,
            stale_count=stale_count,
            status=status,
        )
    except Exception:
        logger.exception("Failed to check index freshness")
        return FreshnessResponse(
            index=INDEX_NAME,
            last_refresh=None,
            doc_count=0,
            stale_count=0,
            status="error",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
