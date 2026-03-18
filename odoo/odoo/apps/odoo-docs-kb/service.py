"""
Odoo 19 Documentation RAG Service

FastAPI service for retrieval-augmented generation over Odoo 19 docs.
Uses Azure AI Search for vector retrieval and Azure OpenAI for generation.
Designed to run as an Azure Container App.
"""

import logging
import os
from contextlib import asynccontextmanager

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
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "odoo19-docs")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
EMBEDDING_DEPLOYMENT = os.environ.get(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"
)
CHAT_DEPLOYMENT = os.environ.get(
    "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"
)

# --- Clients (initialized at startup) ---
search_client: SearchClient | None = None
openai_client: AzureOpenAI | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup."""
    global search_client, openai_client

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

    logger.info("Service started: index=%s", INDEX_NAME)
    yield
    logger.info("Service shutting down")


app = FastAPI(
    title="Odoo 19 Docs RAG",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Request/Response Models ---


class SearchRequest(BaseModel):
    query: str
    version: str = "19.0"
    top_k: int = Field(default=8, le=20)
    path_filter: str | None = None


class ChunkResult(BaseModel):
    chunk_id: str
    content: str
    path: str
    heading_chain: str
    score: float
    citation: str


class SearchResponse(BaseModel):
    results: list[ChunkResult]
    query: str
    count: int


class AnswerRequest(BaseModel):
    query: str
    version: str = "19.0"


class Citation(BaseModel):
    chunk_id: str
    path: str
    heading_chain: str
    relevance: float


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    query: str


class ModuleSearchRequest(BaseModel):
    module_name: str
    query: str
    top_k: int = Field(default=5, le=20)


# --- Endpoints ---


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "index": INDEX_NAME,
        "search_connected": search_client is not None,
        "openai_connected": openai_client is not None,
    }


@app.post("/search", response_model=SearchResponse)
async def search_odoo_docs(req: SearchRequest):
    """Search the Odoo 19 documentation knowledge base."""
    if search_client is None:
        raise HTTPException(503, "Search client not configured")

    # Get query embedding
    vector = _embed_query(req.query)

    # Build filter
    filter_expr = f"version eq '{req.version}'"
    if req.path_filter:
        filter_expr += f" and path ge '{req.path_filter}' and path lt '{req.path_filter}~'"

    # Hybrid search: vector + text
    vector_query = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=req.top_k,
        fields="content_vector",
    )

    results = search_client.search(
        search_text=req.query,
        vector_queries=[vector_query],
        filter=filter_expr,
        select=["chunk_id", "content", "path", "heading_chain", "repo", "branch"],
        top=req.top_k,
    )

    chunks = []
    for r in results:
        citation = (
            f"repo={r.get('repo', 'odoo/documentation')} "
            f"branch={r.get('branch', '19.0')} "
            f"path={r['path']} "
            f"heading={r.get('heading_chain', '')} "
            f"chunk_id={r['chunk_id']}"
        )
        chunks.append(
            ChunkResult(
                chunk_id=r["chunk_id"],
                content=r["content"],
                path=r["path"],
                heading_chain=r.get("heading_chain", ""),
                score=r["@search.score"],
                citation=citation,
            )
        )

    return SearchResponse(results=chunks, query=req.query, count=len(chunks))


@app.post("/answer", response_model=AnswerResponse)
async def answer_with_citations(req: AnswerRequest):
    """Answer a question using grounded retrieval with citations."""
    if search_client is None or openai_client is None:
        raise HTTPException(503, "Service not fully configured")

    # Retrieve relevant chunks
    search_resp = await search_odoo_docs(
        SearchRequest(query=req.query, version=req.version, top_k=8)
    )

    if not search_resp.results:
        return AnswerResponse(
            answer="No relevant documentation found for this query.",
            citations=[],
            query=req.query,
        )

    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(search_resp.results):
        context_parts.append(
            f"[Source {i + 1}: {chunk.path} | {chunk.heading_chain}]\n{chunk.content}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Generate answer with citations
    system_prompt = (
        "You are an Odoo 19 documentation expert. Answer questions using ONLY "
        "the provided documentation sources. Always cite your sources using "
        "[Source N] notation. If the sources don't contain the answer, say so. "
        "Be concise and accurate."
    )

    response = openai_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Sources:\n\n{context}\n\nQuestion: {req.query}",
            },
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content

    citations = [
        Citation(
            chunk_id=c.chunk_id,
            path=c.path,
            heading_chain=c.heading_chain,
            relevance=c.score,
        )
        for c in search_resp.results[:5]
    ]

    return AnswerResponse(
        answer=answer,
        citations=citations,
        query=req.query,
    )


@app.post("/search/module", response_model=SearchResponse)
async def ground_to_module(req: ModuleSearchRequest):
    """Search documentation scoped to a specific Odoo module."""
    # Map module name to doc path prefix
    module_path_map = {
        "account": "content/applications/finance/accounting",
        "sale": "content/applications/sales",
        "purchase": "content/applications/inventory_and_mrp/purchase",
        "stock": "content/applications/inventory_and_mrp/inventory",
        "hr": "content/applications/hr",
        "website": "content/applications/websites/website",
        "crm": "content/applications/sales/crm",
        "project": "content/applications/services/project",
        "mrp": "content/applications/inventory_and_mrp/manufacturing",
    }

    path_filter = module_path_map.get(
        req.module_name, f"content/applications/{req.module_name}"
    )

    return await search_odoo_docs(
        SearchRequest(
            query=req.query,
            top_k=req.top_k,
            path_filter=path_filter,
        )
    )


def _embed_query(text: str) -> list[float]:
    """Embed a query string using Azure OpenAI."""
    if openai_client is None:
        raise HTTPException(503, "OpenAI client not configured")

    response = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_DEPLOYMENT,
    )
    return response.data[0].embedding


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
