"""
PrismaLab Gateway — FastAPI service that fronts Foundry (ipai-copilot) for the
four PrismaLab free tools (PICO, PubMed, PRISMA, Review Type) and the RAG
assistant. Keyless auth via managed identity + AIProjectClient (SDK 2.x).

Endpoints:
  POST /api/prismalab/completions  — structured JSON for PICO/PubMed/Review tools
  POST /api/prismalab/rag          — grounded Q&A with AI Search (srch-ipai-dev)
  GET  /health                     — liveness

Rules:
  - No API keys in code — ManagedIdentityCredential → ChainedTokenCredential
  - All egress tagged with App Insights custom dimensions
  - Redis token-bucket rate limiter (per-IP + global)
  - SSOT model: claude-sonnet-4-6 (Foundry deployment name)
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from azure.identity.aio import (
    ChainedTokenCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
FOUNDRY_ENDPOINT = os.environ.get(
    "FOUNDRY_ENDPOINT",
    "https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot",
)
FOUNDRY_AOAI_ENDPOINT = os.environ.get(
    "FOUNDRY_AOAI_ENDPOINT",
    "https://ipai-copilot-resource.openai.azure.com",
)
FOUNDRY_MODEL = os.environ.get("FOUNDRY_MODEL", "claude-sonnet-4-6")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
RAG_AGENT_ID = os.environ.get("RAG_AGENT_ID", "")  # (deprecated: in-gateway RAG)
SEARCH_ENDPOINT = os.environ.get(
    "SEARCH_ENDPOINT", "https://srch-ipai-dev.search.windows.net"
)
SEARCH_INDEX = os.environ.get("SEARCH_INDEX", "prismalab-rag-v1")
REDIS_URL = os.environ.get(
    "REDIS_URL", "redis://cache-ipai-dev.redis.cache.windows.net:6380"
)
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "https://www.insightpulseai.com,https://insightpulseai.com,http://localhost:3000,http://localhost:5173",
    ).split(",")
    if o.strip()
]
RATE_LIMIT_PER_IP_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_IP_PER_MIN", "12"))
RATE_LIMIT_GLOBAL_PER_MIN = int(os.environ.get("RATE_LIMIT_GLOBAL_PER_MIN", "600"))

# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------
_provider = TracerProvider()
_otlp = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
if _otlp:
    _provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=_otlp)))
trace.set_tracer_provider(_provider)
tracer = trace.get_tracer("ipai.prismalab-gateway")

# ---------------------------------------------------------------------------
# Credential + lazy clients (fail closed on missing auth, not import)
# ---------------------------------------------------------------------------
_credential: Optional[ChainedTokenCredential] = None


def _get_credential() -> ChainedTokenCredential:
    global _credential
    if _credential is None:
        _credential = ChainedTokenCredential(
            ManagedIdentityCredential(client_id=os.environ.get("AZURE_CLIENT_ID", "")),
            DefaultAzureCredential(exclude_interactive_browser_credential=True),
        )
    return _credential


_redis: Optional[aioredis.Redis] = None


async def _get_redis() -> Optional[aioredis.Redis]:
    """Redis is optional — if unreachable, rate limiting is disabled (fail-open, logged)."""
    global _redis
    if _redis is not None:
        return _redis
    try:
        _redis = aioredis.from_url(
            REDIS_URL,
            password=os.environ.get("REDIS_KEY", ""),
            ssl=True,
            decode_responses=True,
            socket_timeout=2,
        )
        await _redis.ping()
    except Exception as e:
        print(f"[WARN] Redis unavailable — rate limiting disabled: {e}")
        _redis = None
    return _redis


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="PrismaLab Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Prismalab-Tool"],
)


# ---------------------------------------------------------------------------
# System prompts — identical to the React file so behavior is consistent
# ---------------------------------------------------------------------------
SYSTEM_PROMPTS: Dict[str, str] = {
    "pico": (
        "You are a Cochrane-trained systematic review methodologist. Structure "
        "the given text as a PICO framework. Return ONLY valid JSON — no prose, "
        "no markdown fences: "
        '{"P":"Population description","I":"Intervention or exposure",'
        '"C":"Comparator or control","O":"Primary outcome(s)",'
        '"question":"Full structured clinical question (1–2 sentences)",'
        '"mesh_terms":["term1","term2","term3","term4"],'
        '"note":"One practical tip for refining this question"}'
    ),
    "pubmed": (
        "You are a medical librarian specialising in systematic review search "
        "strategies (PRESS guidelines, Cochrane). Build a PubMed Boolean search "
        "string. Return ONLY valid JSON — no prose, no markdown fences: "
        '{"search_string":"full PubMed Boolean query",'
        '"strategy":"2–3 sentence explanation",'
        '"key_terms":[{"concept":"Label","terms":["term1","term2"]}],'
        '"filters":["filter suggestion 1","filter suggestion 2"],'
        '"tip":"One practical improvement tip"}'
    ),
    "review": (
        "You are a systematic review methodology expert (Cochrane, Campbell, "
        "JBI). Recommend the most appropriate evidence synthesis approach. "
        "Return ONLY valid JSON — no prose, no markdown fences: "
        '{"recommended":"Review type name",'
        '"rationale":"Why this type fits (2–3 sentences)",'
        '"time_estimate":"Typical time to complete",'
        '"team_size":"Recommended team size",'
        '"alternatives":[{"type":"Type","when":"Consider when…"}],'
        '"next_steps":["step 1","step 2","step 3","step 4"],'
        '"reporting_guideline":"Key reporting standard to follow"}'
    ),
}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class CompletionReq(BaseModel):
    tool: str = Field(..., pattern="^(pico|pubmed|review)$")
    user: str = Field(..., min_length=1, max_length=2000)


class RagReq(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)
    thread_id: Optional[str] = None  # for multi-turn continuation


class RagCitation(BaseModel):
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None


class RagResp(BaseModel):
    answer: str
    citations: List[RagCitation] = []
    thread_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Rate limiting (fail-open if Redis absent)
# ---------------------------------------------------------------------------
async def _enforce_rate_limit(request: Request, bucket: str) -> None:
    r = await _get_redis()
    if r is None:
        return  # fail-open

    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host
        if request.client
        else "unknown"
    )
    now_min = int(time.time() // 60)
    ip_key = f"rl:{bucket}:ip:{client_ip}:{now_min}"
    global_key = f"rl:{bucket}:global:{now_min}"

    try:
        ip_count = await r.incr(ip_key)
        if ip_count == 1:
            await r.expire(ip_key, 65)
        if ip_count > RATE_LIMIT_PER_IP_PER_MIN:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded ({RATE_LIMIT_PER_IP_PER_MIN}/min per IP). Try again shortly.",
            )
        g_count = await r.incr(global_key)
        if g_count == 1:
            await r.expire(global_key, 65)
        if g_count > RATE_LIMIT_GLOBAL_PER_MIN:
            raise HTTPException(
                status_code=503,
                detail="Free-tool capacity reached. Try again shortly.",
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[WARN] rate limit backing off (Redis error): {e}")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "prismalab-gateway",
        "foundry_endpoint": FOUNDRY_ENDPOINT,
        "foundry_aoai_endpoint": FOUNDRY_AOAI_ENDPOINT,
        "foundry_model": FOUNDRY_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "search_index": SEARCH_INDEX,
        "rag_mode": "in-gateway-hybrid",
    }


def _safe_json(text: str) -> Optional[dict]:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


async def _aoai_chat(system: str, user: str, max_tokens: int = 1200) -> str:
    """Call the Foundry-hosted Claude deployment via the AOAI-compatible endpoint,
    using Entra ID (keyless). Returns the assistant text."""
    from openai import AsyncAzureOpenAI  # type: ignore
    from azure.identity.aio import get_bearer_token_provider  # type: ignore

    token_provider = get_bearer_token_provider(
        _get_credential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AsyncAzureOpenAI(
        azure_endpoint=FOUNDRY_AOAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )
    try:
        resp = await client.chat.completions.create(
            model=FOUNDRY_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
    finally:
        await client.close()


async def _aoai_embed(text: str) -> List[float]:
    from openai import AsyncAzureOpenAI  # type: ignore
    from azure.identity.aio import get_bearer_token_provider  # type: ignore

    token_provider = get_bearer_token_provider(
        _get_credential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AsyncAzureOpenAI(
        azure_endpoint=FOUNDRY_AOAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )
    try:
        resp = await client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        return resp.data[0].embedding
    finally:
        await client.close()


async def _search_rag(query: str, top_k: int) -> List[Dict[str, Any]]:
    """Hybrid search (vector + keyword) against prismalab-rag-v1."""
    from azure.search.documents.aio import SearchClient  # type: ignore
    from azure.search.documents.models import VectorizedQuery  # type: ignore

    embedding = await _aoai_embed(query)
    client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=_get_credential(),
    )
    try:
        vector_q = VectorizedQuery(
            vector=embedding, k_nearest_neighbors=top_k, fields="contentVector"
        )
        results = await client.search(
            search_text=query,
            vector_queries=[vector_q],
            top=top_k,
            select=["id", "title", "content", "source", "url", "citation"],
        )
        hits = []
        async for r in results:
            hits.append(
                {
                    "id": r["id"],
                    "title": r["title"],
                    "content": r["content"],
                    "source": r["source"],
                    "url": r.get("url", ""),
                    "citation": r.get("citation", ""),
                    "score": r.get("@search.score", 0.0),
                }
            )
        return hits
    finally:
        await client.close()


@app.post("/api/prismalab/completions")
async def completions(req: CompletionReq, request: Request) -> Dict[str, Any]:
    """Structured JSON completion for PICO / PubMed / Review tools."""
    await _enforce_rate_limit(request, f"comp:{req.tool}")
    with tracer.start_as_current_span("prismalab.completion") as span:
        span.set_attribute("prismalab.tool", req.tool)
        span.set_attribute("prismalab.user_len", len(req.user))
        text = await _aoai_chat(SYSTEM_PROMPTS[req.tool], req.user)

    parsed = _safe_json(text)
    if parsed is None:
        raise HTTPException(
            status_code=502, detail="Model returned non-JSON content."
        )
    return parsed


RAG_SYSTEM = """
You are PrismaLab AI, an assistant grounded in evidence-synthesis methodology.
Answer ONLY using the provided <context> blocks. If the context is insufficient,
say so explicitly. Always cite the source in square brackets at the end of each
claim, using the format [source: <source_id>].

Rules:
  1. Be concise — 2–4 short paragraphs or a bulleted list.
  2. When I² > 75%, recommend subgroup / meta-regression / narrative synthesis
     before pooled estimates.
  3. For PRISMA diagrams, default to two-arm layout unless explicitly asked
     about updates (Previous) or other methods.
  4. Clinical recommendations: refuse — explain methodology instead.
  5. You are a free tool — do NOT promise paid services, do NOT request PII.
""".strip()


@app.post("/api/prismalab/rag", response_model=RagResp)
async def rag(req: RagReq, request: Request) -> RagResp:
    """In-gateway RAG: hybrid search against prismalab-rag-v1 → grounded Claude answer."""
    await _enforce_rate_limit(request, "rag")

    with tracer.start_as_current_span("prismalab.rag") as span:
        span.set_attribute("prismalab.rag.question_len", len(req.question))
        span.set_attribute("prismalab.rag.top_k", req.top_k)

        hits = await _search_rag(req.question, req.top_k)
        if not hits:
            return RagResp(
                answer=(
                    "I don't have enough context in my indexed sources to answer this. "
                    "Try rephrasing, or use the specific PrismaLab tools (PICO, PubMed, "
                    "PRISMA diagram, Review type)."
                ),
                citations=[],
            )

        context_blocks = []
        for h in hits:
            context_blocks.append(
                f"<source id=\"{h['source']}\" title=\"{h['title']}\">\n"
                f"{h['content']}\n"
                f"</source>"
            )
        context_str = "\n\n".join(context_blocks)
        user_prompt = (
            f"<context>\n{context_str}\n</context>\n\n"
            f"Question: {req.question}"
        )

        answer = await _aoai_chat(RAG_SYSTEM, user_prompt, max_tokens=900)

        citations = [
            RagCitation(
                title=h["title"],
                url=h["url"] or None,
                snippet=(h["citation"] or h["content"][:160]),
            )
            for h in hits
        ]

    return RagResp(answer=answer, citations=citations, thread_id=None)


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------
@app.on_event("shutdown")
async def _shutdown() -> None:
    global _redis, _credential
    if _redis is not None:
        try:
            await _redis.close()
        except Exception:
            pass
    if _credential is not None:
        try:
            await _credential.close()
        except Exception:
            pass
