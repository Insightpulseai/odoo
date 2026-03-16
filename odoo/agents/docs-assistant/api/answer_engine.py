#!/usr/bin/env python3
"""
Kapa.ai-style Answer Engine API
Self-hosted RAG system for technical documentation Q&A
"""

import os
import time
import uuid
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from anthropic import Anthropic
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Docs Assistant API",
    description="Kapa.ai-style self-hosted RAG system for technical documentation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        port=os.getenv("SUPABASE_PORT", "5432"),
        database=os.getenv("SUPABASE_DB"),
        user=os.getenv("SUPABASE_USER"),
        password=os.getenv("SUPABASE_PASSWORD"),
        cursor_factory=RealDictCursor
    )

# LLM clients
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Pydantic models
class ChatRequest(BaseModel):
    project_slug: str
    question: str
    history: Optional[List[Dict[str, str]]] = None
    source_groups: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    stream: bool = False

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    project_slug: str
    query: str
    limit: int = 10
    source_groups: Optional[List[str]] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class FeedbackRequest(BaseModel):
    answer_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    user_id: Optional[str] = None

# Authentication middleware
async def authenticate_api_key(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Authenticate API key and return project info"""
    api_key = x_api_key or (authorization.replace("Bearer ", "") if authorization else None)

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # In production, hash the key and compare
            cur.execute("""
                SELECT ak.id, ak.project_id, ak.permissions, p.slug, p.name
                FROM docs_api_keys ak
                JOIN docs_projects p ON ak.project_id = p.id
                WHERE ak.key_hash = %s AND ak.revoked_at IS NULL
            """, (api_key,))
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=401, detail="Invalid API key")

            # Update last used
            cur.execute("""
                UPDATE docs_api_keys
                SET last_used_at = NOW()
                WHERE id = %s
            """, (result['id'],))
            conn.commit()

            return dict(result)
    finally:
        conn.close()

# Utility functions
def get_embedding(text: str, model: str = "text-embedding-3-large") -> List[float]:
    """Get embedding for text using OpenAI"""
    response = openai_client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def search_similar_chunks(
    project_id: str,
    query_embedding: List[float],
    limit: int = 10,
    source_group_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Search for similar chunks using vector similarity"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Convert embedding to PostgreSQL format
            embedding_array = "[" + ",".join(map(str, query_embedding)) + "]"

            if source_group_ids:
                cur.execute("""
                    SELECT * FROM docs_search_chunks(
                        %s::vector, %s, %s::uuid, %s::uuid[]
                    )
                """, (embedding_array, limit, project_id, source_group_ids))
            else:
                cur.execute("""
                    SELECT * FROM docs_search_chunks(
                        %s::vector, %s, %s::uuid, NULL
                    )
                """, (embedding_array, limit, project_id))

            return cur.fetchall()
    finally:
        conn.close()

def generate_answer_with_citations(
    question: str,
    context_chunks: List[Dict[str, Any]],
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Generate answer using LLM with citations"""

    # Build context from chunks
    context_parts = []
    for chunk in context_chunks:
        context_parts.append(f"Source: {chunk['document_title']} - {chunk['heading']}")
        context_parts.append(f"Content: {chunk['content']}")
        context_parts.append("---")

    context = "\n".join(context_parts)

    # Build conversation history
    messages = []
    if history:
        for msg in history[-6:]:  # Keep last 6 messages for context
            messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})

    # Add current question with context
    system_prompt = f"""You are a technical documentation assistant. Answer questions based ONLY on the provided context.

CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the question using ONLY information from the provided context
2. If the context doesn't contain relevant information, say "I don't have enough information to answer this question based on the available documentation"
3. Be precise and cite specific sources using [Source: Document Title] format
4. Keep answers concise and technical
5. Do not make up information or use external knowledge

QUESTION: {question}"""

    messages.append({"role": "user", "content": system_prompt})

    try:
        # Use Claude for better reasoning (can switch to OpenAI if preferred)
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=messages,
            temperature=0.1
        )

        answer = response.content[0].text

        # Extract citations from answer
        citations = []
        for chunk in context_chunks:
            if chunk['document_title'] in answer:
                citations.append({
                    "chunk_id": str(chunk['chunk_id']),
                    "document_title": chunk['document_title'],
                    "heading": chunk['heading'],
                    "content_snippet": chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                    "similarity_score": chunk['similarity_score']
                })

        return {
            "answer": answer,
            "citations": citations,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    except Exception as e:
        logger.error(f"LLM generation error: {e}")
        return {
            "answer": "I encountered an error while generating the answer. Please try again.",
            "citations": [],
            "token_usage": {"input_tokens": 0, "output_tokens": 0}
        }

# API endpoints
@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    auth_info: Dict[str, Any] = Depends(authenticate_api_key)
):
    """Main chat endpoint for Q&A"""
    start_time = time.time()

    # Check permissions
    if not auth_info['permissions'].get('chat', True):
        raise HTTPException(status_code=403, detail="Chat permission denied")

    # Get project info
    project_id = auth_info['project_id']

    # Generate query embedding
    try:
        query_embedding = get_embedding(request.question)
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process question")

    # Search for relevant chunks
    source_group_ids = None
    if request.source_groups:
        # Convert source group names to IDs (implementation needed)
        pass

    chunks = search_similar_chunks(
        project_id=str(project_id),
        query_embedding=query_embedding,
        limit=10,
        source_group_ids=source_group_ids
    )

    if not chunks:
        return ChatResponse(
            answer="I couldn't find relevant information in the documentation to answer your question.",
            citations=[],
            metadata={"grounded": False, "chunks_retrieved": 0}
        )

    # Generate answer
    generation_result = generate_answer_with_citations(
        question=request.question,
        context_chunks=chunks,
        history=request.history
    )

    latency_ms = int((time.time() - start_time) * 1000)

    # Log question and answer
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Log question
            cur.execute("""
                INSERT INTO docs_questions
                (project_id, api_key_id, query, channel, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (project_id, auth_info['id'], request.question, 'api', json.dumps({"stream": request.stream})))
            question_id = cur.fetchone()['id']

            # Log answer
            cur.execute("""
                INSERT INTO docs_answers
                (question_id, project_id, model, answer, latency_ms, token_in, token_out, grounded, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                question_id, project_id, "claude-3-sonnet",
                generation_result["answer"], latency_ms,
                generation_result["token_usage"]["input_tokens"],
                generation_result["token_usage"]["output_tokens"],
                len(generation_result["citations"]) > 0,
                0.8  # Placeholder confidence score
            ))
            answer_id = cur.fetchone()['id']

            # Log citations
            for citation in generation_result["citations"]:
                cur.execute("""
                    INSERT INTO docs_answer_citations
                    (answer_id, chunk_id, relevance_score, citation_text)
                    VALUES (%s, %s, %s, %s)
                """, (answer_id, citation["chunk_id"], citation["similarity_score"], citation["content_snippet"]))

            conn.commit()

            # Return response with answer ID for feedback
            return ChatResponse(
                answer=generation_result["answer"],
                citations=generation_result["citations"],
                metadata={
                    "answer_id": str(answer_id),
                    "grounded": len(generation_result["citations"]) > 0,
                    "chunks_retrieved": len(chunks),
                    "latency_ms": latency_ms,
                    "token_usage": generation_result["token_usage"]
                }
            )
    finally:
        conn.close()

@app.post("/v1/search", response_model=SearchResponse)
async def search_endpoint(
    request: SearchRequest,
    auth_info: Dict[str, Any] = Depends(authenticate_api_key)
):
    """Semantic search endpoint (no LLM generation)"""
    # Check permissions
    if not auth_info['permissions'].get('search', True):
        raise HTTPException(status_code=403, detail="Search permission denied")

    project_id = auth_info['project_id']

    # Generate query embedding
    try:
        query_embedding = get_embedding(request.query)
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

    # Search for relevant chunks
    source_group_ids = None
    if request.source_groups:
        # Convert source group names to IDs
        pass

    chunks = search_similar_chunks(
        project_id=str(project_id),
        query_embedding=query_embedding,
        limit=request.limit,
        source_group_ids=source_group_ids
    )

    return SearchResponse(
        results=chunks,
        metadata={
            "total_results": len(chunks),
            "query": request.query
        }
    )

@app.post("/v1/feedback")
async def feedback_endpoint(
    request: FeedbackRequest,
    auth_info: Dict[str, Any] = Depends(authenticate_api_key)
):
    """Submit feedback for an answer"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO docs_feedback
                (answer_id, rating, comment, user_id)
                VALUES (%s, %s, %s, %s)
            """, (request.answer_id, request.rating, request.comment, request.user_id))
            conn.commit()

        return {"status": "success", "message": "Feedback submitted"}
    finally:
        conn.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected"}, 503

# Streaming chat endpoint (for real-time responses)
@app.post("/v1/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    auth_info: Dict[str, Any] = Depends(authenticate_api_key)
):
    """Streaming chat endpoint for real-time responses"""
    # Implementation for streaming would go here
    # This would use OpenAI/Claude streaming APIs
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
